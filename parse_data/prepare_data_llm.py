import os
from pathlib import Path

import pandas as pd
import pdfplumber

from src.gigachat import gigachat

llm = gigachat


def dataframe_to_markdown(df):
    """Convert pandas DataFrame to nicely formatted Markdown table using GigaChat"""
    try:
        prompt = f"""Convert this DataFrame to a well-formatted Markdown table:
        
        {df.head(3).to_markdown()}  # Sample of the data
        
        Rules:
        1. Maintain all original data
        2. Ensure proper column alignment
        3. Add ### headers for major sections if needed
        4. Make it readable in GitHub-flavored Markdown
        """

        response = llm.invoke(prompt)
        return response.choices[0].message.content  # type: ignore
    except Exception as e:
        print(f"GigaChat error: {e}")
        # Fallback to basic Markdown
        return df.to_markdown()


def extract_table_from_pdf(pdf_path):
    """Extracts all tables from a multi-page PDF"""
    all_tables = []

    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            tables = page.extract_tables()

            if tables:
                for table in tables:
                    if not table or len(table) < 1:
                        continue

                    columns = [
                        f"{col}_{i}" if table[0].count(col) > 1 else col
                        for i, col in enumerate(table[0])
                    ]
                    df = pd.DataFrame(table[1:], columns=columns)
                    all_tables.append(df)

    if all_tables:
        try:
            return pd.concat(all_tables, ignore_index=True)
        except Exception as e:
            print(f"Concatenation error: {e}")
            return all_tables[0]
    return None


def process_all_pdfs(input_dir="resources/", output_dir="resources/markdowns/"):
    """Processes PDFs and saves as Markdown files"""
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    for pdf_file in Path(input_dir).glob("*.pdf"):
        print(f"Processing: {pdf_file.name}")

        try:
            df = extract_table_from_pdf(pdf_file)
            if df is not None:
                markdown_content = dataframe_to_markdown(df)
                md_path = Path(output_dir) / f"{pdf_file.stem}.md"

                with open(md_path, "w", encoding="utf-8") as f:
                    f.write(f"# Extracted from {pdf_file.name}\n\n")
                    f.write(markdown_content)
                print(f"Saved: {md_path}")
        except Exception as e:
            print(f"Failed to process {pdf_file.name}: {str(e)}")


if __name__ == "__main__":
    process_all_pdfs()

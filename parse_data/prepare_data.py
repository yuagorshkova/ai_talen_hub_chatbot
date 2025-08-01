import os
from pathlib import Path

import pandas as pd
import pdfplumber


def extract_table_from_pdf(pdf_path):
    """Extracts all tables from a multi-page PDF with duplicate column handling"""
    all_tables = []

    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            tables = page.extract_tables()

            if tables:
                for table in tables:
                    # Handle empty tables
                    if not table or len(table) < 1:
                        continue

                    # Create DataFrame with unique column names
                    columns = table[0]
                    data = table[1:]

                    # Make column names unique by adding suffix if needed
                    columns = [
                        f"{col}_{i}" if columns.count(col) > 1 else col
                        for i, col in enumerate(columns)
                    ]

                    df = pd.DataFrame(data, columns=columns)
                    all_tables.append(df)

    if all_tables:
        try:
            return pd.concat(all_tables, ignore_index=True)
        except Exception as e:
            print(f"Concatenation error: {e}")
            # Fallback: return first table if concatenation fails
            return all_tables[0]
    return None


def process_all_pdfs(input_dir="resources/", output_dir="resources/"):
    """Processes PDFs with error handling"""
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    for pdf_file in Path(input_dir).glob("*.pdf"):
        print(f"Processing: {pdf_file.name}")

        try:
            df = extract_table_from_pdf(pdf_file)
            if df is not None:
                csv_path = Path(output_dir) / f"{pdf_file.stem}.csv"
                df.to_csv(csv_path, index=False)
                print(f"Saved: {csv_path}")
        except Exception as e:
            print(f"Failed to process {pdf_file.name}: {str(e)}")


if __name__ == "__main__":
    process_all_pdfs()

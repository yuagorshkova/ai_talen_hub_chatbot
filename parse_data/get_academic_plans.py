import os
import re

import requests


def get_page_html(url):
    """Fetch the HTML content of a webpage."""
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching page: {e}")
        return None


def find_pdf_url(html):
    """Find the PDF URL in the HTML using the specified pattern."""
    # Search for the pattern ,"academic_plan":"https://api
    print("academic_plan" in html)
    pattern = r'"academic_plan":"(.+?)"'
    match = re.search(pattern, html)
    if match:
        return match.group(1)
    return None


def download_pdf(url, save_path):
    """Download a PDF file from a URL and save it locally."""
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()

        with open(save_path, "wb") as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)
        print(f"PDF successfully downloaded to {save_path}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error downloading PDF: {e}")
        return False


def main():
    # Input the webpage URL
    # page_url = "https://abit.itmo.ru/program/master/ai"
    page_url = "https://abit.itmo.ru/program/master/ai_product"

    # Get the HTML content
    html = get_page_html(page_url)
    if not html:
        return

    # Find the PDF URL
    pdf_url = find_pdf_url(html)
    if not pdf_url:
        print("No PDF URL found matching the pattern")
        return

    print(f"Found PDF URL: {pdf_url}")

    # Extract filename from URL or create one
    filename = os.path.basename(pdf_url.split("?")[0])  # Remove query parameters
    if not filename.endswith(".pdf"):
        programme = page_url.rsplit("/", 1)[-1]
        filename = f"resources/academic_plan_{programme}.pdf"

    # Download the PDF
    download_pdf(pdf_url, filename)


if __name__ == "__main__":
    main()

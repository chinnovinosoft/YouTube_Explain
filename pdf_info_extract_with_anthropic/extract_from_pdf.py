# pip install anthropic pandas

import anthropic
import re
import json
import pandas as pd
import sys
import os

ANTHROPIC_API_KEY = ""

COLUMNS = [
    "total_revenue",
    "net_profit",
    "operating_margin",
    "revenue_growth",
    "net_profit_growth",
    "cash_equivalents",
    "current_ratio",
    "working_capital",
    "total_assets",
    "equity_to_assets_ratio",
    "debt_to_equity_ratio",
    "total_expenses",
    "employee_expense_ratio",
    "other_expenses",
    "earnings_per_share"
]

def extract_json_from_text(text):
    """
    Extracts JSON array from a string, removing ``` and 'json' tags if present.
    """
    cleaned = re.sub(r"```json|```|json", "", text, flags=re.IGNORECASE).strip()
    match = re.search(r"\[.*\]", cleaned, re.DOTALL)
    if match:
        json_str = match.group(0)
    else:
        json_str = cleaned
    return json.loads(json_str)

def normalize_json_keys(json_data):
    """
    Converts all JSON keys to lowercase.
    """
    return [{k.lower(): v for k, v in row.items()} for row in json_data]

def main():
    if len(sys.argv) < 2:
        print("Usage: python extract_from_pdf.py /path/to/your.pdf")
        sys.exit(1)
    pdf_path = sys.argv[1]
    if not os.path.isfile(pdf_path):
        print(f"File not found: {pdf_path}")
        sys.exit(1)

    print("Uploading PDF and extracting data using Anthropic Claude...")
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    with open(pdf_path, "rb") as f:
        file_upload = client.beta.files.upload(file=(os.path.basename(pdf_path), f, "application/pdf"))

    prompt = (
        "Extract the following financial information from the PDF:\n\n"
        + ",".join(COLUMNS) +
        "\nPlease return the results as a JSON array. Do not return any extra information other than JSON with the attributes mentioned above."
    )

    response = client.beta.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "document", "source": {"type": "file", "file_id": file_upload.id}}
                ]
            }
        ],
        betas=["files-api-2025-04-14"],
    )

    print("Parsing and normalizing extracted JSON...")
    extracted_data = extract_json_from_text(response.content[0].text)
    extracted_data = normalize_json_keys(extracted_data)

    print("\nExtracted JSON:")
    print(json.dumps(extracted_data, indent=2))

    print("\nAs pandas DataFrame:")
    df = pd.DataFrame(extracted_data)
    print(df)

if __name__ == "__main__":
    main()
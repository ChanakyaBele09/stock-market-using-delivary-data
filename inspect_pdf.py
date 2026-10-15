import pdfplumber

PDF_PATH = r"d:\Trading Workflows\data\nse-indices_industry-classification-structure-2023-07.pdf"

with pdfplumber.open(PDF_PATH) as pdf:
    print(f"Total pages: {len(pdf.pages)}")
    # Inspect first 3 pages to understand structure
    for i, page in enumerate(pdf.pages[:3]):
        print(f"\n--- Page {i+1} ---")
        tables = page.extract_tables()
        print(f"  Tables found: {len(tables)}")
        for j, table in enumerate(tables):
            print(f"  Table {j+1} rows: {len(table)}")
            for row in table[:5]:
                print("   ", row)
        # Also try raw text
        if not tables:
            text = page.extract_text()
            print("  RAW TEXT (first 500 chars):")
            print(text[:500] if text else "(empty)")

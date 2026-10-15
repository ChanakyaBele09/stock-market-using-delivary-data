"""
Extract NSE industry classification from PDF + map to symbols via NSE equity master.

Strategy:
1. Parse PDF to build Basic_Ind_Code -> Industry name lookup
2. Download NSE equity master (EQUITY_L.csv) which has Symbol + Industry Code
3. Join them to produce Symbol -> Industry mapping
4. Save as nse_sector_mapping.csv in data/
"""
import pdfplumber
import pandas as pd
import requests
import io

DATA_DIR = r"d:\Trading Workflows\data"
PDF_PATH = rf"{DATA_DIR}\nse-indices_industry-classification-structure-2023-07.pdf"
OUTPUT_PATH = rf"{DATA_DIR}\nse_sector_mapping.csv"

# ── Step 1: Parse PDF ──────────────────────────────────────────────────────────
print("Parsing PDF...")
rows = []
with pdfplumber.open(PDF_PATH) as pdf:
    for page in pdf.pages[1:]:   # skip cover page
        tables = page.extract_tables()
        for table in tables:
            for row in table:
                rows.append(row)

# Build a DataFrame from raw rows
# Columns: MES_Code, MacroSector, Sect_Code, Sector, Ind_Code, Industry, Basic_Ind_Code, Basic Industry, Definition
df_pdf = pd.DataFrame(rows, columns=[
    'MES_Code', 'MacroSector', 'Sect_Code', 'Sector',
    'Ind_Code', 'Industry', 'Basic_Ind_Code', 'BasicIndustry', 'Definition'
] if len(rows[0]) == 9 else None)

# Forward-fill the hierarchy columns (they're blank when same parent row)
for col in ['MES_Code', 'MacroSector', 'Sect_Code', 'Sector', 'Ind_Code', 'Industry']:
    df_pdf[col] = df_pdf[col].replace('', pd.NA).ffill()

# Drop header rows
df_pdf = df_pdf[df_pdf['MES_Code'] != 'MES_Code'].copy()
df_pdf = df_pdf[df_pdf['Basic_Ind_Code'].notna() & (df_pdf['Basic_Ind_Code'] != '')].copy()

# Clean up newlines in text
for col in df_pdf.columns:
    df_pdf[col] = df_pdf[col].astype(str).str.replace('\n', ' ', regex=False).str.strip()

print(f"PDF parsed: {len(df_pdf)} industry classification rows")
print(df_pdf[['Sector','Industry','BasicIndustry']].head(10))

# ── Step 2: Download NSE Equity Master ────────────────────────────────────────
print("\nDownloading NSE Equity Master (EQUITY_L.csv)...")
headers = {'User-Agent': 'Mozilla/5.0'}
try:
    r = requests.get('https://archives.nseindia.com/content/equities/EQUITY_L.csv',
                     headers=headers, timeout=15)
    r.raise_for_status()
    equity_df = pd.read_csv(io.StringIO(r.text))
    print(f"Equity master rows: {len(equity_df)}")
    print("Equity master columns:", equity_df.columns.tolist())
    print(equity_df.head(3))
except Exception as e:
    print(f"Failed to download equity master: {e}")
    equity_df = None

# ── Step 3: Build Symbol -> Sector mapping ─────────────────────────────────────
if equity_df is not None:
    # Identify the industry/sector column in equity master
    print("\nColumn dtypes sample:")
    for c in equity_df.columns:
        print(f"  {c}: {equity_df[c].dropna().iloc[0] if not equity_df[c].dropna().empty else 'N/A'}")

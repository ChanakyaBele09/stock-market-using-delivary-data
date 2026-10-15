"""
Build NSE Symbol->Industry mapping using:
1. NSE F&O API (has meta.industry) - 207 stocks
2. NSE index CSV files (Symbol + Industry) - ~750 stocks
3. Per-symbol NSE quote API for remaining unknowns (batched, with delays)
"""
import requests, io, pandas as pd, time

DATA_DIR = r"d:\Trading Workflows\data"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Referer': 'https://www.nseindia.com/',
}

# ── Session ──
session = requests.Session()
print("Initializing NSE session...")
session.get('https://www.nseindia.com', headers=headers, timeout=15)
time.sleep(2)

collected = []

# ── Source 1: CSV index files ──
print("\nSource 1: NSE index CSV files...")
csv_urls = [
    'https://archives.nseindia.com/content/indices/ind_niftytotalmarket_list.csv',
    'https://archives.nseindia.com/content/indices/ind_niftymicrocap250_list.csv',
    'https://archives.nseindia.com/content/indices/ind_niftysmallcap250list.csv',
    'https://archives.nseindia.com/content/indices/ind_nifty500list.csv',
    'https://archives.nseindia.com/content/indices/ind_niftymidcap150list.csv',
]
for url in csv_urls:
    try:
        r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        if r.status_code == 200:
            df = pd.read_csv(io.StringIO(r.text))
            if 'Symbol' in df.columns and 'Industry' in df.columns:
                collected.append(df[['Symbol', 'Industry']])
                print(f"  CSV: {len(df)} rows from {url.split('/')[-1]}")
    except Exception as e:
        print(f"  CSV error: {e}")

# ── Source 2: F&O API (most reliable NSE API source) ──
print("\nSource 2: NSE F&O API (meta.industry)...")
time.sleep(1)
try:
    r = session.get(
        'https://www.nseindia.com/api/equity-stockIndices?index=SECURITIES%20IN%20F%26O',
        headers=headers, timeout=15
    )
    if r.status_code == 200:
        data = r.json()
        df_fo = pd.DataFrame(data['data'])
        meta_fo = pd.json_normalize(df_fo['meta'])
        if 'industry' in meta_fo.columns:
            chunk = pd.DataFrame({'Symbol': df_fo['symbol'], 'Industry': meta_fo['industry']})
            chunk = chunk[chunk['Industry'].notna() & (chunk['Industry'] != '')]
            collected.append(chunk)
            print(f"  F&O API: {len(chunk)} symbols with industry")
except Exception as e:
    print(f"  F&O API error: {e}")

# ── Combine ──
combined = pd.concat(collected, ignore_index=True)

# Prefer API industry (more granular) over CSV, so put F&O at top
# By keeping 'last' in reverse order - actually let's keep first (CSVs are good)
combined = combined.drop_duplicates(subset=['Symbol'], keep='first')
print(f"\nCombined unique symbols: {len(combined)}")

# ── Source 3: Per-symbol quote for remaining NSE stocks ──
# Load today's processed data to see who is missing
try:
    existing = pd.read_csv(rf"{DATA_DIR}\processed_data_2026-02-19.csv")
    all_symbols = existing[existing['SECTOR'] == 'Unknown']['SYMBOL'].unique()
    already_mapped = set(combined['Symbol'].str.upper())
    missing = [s for s in all_symbols if s.upper() not in already_mapped]
    print(f"\nStill unknown after CSV+F&O: {len(missing)} symbols")
    print(f"Fetching per-symbol quotes for up to 200 of them...")

    new_rows = []
    for sym in missing[:200]:  # limit to avoid rate limiting
        try:
            r = session.get(
                f'https://www.nseindia.com/api/quote-equity?symbol={sym}',
                headers=headers, timeout=8
            )
            if r.status_code == 200:
                d = r.json()
                info = d.get('info', {})
                industry = info.get('industry', '')
                if industry:
                    new_rows.append({'Symbol': sym, 'Industry': industry})
            time.sleep(0.3)
        except:
            pass

    if new_rows:
        extra = pd.DataFrame(new_rows)
        combined = pd.concat([combined, extra], ignore_index=True).drop_duplicates(subset=['Symbol'], keep='first')
        print(f"Added {len(new_rows)} more via per-symbol quote API")
        print(f"Final unique symbols: {len(combined)}")
except Exception as e:
    print(f"Per-symbol step error: {e}")

# ── Save ──
combined.to_csv(rf"{DATA_DIR}\nse_index_combined.csv", index=False)
print(f"\nSaved {len(combined)} symbols to nse_index_combined.csv")
print("\nTop industries:")
print(combined['Industry'].value_counts().head(15).to_string())

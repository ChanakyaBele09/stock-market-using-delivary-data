"""
Test the actual BSE Bhavcopy URLs found from the BhavCopy.aspx page.
URLs found:
- CSV: BhavCopy_BSE_CM_0_0_0_20260220_F_0000.CSV
- ZIP: BSE_EQ_BHAVCOPY_20022026_T0.ZIP
"""
import requests, time, io, zipfile, pandas as pd

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
    'Accept': '*/*',
    'Referer': 'https://www.bseindia.com/markets/MarketInfo/BhavCopy.aspx',
}

session = requests.Session()
session.get('https://www.bseindia.com', headers=headers, timeout=15)
time.sleep(1)
# Also visit the BhavCopy page to get proper cookies/referer state
session.get('https://www.bseindia.com/markets/MarketInfo/BhavCopy.aspx', headers=headers, timeout=10)
time.sleep(1)

# The page shows Feb 20, 2026 data. Try for Feb 19 and Feb 20.
test_dates = [
    ('20260219', '19022026', '190226'),  # Feb 19
    ('20260220', '20022026', '200226'),  # Feb 20
    ('20260218', '18022026', '180226'),  # Feb 18
]

for ymd, ddmmyyyy, ddmmyy in test_dates:
    print(f"\n--- Testing date: {ddmmyyyy} ---")
    urls = [
        # Pattern 1: CSV direct (today's format from page HTML)
        f'https://www.bseindia.com/download/BhavCopy/Equity/BhavCopy_BSE_CM_0_0_0_{ymd}_F_0000.CSV',
        # Pattern 2: ZIP format from page HTML 
        f'https://www.bseindia.com/download/BhavCopy/Equity/BSE_EQ_BHAVCOPY_{ddmmyyyy}_T0.ZIP',
        # Pattern 3: ISIN CSV
        f'https://www.bseindia.com/download/BhavCopy/Equity/EQ_ISINCODE_{ddmmyy}_T0.CSV',
    ]
    for url in urls:
        try:
            r = session.get(url, headers=headers, timeout=10)
            size = len(r.content)
            print(f'[{r.status_code}] size={size} | {url.split("/")[-1]}')
            if r.status_code == 200 and size > 1000:
                ct = r.headers.get('Content-Type', '')
                print(f'  Content-Type: {ct}')
                if 'zip' in ct.lower() or url.endswith('.ZIP') or url.endswith('.zip'):
                    try:
                        zf = zipfile.ZipFile(io.BytesIO(r.content))
                        print(f'  ZIP files: {zf.namelist()}')
                        df = pd.read_csv(zf.open(zf.namelist()[0]))
                        print(f'  Rows: {len(df)} | Cols: {df.columns.tolist()[:8]}')
                    except Exception as ze:
                        print(f'  ZIP parse error: {ze}')
                        print(f'  First 100 bytes: {r.content[:100]}')
                else:
                    df = pd.read_csv(io.StringIO(r.text))
                    print(f'  Rows: {len(df)} | Cols: {df.columns.tolist()[:8]}')
        except Exception as e:
            print(f'[ERR] {url.split("/")[-1]}: {e}')

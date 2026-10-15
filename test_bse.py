"""
Test BSE Bhavcopy download approaches.
BSE changed their URL format - testing all known working patterns.
"""
import requests, io, zipfile, pandas as pd, time

date_str   = '19022026'   # DDMMYYYY
date_short = '190226'     # DDMMYY
date_api   = '19/02/2026' # DD/MM/YYYY for API
date_ymd   = '20260219'   # YYYYMMDD

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Referer': 'https://www.bseindia.com/',
}

session = requests.Session()
print("Getting BSE session...")
session.get('https://www.bseindia.com', headers=headers, timeout=15)
time.sleep(1)

# All URL formats to test
candidate_urls = [
    # Old formats
    (f'https://www.bseindia.com/download/BhavCopy/Equity/EQ{date_short}_CSV.ZIP', 'zip'),
    (f'https://www.bseindia.com/download/BhavCopy/Equity/EQ{date_str}_CSV.ZIP', 'zip'),
    (f'https://www.bseindia.com/download/BhavCopy/Equity/BSE_CM_BhavCopy{date_ymd}.ZIP', 'zip'),
    # BSE India API
    (f'https://api.bseindia.com/BseIndiaAPI/api/BhavCopyDwnld/w?strdate={date_api}', 'zip'),
    # Archive patterns
    (f'https://www.bseindia.com/download/BhavCopy/Equity/EQ_ISINCODE_{date_short}.ZIP', 'zip'),
    # Direct CSV patterns
    (f'https://www.bseindia.com/download/BhavCopy/Equity/BhavCopy_{date_ymd}.ZIP', 'zip'),
    # New BSEData API
    (f'https://www.bseindia.com/download/BhavCopy/Equity/EQ{date_short}ALLOT.ZIP', 'zip'),
    # Try without session (plain requests)
]

for url, file_type in candidate_urls:
    try:
        r = session.get(url, headers=headers, timeout=10, allow_redirects=True)
        print(f'[{r.status_code}] {url}')
        if r.status_code == 200:
            print(f'  Content-Type: {r.headers.get("Content-Type")}')
            print(f'  Content-Length: {len(r.content)} bytes')
            if file_type == 'zip' and len(r.content) > 1000:
                try:
                    with zipfile.ZipFile(io.BytesIO(r.content)) as z:
                        print(f'  ZIP contents: {z.namelist()}')
                        with z.open(z.namelist()[0]) as f:
                            df = pd.read_csv(f)
                            print(f'  Rows: {len(df)} | Cols: {df.columns.tolist()}')
                except Exception as ze:
                    print(f'  ZIP error: {ze}')
                    print(f'  First 200 bytes: {r.content[:200]}')
    except Exception as e:
        print(f'[ERR] {url}: {e}')

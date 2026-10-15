"""
probe_nse_session.py — use requests session to hit the NSE API for MCap data
and probe BSE individual-stock API and bulk MCap report.
"""
import requests
import json
import datetime

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
})

# Step 1 — warm up NSE session (get cookies)
print("Warming NSE session...")
try:
    base = session.get('https://www.nseindia.com', timeout=10)
    print(f"  NSE base: {base.status_code}, cookies: {list(session.cookies.keys())}")
except Exception as e:
    print(f"  NSE base failed: {e}")

# Step 2 — probe NSE API endpoints
nse_apis = [
    'https://www.nseindia.com/api/market-cap-top-companies?category=allCap',
    'https://www.nseindia.com/api/market-cap-top-companies?category=large_mid',
    'https://www.nseindia.com/api/equity-market-cap-data',
    'https://www.nseindia.com/api/market-cap',
    'https://www.nseindia.com/api/quote-equity?symbol=RELIANCE',
    'https://www.nseindia.com/api/quote-equity?symbol=HDFCBANK',
]

print("\nProbing NSE APIs...")
for url in nse_apis:
    try:
        r = session.get(url, timeout=10)
        if r.status_code == 200:
            try:
                d = r.json()
                keys = list(d.keys()) if isinstance(d, dict) else f"list[{len(d)}]"
                print(f"  OK {url[-60:]} | keys={keys}")
                # If RELIANCE quote, look for MCap fields:
                if 'RELIANCE' in url and isinstance(d, dict):
                    flat = json.dumps(d)
                    for kw in ['ffmc','freefloat','free_float','marketCap','mcap','ffMcap']:
                        idx = flat.lower().find(kw.lower())
                        if idx >= 0:
                            print(f"    → found '{kw}' near: {flat[max(0,idx-10):idx+50]}")
            except:
                print(f"  OK {url[-60:]} | non-JSON len={len(r.content)}")
        else:
            print(f"  HTTP {r.status_code} {url[-60:]}")
    except Exception as e:
        print(f"  ERR {url[-60:]} => {e}")

# Step 3 — probe BSE API for free float MCap
print("\nProbing BSE APIs...")
bse_session = requests.Session()
bse_session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Referer': 'https://www.bseindia.com/',
})

dt = datetime.date(2026, 2, 20)
bse_apis = [
    # BSE scrip full data for 500325 (RELIANCE)
    'https://api.bseindia.com/BseIndiaAPI/api/getScripHeaderData/w?Debtflag=&scripcode=500325&seriesid=',
    'https://api.bseindia.com/BseIndiaAPI/api/ComHeader/w?quotetype=EQ&scripcode=500325&seriesid=EQ',
    # BSE market cap download page
    f'https://www.bseindia.com/markets/MarketInfo/DownloadFreeFloat.aspx',
    # BSE NSE mcap type URLs
    f'https://api.bseindia.com/Sensex/api/getMarketCap/w?flag=0&dt={dt.strftime("%Y%m%d")}',
]

for url in bse_apis:
    try:
        r = bse_session.get(url, timeout=10)
        if r.status_code == 200:
            try:
                d = r.json()
                flat = json.dumps(d)
                print(f"  OK {url[-70:]} | type={type(d).__name__}")
                for kw in ['FFMcap','ffmc','freefloat','FreeFloat','Mcap','mcap','MktCap']:
                    idx = flat.lower().find(kw.lower())
                    if idx >= 0:
                        print(f"    → '{kw}' near: {flat[max(0,idx-5):idx+60]!r}")
            except:
                preview = r.text[:200].replace('\n', ' ')
                print(f"  OK {url[-70:]} | non-JSON: {preview!r}")
        else:
            print(f"  HTTP {r.status_code} {url[-70:]}")
    except Exception as e:
        print(f"  ERR {url[-70:]} => {e}")

print("\nDone.")

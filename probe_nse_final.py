"""
probe_nse_final.py
NSE session with explicit decompression + BSE scrip API for ffmc field.
"""
import requests
import json
import time
import gzip
import io

def make_nse_session():
    s = requests.Session()
    s.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                      'Chrome/120.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
        'DNT': '1',
    })
    s.headers['Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,*/*;q=0.8'
    r = s.get('https://www.nseindia.com/', timeout=15)
    print(f"Homepage: {r.status_code}, cookies: {list(s.cookies.keys())}")
    time.sleep(2)
    s.headers['Referer'] = 'https://www.nseindia.com/'
    r2 = s.get('https://www.nseindia.com/market-data/live-equity-market', timeout=15)
    print(f"Market page: {r2.status_code}")
    time.sleep(1.5)
    s.headers['Accept'] = 'application/json, text/plain, */*'
    return s

def nse_get_json(session, url):
    r = session.get(url, timeout=15)
    # handle gzip manually if needed
    content = r.content
    if content[:2] == b'\x1f\x8b':  # gzip magic
        content = gzip.decompress(content)
    return json.loads(content.decode('utf-8'))

print("=== NSE Quote API ===")
s = make_nse_session()

for sym in ['RELIANCE', 'HDFCBANK', 'INFY']:
    try:
        url = f'https://www.nseindia.com/api/quote-equity?symbol={sym}'
        d = nse_get_json(s, url)
        print(f"\n{sym} - Keys: {list(d.keys())}")
        flat = json.dumps(d)
        for kw in ['ffmc', 'freefloat', 'free_float', 'ff_mc', 'marketCap', 'mktcap']:
            idx = flat.lower().find(kw.lower())
            if idx >= 0:
                print(f"  Found '{kw}': {flat[max(0,idx-10):idx+80]!r}")
        # Print priceInfo and tradeInfo specifically
        for section in ['tradeInfo', 'priceInfo', 'marketDeptOrderBook']:
            if section in d:
                print(f"  {section}: {json.dumps(d[section])[:200]}")
        time.sleep(1)
    except Exception as e:
        print(f"  {sym} error: {e}")

print("\n=== NSE Trade Info Section ===")
try:
    d = nse_get_json(s, 'https://www.nseindia.com/api/quote-equity?symbol=RELIANCE&section=trade_info')
    print(f"Keys: {list(d.keys())}")
    print(json.dumps(d, indent=2)[:1500])
except Exception as e:
    print(f"Error: {e}")

print("\n=== BSE ComHeader API ===")
# BSE scripcode 500325 = RELIANCE, 500180 = HDFCBANK
bse = requests.Session()
bse.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
    'Referer': 'https://www.bseindia.com/',
})
for code, sym in [('500325', 'RELIANCE'), ('500180', 'HDFCBANK')]:
    try:
        url = f'https://api.bseindia.com/BseIndiaAPI/api/ComHeader/w?quotetype=EQ&scripcode={code}&seriesid=EQ'
        r = bse.get(url, timeout=10)
        content = r.content
        if content[:2] == b'\x1f\x8b':
            content = gzip.decompress(content)
        try:
            d = json.loads(content.decode('utf-8'))
            print(f"\n{sym} ({code}) type={type(d)}")
            if isinstance(d, list):
                d = d[0] if d else {}
            flat = json.dumps(d)
            print(f"  Keys: {list(d.keys())[:20]}")
            for kw in ['FFMcap', 'ffmc', 'freefloat', 'FreeFloat', 'Mcap', 'MktCap', 'FF', 'Cap']:
                idx = flat.lower().find(kw.lower())
                if idx >= 0:
                    print(f"  Found '{kw}': {flat[max(0,idx-5):idx+80]!r}")
        except Exception as je:
            print(f"  JSON parse error: {je}, raw[:200]: {content[:200]!r}")
    except Exception as e:
        print(f"  {sym} error: {e}")

print("\nDone.")

"""
probe_nse_proper.py
Tests the NSE API with proper 2-step session warm-up (homepage → api), 
then checks individual quote endpoint for ffmc field.
Also probes the NSE equity list page for bulk data.
"""
import requests
import json
import time

def make_nse_session():
    s = requests.Session()
    s.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                      'Chrome/120.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
    })
    # Step 1: hit homepage to get cookies
    print("1. Hitting NSE homepage...")
    s.headers['Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
    r = s.get('https://www.nseindia.com/', timeout=15)
    print(f"   Status: {r.status_code}, Cookies: {list(s.cookies.keys())}")
    time.sleep(1.5)
    
    # Step 2: hit market page to get more cookies
    print("2. Hitting NSE market page...")
    s.headers['Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
    s.headers['Referer'] = 'https://www.nseindia.com/'
    r2 = s.get('https://www.nseindia.com/market-data/live-equity-market', timeout=15)
    print(f"   Status: {r2.status_code}, Cookies: {list(s.cookies.keys())}")
    time.sleep(1.5)
    
    s.headers['Accept'] = 'application/json, text/plain, */*'
    return s

s = make_nse_session()

# Try the quote-equity endpoint
print("\n3. Trying quote-equity API...")
for sym in ['RELIANCE', 'HDFCBANK']:
    try:
        r = s.get(f'https://www.nseindia.com/api/quote-equity?symbol={sym}', timeout=15)
        print(f"   {sym}: Status {r.status_code}, len={len(r.content)}")
        if r.status_code == 200:
            try:
                d = r.json()
                flat = json.dumps(d)
                print(f"   Keys: {list(d.keys())}")
                # Search for MCap related fields
                for kw in ['ffmc', 'freefloat', 'free_float', 'marketCap', 'ffMcap', 'FF_MCap']:
                    idx = flat.lower().find(kw.lower())
                    if idx >= 0:
                        print(f"   → '{kw}': {flat[max(0,idx-5):idx+80]!r}")
                # Print trade_info section if available
                if 'tradeInfo' in d:
                    print(f"   tradeInfo: {d['tradeInfo']}")
            except Exception as e:
                print(f"   JSON error: {e} | Response: {r.text[:200]}")
    except Exception as e:
        print(f"   Error: {e}")
    time.sleep(1)

# Try the trade_info section
print("\n4. Trying quote-equity trade_info section...")
try:
    r = s.get('https://www.nseindia.com/api/quote-equity?symbol=RELIANCE&section=trade_info', timeout=15)
    print(f"   Status: {r.status_code}, len={len(r.content)}")
    if r.status_code == 200:
        d = r.json()
        print(f"   Keys: {list(d.keys())}")
        flat = json.dumps(d)
        for kw in ['ffmc', 'freefloat', 'marketCap', 'mcap', 'FF']:
            idx = flat.lower().find(kw.lower())
            if idx >= 0:
                print(f"   → '{kw}': {flat[max(0,idx-5):idx+80]!r}")
        print(f"\n   Full JSON: {json.dumps(d, indent=2)[:1000]}")
except Exception as e:
    print(f"   Error: {e}")

# Also check NSE market cap report page for links
print("\n5. Checking NSE market data page...")
try:
    r = s.get('https://www.nseindia.com/market-data/equity-market-capitalisation', timeout=15)
    print(f"   Status: {r.status_code}")
    # Look for download links or API calls
    text = r.text[:3000]
    for kw in ['download', 'csv', 'mcap', 'marketcap', '.zip', 'api/']:
        idx = text.lower().find(kw.lower())
        if idx >= 0:
            print(f"   → '{kw}' at {idx}: {text[max(0,idx-20):idx+80]!r}")
except Exception as e:
    print(f"   Error: {e}")

print("\nDone.")

"""Verbose NSE API debug — check raw HTTP response."""
import requests
import gzip
import json
import time

s = requests.Session()
s.headers.update({
    'User-Agent': ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                   'AppleWebKit/537.36 (KHTML, like Gecko) '
                   'Chrome/120.0.0.0 Safari/537.36'),
    'Accept-Language': 'en-US,en;q=0.9',
    'DNT': '1',
})

# Step 1: homepage
print("Getting homepage...")
s.headers['Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
r = s.get('https://www.nseindia.com/', timeout=15)
print(f"  Status: {r.status_code}, Cookies: {list(s.cookies.keys())}")
time.sleep(2)

# Step 2: market page
print("Getting market page...")
s.headers['Referer'] = 'https://www.nseindia.com/'
r2 = s.get('https://www.nseindia.com/market-data/live-equity-market', timeout=15)
print(f"  Status: {r2.status_code}, Cookies: {list(s.cookies.keys())}")
time.sleep(1.5)

# Step 3: API call - verbose
print("\nGetting RELIANCE quote...")
s.headers['Accept'] = 'application/json, text/plain, */*'
s.headers['X-Requested-With'] = 'XMLHttpRequest'
url = 'https://www.nseindia.com/api/quote-equity?symbol=RELIANCE'
r3 = s.get(url, timeout=15)
print(f"  Status: {r3.status_code}")
print(f"  Headers: {dict(r3.headers)}")

content = r3.content
print(f"  Content length: {len(content)}")
print(f"  First 8 bytes (hex): {content[:8].hex()}")

# Try decode
if content[:2] == b'\x1f\x8b':
    print("  → GZIP detected, decompressing...")
    try:
        content = gzip.decompress(content)
        print(f"  Decompressed len: {len(content)}")
    except Exception as e:
        print(f"  GZIP error: {e}")
elif content[:4] == b'\x00\x00\x00\x00':
    print("  → Possible Brotli or other encoding")
    
print(f"  First 500 chars: {content[:500]!r}")

# Try JSON parse
try:
    d = json.loads(content.decode('utf-8', errors='replace'))
    print(f"\n  JSON keys: {list(d.keys())}")
    if 'marketDeptOrderBook' in d:
        trade = d['marketDeptOrderBook'].get('tradeInfo', {})
        print(f"  tradeInfo: {trade}")
except Exception as e:
    print(f"  JSON parse failed: {e}")

"""
probe_nse_ff.py — Diagnose why ffmc is None from NSE API.
Dumps the raw structure of marketDeptOrderBook and searches for ff/mcap fields.
"""
import requests, json, gzip, time

def make_session():
    s = requests.Session()
    s.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9', 'DNT': '1',
    })
    s.headers['Accept'] = 'text/html,*/*;q=0.8'
    r = s.get('https://www.nseindia.com/', timeout=15)
    print(f"Homepage: {r.status_code}")
    time.sleep(2)
    s.headers['Referer'] = 'https://www.nseindia.com/'
    s.get('https://www.nseindia.com/market-data/live-equity-market', timeout=15)
    time.sleep(1.5)
    s.headers['Accept'] = 'application/json, text/plain, */*'
    return s

def decode(r):
    c = r.content
    if c[:2] == b'\x1f\x8b': c = gzip.decompress(c)
    return json.loads(c.decode('utf-8'))

s = make_session()

# --- Standard quote-equity endpoint ---
print("\n=== /api/quote-equity?symbol=RELIANCE ===")
r = s.get('https://www.nseindia.com/api/quote-equity?symbol=RELIANCE', timeout=15)
print(f"Status: {r.status_code}")
d = decode(r)
print(f"Top-level keys: {list(d.keys())}")

# Check marketDeptOrderBook fully
mdo = d.get('marketDeptOrderBook') or {}
print(f"\nmarketDeptOrderBook keys: {list(mdo.keys())}")
ti = mdo.get('tradeInfo') or {}
print(f"tradeInfo: {json.dumps(ti)}")
print(f"tradeInfo empty? {not ti}")

# Search ENTIRE JSON for ffmc
flat = json.dumps(d).lower()
for kw in ['ffmc', 'freefloat', 'free_float', 'ffmktcap', 'ff_mcap', 'ffmcap', 'freefl']:
    idx = flat.find(kw)
    if idx >= 0:
        print(f"\n✅ Found '{kw}': ...{flat[max(0,idx-20):idx+100]}...")
    else:
        print(f"❌ '{kw}' NOT found in response")

# --- Try section=trade_info variant ---
print("\n=== /api/quote-equity?symbol=RELIANCE&section=trade_info ===")
time.sleep(0.5)
try:
    r2 = s.get('https://www.nseindia.com/api/quote-equity?symbol=RELIANCE&section=trade_info', timeout=15)
    print(f"Status: {r2.status_code}")
    d2 = decode(r2)
    print(f"Keys: {list(d2.keys())}")
    ti2 = (d2.get('marketDeptOrderBook') or {}).get('tradeInfo') or {}
    print(f"tradeInfo: {json.dumps(ti2)[:500]}")
    if ti2.get('ffmc'):
        print(f"✅ ffmc = {ti2['ffmc']}, totalMarketCap = {ti2.get('totalMarketCap')}")
    else:
        print("❌ ffmc not in tradeInfo")
except Exception as e:
    print(f"Error: {e}")

# --- Check priceInfo for any mcap data ---
print("\n=== priceInfo section ===")
pi = d.get('priceInfo') or {}
print(f"priceInfo keys: {list(pi.keys())}")
for k, v in pi.items():
    if 'cap' in k.lower() or 'ff' in k.lower() or 'mcap' in k.lower():
        print(f"  {k}: {v}")

print("\nDone.")

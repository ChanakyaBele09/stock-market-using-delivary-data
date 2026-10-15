"""Dump full NSE API response to file for inspection."""
import requests, gzip, json, time

s = requests.Session()
s.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120'})
s.headers['Accept'] = 'text/html,*/*'
s.get('https://www.nseindia.com/', timeout=15)
time.sleep(2)
s.headers['Referer'] = 'https://www.nseindia.com/'
s.get('https://www.nseindia.com/market-data/live-equity-market', timeout=15)
time.sleep(1.5)

s.headers['Accept'] = 'application/json'
r = s.get('https://www.nseindia.com/api/quote-equity?symbol=RELIANCE', timeout=15)
content = r.content
if content[:2] == b'\x1f\x8b':
    content = gzip.decompress(content)

d = json.loads(content.decode('utf-8', errors='replace'))
# Write full JSON
with open('nse_reliance_response.json', 'w') as f:
    json.dump(d, f, indent=2)
print('Saved to nse_reliance_response.json')
print('Top-level keys:', list(d.keys()))

# Search for ffmc in flattened JSON
flat = json.dumps(d)
for kw in ['ffmc', 'freeFloat', 'freefloat', 'totalMarket', 'marketCap', 'mktCap', 'ffMc']:
    idx = flat.lower().find(kw.lower())
    if idx >= 0:
        print(f"  Found '{kw}' near: {flat[max(0,idx-15):idx+80]!r}")
    else:
        print(f"  NOT found: {kw}")

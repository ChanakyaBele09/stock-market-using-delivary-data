"""
probe_nse_mcap_bulk.py
Probe for NSE bulk market cap files - the correct download endpoint.
NSE publishes MCap reports - let's find the right URL.
"""
import requests
import gzip
import json
import time

s = requests.Session()
s.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120'})
s.headers['Accept'] = 'text/html,*/*'
s.get('https://www.nseindia.com/', timeout=15)
time.sleep(1.5)
s.headers['Referer'] = 'https://www.nseindia.com/'
s.get('https://www.nseindia.com/market-data/live-equity-market', timeout=15)
time.sleep(1.5)
s.headers['Accept'] = 'application/json'

# Check NSE equity market cap API endpoints
endpoints = [
    # NSE market cap rankings API
    'https://www.nseindia.com/api/market-cap-top-companies?category=allCap&from=1&to=50',
    'https://www.nseindia.com/api/equity-stockIndices?index=NIFTY%2050',
    # NSE MCap with section parameter
    'https://www.nseindia.com/api/quote-equity?symbol=RELIANCE&section=trade_info',
    # NSE equity list with mcap
    'https://www.nseindia.com/api/live-analysis-variations?index=gainers',
    # NSE bulk MCap report metadata
    'https://www.nseindia.com/api/market-cap-companies',
    'https://www.nseindia.com/api/marketcap',
    # BSE MCap via a better endpoint  
    'https://api.bseindia.com/BseIndiaAPI/api/MarketCapReport/w?type=M&flag=&fromdate=&todate=',
    'https://api.bseindia.com/BseIndiaAPI/api/getQuotes/w?code=500325&Entry=Q',
    'https://api.bseindia.com/BseIndiaAPI/api/MktCapData/w',
]

for url in endpoints:
    try:
        r = s.get(url, timeout=12)
        content = r.content
        if content[:2] == b'\x1f\x8b':
            content = gzip.decompress(content)
        
        try:
            d = json.loads(content.decode('utf-8', errors='replace'))
            flat = json.dumps(d)
            has_ff = any(kw.lower() in flat.lower() 
                        for kw in ['ffmc', 'freeFloat', 'freefloat', 'ff_mcap'])
            keys = list(d.keys()) if isinstance(d, dict) else f'list[{len(d) if isinstance(d, list) else "?"}]'
            print(f'  OK {r.status_code} | ffmc={has_ff} | keys={str(keys)[:80]} | {url[-60:]}')
            if has_ff:
                for kw in ['ffmc', 'freeFloat', 'freefloat']:
                    idx = flat.lower().find(kw.lower())
                    if idx >= 0:
                        print(f'    → {kw}: {flat[max(0,idx-10):idx+100]!r}')
        except:
            preview = content[:150].decode('utf-8', errors='replace').replace('\n', ' ')
            print(f'  OK {r.status_code} | non-JSON: {preview!r} | {url[-60:]}')
    except Exception as e:
        print(f'  ERR {url[-60:]}: {e}')

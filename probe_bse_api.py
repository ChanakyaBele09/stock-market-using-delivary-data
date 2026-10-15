"""probe_bse_api.py - probe BSE API for MCap fields"""
import requests
import json

s = requests.Session()
s.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120',
    'Referer': 'https://www.bseindia.com/',
    'Origin': 'https://www.bseindia.com'
})

# Full structure of BSE header response
r = s.get('https://api.bseindia.com/BseIndiaAPI/api/getScripHeaderData/w?Debtflag=&scripcode=500325&seriesid=', timeout=10)
d = r.json()
print('Top keys:', list(d.keys()))
comp = d.get('CompResp', {})
print('\nCompResp keys:', list(comp.keys()))
for k, v in comp.items():
    if any(x in k.lower() for x in ['mcap', 'cap', 'float', 'ff', 'free', 'mkt']):
        print(f'  MCAP FIELD: {k} = {v}')

# Also print Header
hdr = d.get('Header', {})
print('\nHeader fields:')
for k, v in hdr.items():
    print(f'  {k} = {v}')

# Also try BSE ComHeader API
print('\nTrying ComHeader...')
r2 = s.get('https://api.bseindia.com/BseIndiaAPI/api/ComHeader/w?quotetype=EQ&scripcode=500325&seriesid=EQ', timeout=10)
print('Status:', r2.status_code)
try:
    d2 = r2.json()
    print('Keys:', list(d2.keys()))
    flat = json.dumps(d2)
    for kw in ['FFMcap', 'ffmc', 'freefloat', 'FreeFloat', 'Mcap', 'mcap', 'MktCap', 'FF']:
        idx = flat.lower().find(kw.lower())
        if idx >= 0:
            print(f"  Found '{kw}': {flat[max(0,idx-5):idx+80]!r}")
except Exception as e:
    print('Non-JSON:', r2.text[:300])

# BSE bulk market cap
print('\nTrying BSE bulk MCap endpoints...')
bulk_urls = [
    'https://api.bseindia.com/BseIndiaAPI/api/marketcapital/w',
    'https://api.bseindia.com/BseIndiaAPI/api/MarketCap/w',
    'https://api.bseindia.com/BseIndiaAPI/api/getMarketCapFormat/w?ddlcategory=M',
    'https://www.bseindia.com/markets/equity/EQReports/GetMarketCapFormat.aspx?ddlcategory=M&Type=E',
]
for u in bulk_urls:
    try:
        rr = s.get(u, timeout=8)
        preview = rr.text[:150].replace('\n', ' ')
        print(f'  {rr.status_code} {u[-60:]}: {preview!r}')
    except Exception as e:
        print(f'  ERR {u[-60:]}: {e}')

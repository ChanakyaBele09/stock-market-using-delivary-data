"""
probe_bse_mcap.py
Probe BSE APIs for:
1. Scrip list with ISIN → scrip_code mapping (bulk)
2. Individual stock FF MCap (issued_size + ff_factor)
"""
import requests
import gzip
import json

bse = requests.Session()
bse.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120',
    'Referer': 'https://www.bseindia.com/',
    'Origin': 'https://www.bseindia.com',
    'Accept': 'application/json, text/plain, */*',
})

def decode(r):
    c = r.content
    if c[:2] == b'\x1f\x8b':
        c = gzip.decompress(c)
    return c

def probe(url, label=''):
    try:
        r = bse.get(url, timeout=12)
        c = decode(r)
        try:
            d = json.loads(c.decode('utf-8', errors='replace'))
            flat = json.dumps(d)
            # Look for FF MCap fields
            ff_found = []
            for kw in ['FFMcap', 'ffmc', 'FreeFloat', 'freefloat', 'McapFF', 'Mcap_FF',
                       'MktCap', 'mcap', 'MCapFF', 'FFMCAP', 'FF_MCap', 'Mktcap']:
                idx = flat.lower().find(kw.lower())
                if idx >= 0:
                    ff_found.append(f'{kw}={flat[idx:idx+40]!r}')
            # Look for ISIN fields
            isin_found = 'ISIN' in flat or 'isin' in flat
            keys = list(d.keys()) if isinstance(d, dict) else (
                f'list[{len(d)}]' if isinstance(d, list) else type(d).__name__
            )
            print(f'  OK {r.status_code} | {str(keys)[:60]} | isin={isin_found} | {url[-65:]}')
            if ff_found:
                print(f'    FF fields: {ff_found[:4]}')
            if isinstance(d, list) and len(d) > 0:
                print(f'    Sample[0] keys: {list(d[0].keys())[:10] if isinstance(d[0], dict) else d[0]}')
        except Exception as je:
            preview = c[:150].decode('utf-8', errors='replace').replace('\n', ' ')
            print(f'  OK {r.status_code} | non-JSON | {url[-65:]}: {preview!r}')
    except Exception as e:
        print(f'  ERR {url[-65:]}: {type(e).__name__}: {e}')

# ── 1. BSE master scrip list ──────────────────────────────────────────────────
print('\n=== BSE Bulk Scrip List (ISIN→Code mapping) ===')
scrip_urls = [
    # Standard BSE equity list
    'https://api.bseindia.com/BseIndiaAPI/api/ListofScripData/w?Group=&Scripcode=&shname=&PSindustry=&segment=Equity&status=Active',
    # BSE equity list via different param
    'https://api.bseindia.com/BseIndiaAPI/api/getScripData/w?Segment=Equity&status=Active',
    # BSE download list
    'https://www.bseindia.com/corporates/List_Scrips.aspx',
    # Direct CSV from BSE
    'https://www.bseindia.com/download/BhavCopy/Equity/EQ_ISINDEQCONV_20022026_F.ZIP',
    # Master data
    'https://api.bseindia.com/BseIndiaAPI/api/GetScripDataSet/w?Segment=Equity',
]
for u in scrip_urls:
    probe(u)

# ── 2. Individual stock MCap (FF MCap) ────────────────────────────────────────
# 500325=RELIANCE, 532454=BHARTIARTL, 540777=HDFC BANK, 507685=BSE-ONLY STOCK
print('\n=== BSE Individual MCap APIs ===')
mcap_urls = [
    # BSE exchange summary - likely has MCap
    'https://api.bseindia.com/BseIndiaAPI/api/IndExchSummary/w?scripcode=500325&seriesid=EQ',
    'https://api.bseindia.com/BseIndiaAPI/api/IndExchSummary/w?scripcode=500325',
    # BSE getQuotes - like Bloomberg terminal style
    'https://api.bseindia.com/BseIndiaAPI/api/getQuotes/w?code=500325&Entry=Q',
    'https://api.bseindia.com/BseIndiaAPI/api/getQuotes/w?code=500325',
    # Market summary
    'https://api.bseindia.com/BseIndiaAPI/api/MktSummary/w?scripcode=500325',
    # Full company details
    'https://api.bseindia.com/BseIndiaAPI/api/CompanyHeader/w?scripcode=500325',
    # BSE scrip details 
    'https://api.bseindia.com/BseIndiaAPI/api/GetScripDetails/w?scripcode=500325',
    # BSEPlus
    'https://api.bseindia.com/BseIndiaAPI/api/stockReachGraph/w?scripcode=500325&flag=0&fromdate=20260220&todate=20260220&seriesid=EQ',
    # Fundamental data
    'https://api.bseindia.com/BseIndiaAPI/api/GetSummaryData/w?scripcode=500325',
]
for u in mcap_urls:
    probe(u)

print('\nDone.')

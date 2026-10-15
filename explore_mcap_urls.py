"""
explore_mcap_urls.py — probe NSE/BSE URLs for bulk free-float market cap data.
"""
import urllib.request
import urllib.error
import datetime
import io
import zipfile
import sys

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Referer': 'https://www.nseindia.com/',
}

dt = datetime.date(2026, 2, 20)   # last trading day
d = dt.strftime('%d%m%Y')          # DDMMYYYY
d2 = dt.strftime('%d-%m-%Y')       # DD-MM-YYYY
d3 = dt.strftime('%Y%m%d')         # YYYYMMDD

NSE_URLS = [
    # Known MCap report URL patterns
    f'https://archives.nseindia.com/reports/NSE_EQUITY_MCAP_{d}.zip',
    f'https://archives.nseindia.com/content/indices/mcap{d3}.csv',
    f'https://archives.nseindia.com/content/equities/mcap{d3}.csv',
    # NSE market cap via API
    'https://www.nseindia.com/api/equity-market-cap-data',
    'https://www.nseindia.com/api/market-cap',
    # NSE download page for market cap
    'https://archives.nseindia.com/content/equities/EQUITY_L.csv',
]

BSE_URLS = [
    # BSE market cap report
    f'https://www.bseindia.com/download/BhavCopy/Equity/EQ_ISINDEQCONV_{d}_F.ZIP',
    'https://api.bseindia.com/BseIndiaAPI/api/getScripHeaderData/w?Debtflag=&scripcode=500325&seriesid=',
    f'https://www.bseindia.com/markets/MarketInfo/DownloadFreeFloat.aspx',
    # BSE bulk MCap CSV  
    f'https://www.bseindia.com/download/MarketCapitalization/MarketCapitalization_{d2}.zip',
]

def probe(url, label=''):
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        resp = urllib.request.urlopen(req, timeout=10)
        ctype = resp.headers.get('Content-Type', '?')
        clen  = resp.headers.get('Content-Length', '?')
        raw   = resp.read(2000)
        # If zip, peek inside
        if b'PK' in raw[:4]:
            try:
                z = zipfile.ZipFile(io.BytesIO(raw + resp.read()))
                names = z.namelist()
                first = z.read(names[0])[:300].decode('latin-1', errors='replace')
                print(f'  OK ZIP {url[-60:]} | files={names} | preview={first[:120]!r}')
                return
            except Exception as ze:
                print(f'  OK ZIP-ERR {url[-60:]} | {ze}')
                return
        preview = raw.decode('utf-8', errors='replace')[:200].replace('\n', ' ')
        print(f'  OK {resp.getcode()} {url[-70:]} | size={clen} | {preview!r}')
    except urllib.error.HTTPError as e:
        print(f'  HTTP {e.code} {url[-70:]}')
    except Exception as ex:
        print(f'  ERR {url[-70:]} => {type(ex).__name__}: {str(ex)[:60]}')

print('\n=== NSE URLs ===')
for u in NSE_URLS:
    probe(u)

print('\n=== BSE URLs ===')
for u in BSE_URLS:
    probe(u)

print('\ndone')

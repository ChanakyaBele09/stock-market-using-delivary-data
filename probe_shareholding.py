"""
probe_shareholding.py
Check SEBI and NSE quarterly shareholding pattern files for ff_factor derivation.
ff_factor = 1 - (promoter_holding_pct / 100)
"""
import requests, json, zipfile, io, time

s = requests.Session()
s.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120',
    'Accept': '*/*',
})

def probe(label, url):
    try:
        r = s.get(url, timeout=20)
        c = r.content
        print(f'[{label}] {r.status_code} | len={len(c)} | type={r.headers.get("Content-Type","?")}')
        
        if r.status_code == 200:
            # Try ZIP
            if c[:2] == b'PK':
                z = zipfile.ZipFile(io.BytesIO(c))
                print(f'  ZIP contents: {z.namelist()}')
                # Read first CSV
                for name in z.namelist()[:2]:
                    lines = z.read(name).decode('utf-8', errors='replace').split('\n')
                    print(f'  {name} header: {lines[0][:150]}')
                    print(f'  {name} line 2: {lines[1][:150]}')
                return
            # Try JSON
            try:
                d = json.loads(c.decode('utf-8', errors='replace'))
                flat = json.dumps(d)
                prom_kws = [kw for kw in ['Promoter', 'promoter', 'PublicHold', 'freefloat', 'FreeFloat', 'NonPromoter']
                            if kw.lower() in flat.lower()]
                print(f'  JSON | prom_kws={prom_kws}')
                if prom_kws and isinstance(d, list) and d:
                    print(f'  sample[0]: {d[0]}')
                elif prom_kws and isinstance(d, dict):
                    print(f'  sample: {str(d)[:300]}')
                return
            except:
                pass
            # Show raw text
            preview = c[:300].decode('utf-8', errors='replace').replace('\n', ' ')
            print(f'  Raw: {preview!r}')
    except Exception as e:
        print(f'[{label}] ERR: {e}')
    time.sleep(0.4)

print('=== NSE shareholding bulk ===')
# NSE quarterly shareholding CSV (format: promoter, DII, FII, public)
probe('nse_shold_q3_2025', 'https://archives.nseindia.com/corporate/shareholdingpattern/Dec2025.zip')
probe('nse_shold_q2_2025', 'https://archives.nseindia.com/corporate/shareholdingpattern/Sep2025.zip')
probe('nse_shold_q3_csv',  'https://archives.nseindia.com/corporate/shareholdingpattern/Dec2025.csv')

print('\n=== BSE shareholding bulk ===')
probe('bse_shold_bulk1', 'https://www.bseindia.com/data/xml/SP_bulk.zip')
probe('bse_shold_bulk2', 'https://www.bseindia.com/sharedata/shar_hold/Dec2025_Dec2025.xls')
probe('bse_shold_zip',   'https://www.bseindia.com/sharedata/shar_hold/BSE_Share_Pattern_Dec_2025.zip')
probe('bse_shold_api',   'https://api.bseindia.com/BseIndiaAPI/api/ShareHoldingReport/w')

print('\n=== Direct NSE API for promoter holding ===')
# NSE has a corporate actions API that includes shareholding
s.headers['Referer'] = 'https://www.nseindia.com/'
s.headers['Accept'] = 'application/json'
s.get('https://www.nseindia.com/', timeout=10)
time.sleep(1.5)
s.get('https://www.nseindia.com/market-data/live-equity-market', timeout=10)
time.sleep(1)
probe('nse_shold_reliance', 'https://www.nseindia.com/api/corporate-shareholding?symbol=RELIANCE&market=equities&quarters=December2025')
probe('nse_shold_api2',     'https://www.nseindia.com/api/corporates-shp?index=NIFTY50&period=December2025')

print('\nDone.')

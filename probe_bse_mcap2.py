"""
probe_bse_mcap2.py - cleaner version, saves to file
"""
import requests, gzip, json, time

bse = requests.Session()
bse.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120',
    'Referer': 'https://www.bseindia.com/',
    'Accept': 'application/json, text/plain, */*',
})

def fetch(url):
    r = bse.get(url, timeout=12)
    c = r.content
    if c[:2] == b'\x1f\x8b':
        c = gzip.decompress(c)
    return r.status_code, c

results = []

tests = [
    # --- Bulk scrip list ---
    ('bulk_list_1', 'https://api.bseindia.com/BseIndiaAPI/api/ListofScripData/w?Group=&Scripcode=&shname=&PSindustry=&segment=Equity&status=Active'),
    ('bulk_list_2', 'https://api.bseindia.com/BseIndiaAPI/api/getScripData/w?Segment=Equity&status=Active'),
    # --- Individual MCap ---
    ('ind_exch_sum_eq', 'https://api.bseindia.com/BseIndiaAPI/api/IndExchSummary/w?scripcode=500325&seriesid=EQ'),
    ('ind_exch_sum',    'https://api.bseindia.com/BseIndiaAPI/api/IndExchSummary/w?scripcode=500325'),
    ('get_quotes',      'https://api.bseindia.com/BseIndiaAPI/api/getQuotes/w?code=500325&Entry=Q'),
    ('mkt_summary',     'https://api.bseindia.com/BseIndiaAPI/api/MktSummary/w?scripcode=500325'),
    ('company_header',  'https://api.bseindia.com/BseIndiaAPI/api/CompanyHeader/w?scripcode=500325'),
    ('scrip_details',   'https://api.bseindia.com/BseIndiaAPI/api/GetScripDetails/w?scripcode=500325'),
    ('summary_data',    'https://api.bseindia.com/BseIndiaAPI/api/GetSummaryData/w?scripcode=500325'),
    # BSE scrip code lookup by ISIN
    ('isin_lookup',     'https://api.bseindia.com/BseIndiaAPI/api/fetchbyscrip/w?ISIN=INE002A01018'),
    ('isin_lookup2',    'https://api.bseindia.com/BseIndiaAPI/api/GetScripByIsin/w?isin=INE002A01018'),
]

with open('bse_probe_results.txt', 'w') as f:
    for label, url in tests:
        try:
            status, content = fetch(url)
            try:
                d = json.loads(content.decode('utf-8', errors='replace'))
                flat = json.dumps(d)
                ff_kws = [kw for kw in ['FFMcap','ffmc','FreeFloat','McapFF','Mcap_FF','MktCap',
                                         'MCapFF','FFMCAP','MktCapFF','CMP','Mcap','ISIN','isin',
                                         'issued','issued_size','outstanding']
                          if kw.lower() in flat.lower()]
                is_list = isinstance(d, list)
                top_keys = list(d.keys()) if isinstance(d, dict) else (
                    list(d[0].keys())[:8] if is_list and d and isinstance(d[0], dict) else str(type(d))
                )
                line = f'[{label}] {status} JSON | keys={top_keys} | ff_kws={ff_kws}\n'
                # Print sample with ff fields
                if ff_kws:
                    for kw in ff_kws[:3]:
                        idx = flat.lower().find(kw.lower())
                        line += f'  {kw}: ...{flat[max(0,idx-5):idx+60]}...\n'
                elif is_list and d:
                    line += f'  list len={len(d)}, sample[0]={json.dumps(d[0])[:200]}\n'
            except Exception:
                line = f'[{label}] {status} HTML/non-JSON | first200: {content[:200].decode("utf-8","replace").replace(chr(10)," ")}\n'
            f.write(line)
            print(line, end='')
        except Exception as e:
            line = f'[{label}] ERR {type(e).__name__}: {e}\n'
            f.write(line)
            print(line, end='')
        time.sleep(0.5)

print('Done. See bse_probe_results.txt')

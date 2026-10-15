"""
probe_bse_ff.py
Find BSE FF MCap or shareholding (promoter %) data through alternate endpoints.
ff_factor = 1 - promoter_holding_pct / 100
"""
import requests, json, time

bse = requests.Session()
bse.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120',
    'Referer': 'https://www.bseindia.com/',
    'Accept': 'application/json, text/plain, */*',
})

def probe(label, url, save_json=None):
    try:
        r = bse.get(url, timeout=15)
        c = r.content
        try:
            d = json.loads(c.decode('utf-8', errors='replace'))
            flat = json.dumps(d)
            ff_kws = [kw for kw in ['FFMcap', 'Mcap_FF', 'freefloat', 'FreeFloat',
                                     'Promoter', 'promoter', 'ShareHolding',
                                     'PublicHolding', 'NonPromoter', 'float',
                                     'FFMCAP', 'MktCapFF', 'FF']
                      if kw.lower() in flat.lower()]
            keys = list(d.keys()) if isinstance(d, dict) else (
                f'list[{len(d)}], sample_keys={list(d[0].keys())[:8]}' if isinstance(d, list) and d else type(d).__name__)
            print(f'  [{label}] {r.status_code} JSON | ff={ff_kws} | {str(keys)[:80]}')
            if ff_kws and save_json:
                with open(save_json, 'w') as f:
                    json.dump(d, f, indent=2)
                print(f'    → Saved to {save_json}')
            # Show sample data
            if isinstance(d, list) and d and isinstance(d[0], dict):
                for kw in ff_kws[:2]:
                    idx = flat.lower().find(kw.lower())
                    print(f'    {kw}: {flat[idx:idx+80]!r}')
        except Exception:
            preview = c[:120].decode('utf-8', errors='replace').replace('\n', ' ')
            print(f'  [{label}] {r.status_code} HTML | {preview!r}')
    except Exception as e:
        print(f'  [{label}] ERR: {e}')
    time.sleep(0.4)

print('\n=== BSE FF MCap / Shareholding endpoints ===')

# BSE has a market cap segment page with FF data
# Example: https://www.bseindia.com/market/Equity/EQReports/MarketWatch.aspx
# API version:
probe('mktwatch_bulk', 'https://api.bseindia.com/BseIndiaAPI/api/ManageMarketWatch/w?marketwatchid=1')
probe('mktcap_segment', 'https://api.bseindia.com/BseIndiaAPI/api/MarketCapData/w?type=M&flag=&fromdate=&todate=')
probe('mktcap_report',  'https://api.bseindia.com/BseIndiaAPI/api/MktCapReport/w')
probe('ff_mktcap',      'https://api.bseindia.com/BseIndiaAPI/api/FFMktCap/w')
probe('equity_ff',      'https://api.bseindia.com/BseIndiaAPI/api/EquityFF/w?scripcode=500325')

# BSE Shareholding pattern APIs
probe('shold_current',  'https://api.bseindia.com/BseIndiaAPI/api/ShareHoldingPatterns/w?scripcode=500325&type=&period=')
probe('shold_bulk',     'https://api.bseindia.com/BseIndiaAPI/api/ShareHoldingBulk/w?period=December+2025')
probe('promoter_hold',  'https://api.bseindia.com/BseIndiaAPI/api/PromoterHolding/w?scripcode=500325')

# NSE Shareholding (can give ff_factor for NSE stocks which covers BSE dually-listed too)
# NSE publishes shareholding for all listed companies
probe('nse_shold',      'https://www.nseindia.com/api/corporate-shareholding-data?index=NIFTY+50')

# BSE Index composition (Sensex weights = proportional to FF MCap)
probe('sensex_comp',    'https://api.bseindia.com/BseIndiaAPI/api/GetIndexComp/w?index=16&type=C&SubIndustry=MCI&IndexCode=BSESENSEX&flag=')
probe('sensex30',       'https://api.bseindia.com/BseIndiaAPI/api/SensexWtage/w?index=BSESENSEX')

# BSE bhav copy with additional MCap columns?
probe('bhav_plus',      'https://api.bseindia.com/BseIndiaAPI/api/BhavData/w?Dt=20022026')

# SEBI SAST / shareholding bulk data
probe('bse_public_shold', 'https://api.bseindia.com/BseIndiaAPI/api/shareholding/w?period=Q&Dt=31122025&scripcode=500325')
probe('bse_mcap_ff_list', 'https://api.bseindia.com/BseIndiaAPI/api/ListofScripData/w?Group=&Scripcode=&shname=&PSindustry=&segment=Equity&status=Active&withFF=Y')

print('\nDone.')

"""
Expand NSE sector coverage by trying all available NSE index CSVs.
Goal: maximise Symbol -> Industry coverage across all listed NSE stocks.
"""
import requests, io, pandas as pd

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

# Broader + sector-specific NSE index constituent files
urls = {
    # Broad market
    'NIFTY_ALL_SHARE':     'https://archives.nseindia.com/content/indices/ind_niftyallshare_list.csv',
    'NIFTY_TOTAL_MARKET':  'https://archives.nseindia.com/content/indices/ind_niftytotalmarket_list.csv',
    'NIFTY500':            'https://archives.nseindia.com/content/indices/ind_nifty500list.csv',
    'NIFTY_MICROCAP250':   'https://archives.nseindia.com/content/indices/ind_niftymicrocap250_list.csv',
    'NIFTY_SMALLCAP250':   'https://archives.nseindia.com/content/indices/ind_niftysmallcap250list.csv',
    'NIFTY_SMALLCAP50':    'https://archives.nseindia.com/content/indices/ind_niftysmallcap50list.csv',
    'NIFTY_MIDCAP150':     'https://archives.nseindia.com/content/indices/ind_niftymidcap150list.csv',
    'NIFTY_MIDCAP50':      'https://archives.nseindia.com/content/indices/ind_niftymidcap50list.csv',
    'NIFTY_LARGEMID250':   'https://archives.nseindia.com/content/indices/ind_niftylargemidc250list.csv',
    # Sector indices (include stocks not in broader indices)
    'NIFTY_AUTO':          'https://archives.nseindia.com/content/indices/ind_niftyautolist.csv',
    'NIFTY_BANK':          'https://archives.nseindia.com/content/indices/ind_niftybanklist.csv',
    'NIFTY_ENERGY':        'https://archives.nseindia.com/content/indices/ind_niftyenergylist.csv',
    'NIFTY_FINSERV':       'https://archives.nseindia.com/content/indices/ind_niftyfinancelist.csv',
    'NIFTY_FMCG':          'https://archives.nseindia.com/content/indices/ind_niftyfmcglist.csv',
    'NIFTY_IT':            'https://archives.nseindia.com/content/indices/ind_niftyitlist.csv',
    'NIFTY_MEDIA':         'https://archives.nseindia.com/content/indices/ind_niftymedialist.csv',
    'NIFTY_METAL':         'https://archives.nseindia.com/content/indices/ind_niftymetallist.csv',
    'NIFTY_PHARMA':        'https://archives.nseindia.com/content/indices/ind_niftypharmalist.csv',
    'NIFTY_PSU_BANK':      'https://archives.nseindia.com/content/indices/ind_niftypsubanklist.csv',
    'NIFTY_REALTY':        'https://archives.nseindia.com/content/indices/ind_niftyrealtylist.csv',
    'NIFTY_HEALTHCARE':    'https://archives.nseindia.com/content/indices/ind_niftyhealthcare_list.csv',
    'NIFTY_INFRA':         'https://archives.nseindia.com/content/indices/ind_niftyinfralist.csv',
    'NIFTY_PSE':           'https://archives.nseindia.com/content/indices/ind_niftypse_list.csv',
    'NIFTY_OIL_GAS':       'https://archives.nseindia.com/content/indices/ind_niftyoilgas_list.csv',
    'NIFTY_CONSUMER_DURABLES': 'https://archives.nseindia.com/content/indices/ind_niftyconsumerdurableslist.csv',
    'NIFTY_CAPITAL_MARKETS':   'https://archives.nseindia.com/content/indices/ind_niftycapitalmarket_list.csv',
}

all_dfs = []
for name, url in urls.items():
    try:
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code == 200:
            df = pd.read_csv(io.StringIO(r.text))
            if 'Symbol' in df.columns and 'Industry' in df.columns:
                all_dfs.append(df[['Symbol', 'Industry']])
                print(f"[OK] {name}: {len(df)} rows")
            else:
                print(f"[SKIP] {name}: missing Symbol/Industry cols | {df.columns.tolist()}")
        else:
            print(f"[{r.status_code}] {name}")
    except Exception as e:
        print(f"[ERR] {name}: {e}")

if all_dfs:
    combined = pd.concat(all_dfs, ignore_index=True)
    before = len(combined)
    # Keep first occurrence (broader indices are listed first so have more accurate classification)
    combined = combined.drop_duplicates(subset=['Symbol'], keep='first')
    print(f"\nTotal unique symbols: {len(combined)} (from {before} rows)")
    combined.to_csv(r"d:\Trading Workflows\data\nse_index_combined.csv", index=False)
    print(f"Saved to nse_index_combined.csv")
    print("\nSample:")
    print(combined.head(10).to_string())

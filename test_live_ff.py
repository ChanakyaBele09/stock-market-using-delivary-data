"""
test_live_ff.py — Quick test of NSE FF MCap for specific symbols during market hours.
Run:   .venv\Scripts\python.exe test_live_ff.py
"""
import sys, os, time, json, gzip
import requests, sqlite3

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
DB_PATH = os.path.join(os.path.dirname(__file__), 'data', 'stock_data.db')
NSE_BASE = 'https://www.nseindia.com'
TEST_SYMBOLS = ['RELIANCE', 'ITC', 'HDFCBANK']

def make_session():
    s = requests.Session()
    s.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
        'DNT': '1',
    })
    return s

def warm_session(s):
    print("Warming NSE session...")
    s.headers['Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
    r = s.get(f'{NSE_BASE}/', timeout=15)
    print(f"  Homepage: {r.status_code}")
    time.sleep(2)
    s.headers['Referer'] = f'{NSE_BASE}/'
    r2 = s.get(f'{NSE_BASE}/market-data/live-equity-market', timeout=15)
    print(f"  Market page: {r2.status_code}")
    time.sleep(1.5)
    s.headers['Accept'] = 'application/json, text/plain, */*'
    print("Session ready.\n")

def nse_decode(r):
    c = r.content
    if c[:2] == b'\x1f\x8b':
        c = gzip.decompress(c)
    return json.loads(c.decode('utf-8'))

def fetch_quote(s, symbol):
    url = f'{NSE_BASE}/api/quote-equity?symbol={symbol}'
    r = s.get(url, timeout=15)
    if r.status_code != 200:
        print(f"  {symbol}: HTTP {r.status_code}")
        return None, None
    d = nse_decode(r)

    issued_size = (d.get('securityInfo') or {}).get('issuedSize')
    trade_info  = (d.get('marketDeptOrderBook') or {}).get('tradeInfo') or {}
    ffmc        = trade_info.get('ffmc')
    total_mcap  = trade_info.get('totalMarketCap')

    ff_factor = None
    if ffmc is not None and total_mcap and float(total_mcap) > 0:
        ff_factor = round(float(ffmc) / float(total_mcap), 6)

    return issued_size, ff_factor, ffmc, total_mcap

def main():
    conn = sqlite3.connect(DB_PATH)
    s = make_session()
    warm_session(s)

    print(f"{'Symbol':<12}  {'Issued Size':>16}  {'FF Factor':>10}  {'FFMC (Cr)':>12}  {'Total MCap (Cr)':>16}  {'FF MCap (Cr)':>12}")
    print("-" * 85)
    for sym in TEST_SYMBOLS:
        result = fetch_quote(s, sym)
        issued_size, ff_factor, ffmc, total_mcap = result

        # Look up existing DB values for comparison
        row = conn.execute("SELECT issued_size, ff_factor, ff_factor_date FROM stock_metadata WHERE symbol=?", (sym,)).fetchone()
        db_issued, db_ff, db_ff_date = row if row else (None, None, None)

        issued_str = f"{issued_size:,}" if issued_size else "N/A"
        ff_str = f"{ff_factor:.4f}" if ff_factor else ("none (after-hours?)" if issued_size else "FAILED")
        ffmc_str = f"{float(ffmc):,.0f}" if ffmc else "—"
        total_str = f"{float(total_mcap):,.0f}" if total_mcap else "—"

        # Compute FF MCap in Cr using live issued_size × close
        latest = conn.execute("SELECT close FROM daily_bhavcopy WHERE symbol=? ORDER BY date DESC LIMIT 1", (sym,)).fetchone()
        close = latest[0] if latest else None
        ff_mcap = None
        if issued_size and ff_factor and close:
            ff_mcap = issued_size * ff_factor * close / 1e7

        print(f"{sym:<12}  {issued_str:>16}  {ff_str:>10}  {ffmc_str:>12}  {total_str:>16}  {'₹' + f'{ff_mcap:,.2f}' if ff_mcap else '—':>12}")
        print(f"{'  DB was:':<12}  {'issued='+str(db_issued) if db_issued else 'N/A':>16}  {'ff='+str(db_ff) if db_ff else 'N/A':>10}  {'date='+str(db_ff_date) if db_ff_date else '':>12}")
        print()
        time.sleep(0.5)

    conn.close()
    print("\n--- Test complete. If ff_factor shows values, run full update with: ---")
    print("  .venv\\Scripts\\python.exe src\\fetch_mcap.py --force")

if __name__ == '__main__':
    main()

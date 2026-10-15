"""Quick test of NSE fetch for specific symbols."""
import sys
sys.path.insert(0, 'src')
from fetch_mcap import make_session, warm_session, fetch_quote, init_mcap_table, upsert_mcap
import sqlite3, datetime

conn = sqlite3.connect('data/stock_data.db')
init_mcap_table(conn)

s = make_session()
warm_session(s)

date = '2026-02-20'

# test with known NSE symbols + the top-volume ones from DB
test_syms = [
    ('RELIANCE', 'INE002A01018'),
    ('HDFCBANK', 'INE040A01034'),
    ('IDEA', 'INE669E01016'),        # top volume in DB
    ('FILATFASH', 'INE185E01021'),   # top volume in DB
    ('EASEMYTRIP', 'INE07O001026'),  # top volume in DB
]

for sym, isin in test_syms:
    full, ff = fetch_quote(s, sym)
    print(f'{sym}: full_mcap={full}, ff_mcap={ff}')
    if full or ff:
        upsert_mcap(conn, date, sym, isin, full, ff)

rows = conn.execute('SELECT symbol, full_mcap_cr, ff_mcap_cr FROM stock_mcap').fetchall()
print(f'\nSaved {len(rows)} rows:')
for r in rows:
    print(f'  {r}')
conn.close()

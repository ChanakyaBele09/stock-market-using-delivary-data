"""init_stock_metadata.py — create stock_metadata table and populate with test data."""
import sqlite3, sys
sys.path.insert(0, 'src')
from fetch_mcap import init_tables

conn = sqlite3.connect('data/stock_data.db')
init_tables(conn)
print('Tables ready.')

# Populate with our 5 test symbols (issued_size from NSE API dump)
test_data = [
    ('RELIANCE',   'INE002A01018', 13532472634,  None),
    ('HDFCBANK',   'INE040A01034', 7617618918,   None),
    ('IDEA',       'INE669E01016', 275693760000,  None),
    ('FILATFASH',  'INE185E01021', 140699614,    None),
    ('EASEMYTRIP', 'INE07O001026', 1279999775,   None),
]

for sym, isin, issued, ff in test_data:
    conn.execute("""
        INSERT INTO stock_metadata
            (symbol, isin, issued_size, ff_factor, ff_factor_date, issued_date, updated_at)
        VALUES (?,?,?,?,NULL,'2026-02-20',datetime('now'))
        ON CONFLICT(symbol) DO UPDATE SET
            isin=excluded.isin, issued_size=excluded.issued_size,
            issued_date=excluded.issued_date, updated_at=excluded.updated_at
    """, (sym, isin, issued, ff))

conn.commit()
rows = conn.execute('SELECT symbol, issued_size, ff_factor FROM stock_metadata').fetchall()
print(f'stock_metadata rows: {len(rows)}')
for r in rows:
    print(f'  {r}')
conn.close()

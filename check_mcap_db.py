import sqlite3
conn = sqlite3.connect('data/stock_data.db')
syms = conn.execute(
    "SELECT symbol, isin FROM daily_bhavcopy WHERE date=? ORDER BY total_volume DESC LIMIT 5",
    ('2026-02-20',)
).fetchall()
print('Symbols found:', syms)
tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
print('Tables:', [t[0] for t in tables])
mcap_rows = conn.execute("SELECT COUNT(*) FROM stock_mcap").fetchone()
print('MCap rows:', mcap_rows[0])

"""
remap_sectors_v2.py — Remap sectors using NSE Code, BSE Code, AND ISIN matching.
"""
import sqlite3
import pandas as pd
import time
import os

DB_PATH = r'd:\Trading Workflows\data\stock_data.db'
SCREENER = r'd:\Trading Workflows\data\Screener Data.csv'

def main():
    t0 = time.time()

    # 1. Load Custom Mapping Data (Highest Priority)
    custom_map = {}
    if os.path.exists(r'd:\Trading Workflows\data\symbol_mapping.csv'):
        map_df = pd.read_csv(r'd:\Trading Workflows\data\symbol_mapping.csv')
        map_df.columns = map_df.columns.str.strip()
        
        # Build custom NSE map
        custom_nse = map_df[map_df['NSE Code'].notna() & map_df['Industry'].notna()].copy()
        custom_nse['symbol'] = custom_nse['NSE Code'].astype(str).str.strip().str.upper()
        custom_nse['sector'] = custom_nse['Industry'].astype(str).str.strip()
        custom_map.update(dict(zip(custom_nse['symbol'], custom_nse['sector'])))
        
        # Build custom ISIN map
        custom_isin = map_df[map_df['ISIN Code'].notna() & map_df['Industry'].notna()].copy()
        custom_isin['isin'] = custom_isin['ISIN Code'].astype(str).str.strip().str.upper()
        custom_isin['sector'] = custom_isin['Industry'].astype(str).str.strip()
        custom_isin_map_dict = dict(zip(custom_isin['isin'], custom_isin['sector']))
        
        # Build custom Name map
        custom_name = map_df[map_df['Name'].notna() & map_df['Industry'].notna()].copy()
        custom_name['name_upper'] = custom_name['Name'].astype(str).str.strip().str.upper()
        custom_name['sector'] = custom_name['Industry'].astype(str).str.strip()
        custom_name_map_dict = dict(zip(custom_name['name_upper'], custom_name['sector']))
        
        print(f"Loaded Custom Maps: NSE={len(custom_nse)}, ISIN={len(custom_isin)}, Name={len(custom_name)}")
    else:
        custom_isin_map_dict = {}
        custom_name_map_dict = {}

    # 1.5 Load Screener Data (Secondary Priority)
    try:
        sc = pd.read_csv(SCREENER)
        sc.columns = sc.columns.str.strip()

        # Build 3 mapping sources from Screener
        # A) NSE Code -> sector
        nse = sc[sc['NSE Code'].notna() & sc['Final Segrigation'].notna()].copy()
        nse['symbol'] = nse['NSE Code'].astype(str).str.strip().str.upper()
        nse['sector'] = nse['Final Segrigation'].astype(str).str.strip()
        nse_map = dict(zip(nse['symbol'], nse['sector']))
        print(f"Map A (NSE Code): {len(nse_map)} symbols")

        # B) ISIN Code -> sector
        isin = sc[sc['ISIN Code'].notna() & sc['Final Segrigation'].notna()].copy()
        isin['isin'] = isin['ISIN Code'].astype(str).str.strip().str.upper()
        isin['sector'] = isin['Final Segrigation'].astype(str).str.strip()
        isin_map = dict(zip(isin['isin'], isin['sector']))
        print(f"Map B (ISIN Code): {len(isin_map)} ISINs")

        # C) Name matching (fuzzy backup)
        name = sc[sc['Name'].notna() & sc['Final Segrigation'].notna()].copy()
        name['name_upper'] = name['Name'].astype(str).str.strip().str.upper()
        name['sector'] = name['Final Segrigation'].astype(str).str.strip()
        name_map = dict(zip(name['name_upper'], name['sector']))
        print(f"Map C (Name): {len(name_map)} names")
    except Exception as e:
        print(f"Skipped Screener Data: {e}")
        nse_map, isin_map, name_map = {}, {}, {}

    # 2. Connect to DB
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA synchronous = NORMAL")

    # 3. Get all distinct (symbol, isin) from DB
    all_symbols = pd.read_sql(
        "SELECT DISTINCT symbol, isin FROM daily_bhavcopy",
        conn
    )
    print(f"\nDB has {len(all_symbols)} distinct symbols")

    # 4. Map each symbol using priority: Custom Mapping > Screener NSE > ISIN > Name
    symbol_sector = {}
    matched_custom = matched_nse = matched_isin = matched_name = unmatched = 0

    for _, row in all_symbols.iterrows():
        sym = str(row['symbol']).strip().upper()
        isin_val = str(row['isin']).strip().upper() if pd.notna(row['isin']) else ''

        if sym in custom_map:
            symbol_sector[sym] = custom_map[sym]
            matched_custom += 1
        elif isin_val in custom_isin_map_dict:
            symbol_sector[sym] = custom_isin_map_dict[isin_val]
            matched_custom += 1
        elif sym in custom_name_map_dict:
            symbol_sector[sym] = custom_name_map_dict[sym]
            matched_custom += 1
        elif sym in nse_map:
            symbol_sector[sym] = nse_map[sym]
            matched_nse += 1
        elif isin_val in isin_map:
            symbol_sector[sym] = isin_map[isin_val]
            matched_isin += 1
        elif sym in name_map:
            symbol_sector[sym] = name_map[sym]
            matched_name += 1
        else:
            symbol_sector[sym] = 'Unknown'
            unmatched += 1

    print(f"  Matched via Custom CSV: {matched_custom}")

    print(f"  Matched via NSE Code: {matched_nse}")
    print(f"  Matched via ISIN:     {matched_isin}")
    print(f"  Matched via Name:     {matched_name}")
    print(f"  Unmatched:            {unmatched}")

    # 5. Load into temp table and batch update
    conn.execute("DROP TABLE IF EXISTS _sector_map")
    conn.execute("CREATE TABLE _sector_map (symbol TEXT PRIMARY KEY, sector TEXT)")
    conn.executemany(
        "INSERT INTO _sector_map (symbol, sector) VALUES (?, ?)",
        list(symbol_sector.items())
    )
    conn.commit()

    # 6. Single batch UPDATE
    conn.execute("""
        UPDATE daily_bhavcopy SET sector = (
            SELECT m.sector FROM _sector_map m 
            WHERE m.symbol = UPPER(daily_bhavcopy.symbol)
        )
    """)
    conn.commit()
    print(f"\nBatch UPDATE done")

    # 7. Stats
    latest = conn.execute("SELECT MAX(date) FROM daily_bhavcopy").fetchone()[0]
    total = conn.execute("SELECT COUNT(DISTINCT symbol) FROM daily_bhavcopy WHERE date=?", (latest,)).fetchone()[0]
    mapped = conn.execute("SELECT COUNT(DISTINCT symbol) FROM daily_bhavcopy WHERE date=? AND sector != 'Unknown'", (latest,)).fetchone()[0]
    print(f"\nLatest date: {latest}")
    print(f"Total stocks: {total}")
    print(f"Mapped:       {mapped}")
    print(f"Unknown:      {total - mapped}")

    print("\nTop 15 sectors:")
    rows = conn.execute("""
        SELECT sector, COUNT(DISTINCT symbol) as cnt 
        FROM daily_bhavcopy WHERE date=?
        GROUP BY sector ORDER BY cnt DESC LIMIT 15
    """, (latest,)).fetchall()
    for sector, cnt in rows:
        print(f"  {cnt:4d}  {sector}")

    # Cleanup
    conn.execute("DROP TABLE IF EXISTS _sector_map")
    conn.commit()
    conn.close()
    print(f"\nDone in {time.time()-t0:.1f}s")

if __name__ == '__main__':
    main()

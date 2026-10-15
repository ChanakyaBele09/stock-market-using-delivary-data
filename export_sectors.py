import sqlite3
import pandas as pd

def export():
    conn = sqlite3.connect('src/data/market.db')
    # Get the most recent mapping
    df = pd.read_sql("""
        SELECT symbol, sector 
        FROM daily_bhavcopy 
        WHERE date = (SELECT MAX(date) FROM daily_bhavcopy)
        ORDER BY sector ASC, symbol ASC
    """, conn)
    conn.close()
    
    output_file = "stock_sector_mapping.csv"
    df.to_csv(output_file, index=False)
    print(f"Exported {len(df)} rows to {output_file}")

if __name__ == '__main__':
    export()

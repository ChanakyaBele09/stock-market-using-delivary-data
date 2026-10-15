import sqlite3
import os

DB_PATH = os.path.join('data', 'stock_data.db')

def migrate():
    conn = sqlite3.connect(DB_PATH)
    try:
        # Add bse_scrip_code
        try:
            conn.execute("ALTER TABLE stock_metadata ADD COLUMN bse_scrip_code TEXT")
            print("Added bse_scrip_code column.")
        except sqlite3.OperationalError as e:
            print(f"bse_scrip_code: {e}")

        # Add bse_ff_factor
        try:
            conn.execute("ALTER TABLE stock_metadata ADD COLUMN bse_ff_factor REAL")
            print("Added bse_ff_factor column.")
        except sqlite3.OperationalError as e:
            print(f"bse_ff_factor: {e}")
        
        # Create index
        conn.execute("CREATE INDEX IF NOT EXISTS idx_meta_bse ON stock_metadata(bse_scrip_code)")
        print("Created index idx_meta_bse.")
        
        conn.commit()
    finally:
        conn.close()

if __name__ == '__main__':
    migrate()

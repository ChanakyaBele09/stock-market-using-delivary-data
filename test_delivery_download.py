import requests
import datetime
import pandas as pd
import io

def test_nse_delivery(date):
    date_str = date.strftime('%d%m%Y')
    # URL: https://nsearchives.nseindia.com/products/content/sec_bhavdata_full_18022026.csv
    url = f"https://nsearchives.nseindia.com/products/content/sec_bhavdata_full_{date_str}.csv"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    }
    
    print(f"Testing NSE Delivery URL: {url}")
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            print("NSE Success!")
            df = pd.read_csv(io.StringIO(response.text))
            print("Columns:", df.columns.tolist())
            print(df.head(2))
            return df
        else:
            print(f"NSE Failed with status code: {response.status_code}")
    except Exception as e:
        print(f"NSE Error: {e}")

def test_bse_delivery(date):
    # Year YYYY
    year = date.strftime('%Y')
    # Date DDMM
    ddmm = date.strftime('%d%m')
    
    # URL: https://www.bseindia.com/BSEDATA/gross/2026/SCBSEALL1802.TXT
    url = f"https://www.bseindia.com/BSEDATA/gross/{year}/SCBSEALL{ddmm}.TXT"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    }
    
    print(f"Testing BSE Delivery URL: {url}")
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            print("BSE Download Success!")
            # Determine separator (usually |)
            content = response.text
            df = pd.read_csv(io.StringIO(content), sep='|')
            print("BSE Columns:", df.columns.tolist())
            print(df.head(2))
            return df
        else:
            print(f"BSE Failed with status code: {response.status_code}")
    except Exception as e:
        print(f"BSE Error: {e}")

if __name__ == "__main__":
    # Test for 2026-02-18
    date = datetime.datetime(2026, 2, 18)
    print(f"Testing for date: {date.date()}")
    print("-" * 20)
    test_nse_delivery(date)
    print("-" * 20)
    test_bse_delivery(date)

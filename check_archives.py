import requests, datetime, time

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': '*/*',
    'Referer': 'https://www.nseindia.com/'
})
session.get('https://www.nseindia.com', timeout=10)
time.sleep(1)

print('=== NSE sec_bhavdata_full availability ===')
test_dates = [
    datetime.date(2026, 2, 19),
    datetime.date(2025, 12, 31),
    datetime.date(2025, 9, 30),
    datetime.date(2025, 6, 30),
    datetime.date(2025, 3, 31),
    datetime.date(2024, 12, 31),
    datetime.date(2024, 9, 30),
    datetime.date(2024, 6, 28),
    datetime.date(2024, 3, 28),
]
for d in test_dates:
    ds = d.strftime('%d%m%Y')
    url = f'https://nsearchives.nseindia.com/products/content/sec_bhavdata_full_{ds}.csv'
    try:
        r = session.head(url, timeout=8, allow_redirects=True)
        size = r.headers.get('Content-Length', '?')
        print(f'  {d}: HTTP {r.status_code}  size={size}')
    except Exception as e:
        print(f'  {d}: ERROR {e}')
    time.sleep(0.5)

print()
print('=== BSE BhavCopy availability ===')
bse_sess = requests.Session()
bse_sess.headers.update({'User-Agent': 'Mozilla/5.0'})
bse_sess.get('https://www.bseindia.com', timeout=10)
time.sleep(1)

bse_dates = [
    datetime.date(2026, 2, 19),
    datetime.date(2025, 12, 31),
    datetime.date(2025, 9, 30),
    datetime.date(2025, 6, 30),
    datetime.date(2025, 3, 31),
    datetime.date(2024, 12, 31),
    datetime.date(2024, 9, 30),
]
for d in bse_dates:
    ymd = d.strftime('%Y%m%d')
    url = f'https://www.bseindia.com/download/BhavCopy/Equity/BhavCopy_BSE_CM_0_0_0_{ymd}_F_0000.CSV'
    try:
        r = bse_sess.head(url, timeout=8, allow_redirects=True)
        print(f'  {d}: HTTP {r.status_code}')
    except Exception as e:
        print(f'  {d}: ERROR {e}')
    time.sleep(0.5)

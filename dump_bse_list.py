"""Dump all fields from BSE bulk list and check for FF MCap."""
import requests, json

bse = requests.Session()
bse.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120',
    'Referer': 'https://www.bseindia.com/',
    'Accept': 'application/json',
})

url = 'https://api.bseindia.com/BseIndiaAPI/api/ListofScripData/w?Group=&Scripcode=&shname=&PSindustry=&segment=Equity&status=Active'
r = bse.get(url, timeout=20)
d = r.json()

print(f'Type: {type(d).__name__}')
if isinstance(d, list):
    print(f'Total records: {len(d)}')
    print(f'All keys in record[0]: {list(d[0].keys())}')
    print()
    # Print 5 samples
    for item in d[:5]:
        print(item)
    print()
    # Search for any FF-related fields across ALL keys
    all_keys = set()
    for row in d:
        all_keys.update(row.keys())
    print(f'All unique keys: {sorted(all_keys)}')
    # Save to file
    with open('bse_scrip_list.json', 'w') as f:
        json.dump(d[:20], f, indent=2)  # first 20 only for inspection
    print('\nSaved first 20 to bse_scrip_list.json')
elif isinstance(d, dict):
    print(f'Keys: {list(d.keys())}')
    # usually wraps in a key
    for k, v in d.items():
        if isinstance(v, list) and v:
            print(f'  {k}: list[{len(v)}], sample keys: {list(v[0].keys())}')
            all_keys = set()
            for row in v:
                all_keys.update(row.keys())
            print(f'  All keys: {sorted(all_keys)}')
            for item in v[:3]:
                print(f'  {item}')

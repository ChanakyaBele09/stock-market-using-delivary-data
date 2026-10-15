import pandas as pd

df = pd.read_csv('data/processed_data_2026-02-19.csv')
total = len(df)
known = len(df[df['SECTOR'] != 'Unknown'])
print(f'Overall: {known}/{total} = {round(100*known/total,1)}% known')

nse_df = df[df['Source'] == 'NSE']
bse_df = df[df['Source'] == 'BSE']
nse_known = len(nse_df[nse_df['SECTOR'] != 'Unknown'])
bse_known = len(bse_df[bse_df['SECTOR'] != 'Unknown'])
print(f'NSE known: {nse_known}/{len(nse_df)} = {round(100*nse_known/len(nse_df),1)}%')
print(f'BSE known: {bse_known}/{len(bse_df)} = {round(100*bse_known/len(bse_df),1)}%')

# Check Screener Data columns for BSE mapping
sc = pd.read_csv('data/Screener Data.csv')
print(f'\nScreener columns: {sc.columns.tolist()}')
print(f'Screener BSE-only stocks (no NSE code): {len(sc[sc["NSE Code"].isna()])}')
print(sc[sc['NSE Code'].isna()][['Name','BSE Code','Industry']].head(5))

import pandas as pd
from pytickersymbols import PyTickerSymbols

stock_data = PyTickerSymbols()
print(stock_data)



indexes = stock_data.get_all_indices()
#indexes = ['DOW JONES', 'S&P 100', 'S&P 500', 'DAX', 'NASDAQ 100']
indexes.sort()
print(indexes)

# Initialize an empty DataFrame
df = pd.DataFrame()

# Iterate over the indexes and append the data to df
for i in indexes:
    df_temp = pd.DataFrame(stock_data.get_stocks_by_index(i))
    df_temp['index'] = i
    df = pd.concat([df, df_temp], ignore_index=True)
    df['symbol'] = df['symbol'].fillna('NAN')
main_df = df[['symbol', 'name', 'country', 'index', 'industries', 'metadata']]
main_df = main_df.join(pd.DataFrame(main_df['metadata'].tolist()))
main_df = main_df.drop(columns=['metadata'])


df_symbols = main_df[['symbol', 'name', 'country', 'index', 'founded', 'employees']]

df_symbols = df_symbols.assign(employees=pd.to_numeric(df_symbols['employees'], errors='coerce'))
df_symbols = df_symbols.assign(employees=df_symbols['employees'].map('{:,.0f}'.format))
df_symbols['employees'] = df_symbols['employees'].replace('nan', 'N/A')


df_symbols = df_symbols.rename(columns={
                                        'symbol': 'Symbol',
                                        'name': 'Company Name',
                                        'country': 'Country',
                                        'index': 'Stock Index',
                                        'founded': 'Year of Founded',
                                        'employees': '#Employees'})


df_industries = main_df.explode('industries')[['industries', 'symbol']]
df_industries['industries'] = df_industries['industries'].fillna('Unknown')
df_industries = df_industries.drop_duplicates().sort_values(by=['industries']).reset_index(drop=True)
df_industries = df_industries.rename(columns={
                                              'industries': 'Industries',
                                              'symbol': 'Symbol',
                                              'name': 'Company Name'})

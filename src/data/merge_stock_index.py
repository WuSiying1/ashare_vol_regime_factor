import pandas as pd

# 读取股票池
stock = pd.read_csv('../../data/processed/stock_pool.csv', parse_dates=['time'])

# 读取沪深300
index = pd.read_excel('../../data/raw/hs300_index.xlsx')
index['time'] = pd.to_datetime(index['time'])

# 排序
stock = stock.sort_values('time')
index = index.sort_values('time')

# 只保留共同交易日
df = pd.merge(
    stock,
    index[['time', 'close']],
    on='time',
    how='inner',
    suffixes=('_stock', '_index')
)

df.to_csv('../../data/processed/stock_index_merged.csv', index=False)

print('Merged data saved.')

# 计算日收益率
df['ret_stock'] = df['close_stock'].pct_change()
df['ret_index'] = df['close_index'].pct_change()

# 超额收益
df['ret_excess'] = df['ret_stock'] - df['ret_index']

# 去掉第一天的 NaN
df = df.dropna().reset_index(drop=True)

df.to_csv('../../data/processed/returns.csv', index=False)

print('Return data saved.')


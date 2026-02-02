import pandas as pd
import numpy as np

# 读取数据
df = pd.read_csv('../../data/processed/vol_regime.csv', parse_dates=['time'])

# 未来 1 日超额收益（最干净）
df['ret_excess_fwd_1'] = df['ret_excess'].shift(-1)
df = df.dropna().reset_index(drop=True)

# 只看 high / low
df = df[df['vol_regime'].isin(['high', 'low'])]

# 计算分组净值
nav = (
    df.groupby('vol_regime')['ret_excess_fwd_1']
    .apply(lambda x: (1 + x).cumprod())
)

nav = nav.reset_index()

nav.to_csv('../../data/processed/vol_regime_nav.csv', index=False)
print('Group NAV saved.')

# 用连续因子（vol_20），而不是 high/low 标签
df = pd.read_csv('../../data/processed/vol_regime.csv', parse_dates=['time'])

# 未来 1 日超额收益
df['ret_excess_fwd_1'] = df['ret_excess'].shift(-1)
df = df.dropna()

# IC
ic = df[['vol_20', 'ret_excess_fwd_1']].corr().iloc[0, 1]

print('IC:', ic)

df['year'] = df['time'].dt.year

ic_by_year = (
    df.groupby('year')
    .apply(lambda x: x[['vol_20', 'ret_excess_fwd_1']].corr().iloc[0, 1])
)

print(ic_by_year)

import pandas as pd
import numpy as np

# 读取收益率数据
df = pd.read_csv('../../data/processed/returns.csv', parse_dates=['time'])

# 滚动 20 日波动率（基于股票收益）
window = 20
df['vol_20'] = (
    df['ret_stock']
    .rolling(window)
    .std()
    * np.sqrt(252)
)

# 去掉前 window 天
df = df.dropna().reset_index(drop=True)

df.to_csv('../../data/processed/vol_with_return.csv', index=False)

print('Volatility computed.')

# 计算分位点
high_q = df['vol_20'].quantile(0.7)
low_q = df['vol_20'].quantile(0.3)

def vol_regime(vol):
    if vol >= high_q:
        return 'high'
    elif vol <= low_q:
        return 'low'
    else:
        return 'mid'

df['vol_regime'] = df['vol_20'].apply(vol_regime)

df.to_csv('../../data/processed/vol_regime.csv', index=False)

print('Volatility regime labeled.')

# 未来 5 日超额收益
df['ret_excess_fwd_5'] = (
    df['ret_excess']
    .shift(-5)
)

# 按波动率状态分组
summary = (
    df.groupby('vol_regime')['ret_excess_fwd_5']
    .mean()
)

print(summary)

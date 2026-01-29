import pandas as pd

# ======================
# 1. 读取原始 Excel 数据
# ======================
raw_path = '../../data/raw/600519_maotai_adj.xlsx'
df = pd.read_excel(raw_path)


# 转换日期格式
df['time'] = pd.to_datetime(df['time'])

# ======================
# 3. 排序（时间序列研究的硬性要求）
# ======================
df = df.sort_values('time').reset_index(drop=True)

# ======================
# 4. 剔除异常交易日
# ======================
# 剔除停牌（成交量为 0）
df = df[df['volume'] > 0]

# 剔除 ST（如果有）
df = df[~df['thscode'].str.contains('ST', na=False)]

# ======================
# 5. 缺失值处理
# ======================
df = df.fillna(method='ffill')

# ======================
# 6. 保留核心字段（非常重要）
# ======================
df = df[
    ['time', 'open', 'high', 'low', 'close', 'volume', 'amount', 'thscode']
]

# ======================
# 7. 保存为 processed 数据
# ======================
save_path = '../../data/processed/600519_maotai_cleaned.csv'
df.to_csv(save_path, index=False)

print('Cleaned stock data saved:', save_path)

# ======================
# Step 3: 生成股票池
# ======================

# 假设 df 是已经清洗完成后的 DataFrame
# 包含字段：number, time, open, high, low, close, volume, amount, thscode

# 1. 上市时间 > 120 个交易日
stock_pool = df.groupby('thscode').filter(
    lambda x: len(x) > 120
)

# 2. 日均成交量 > 50 万股
stock_pool = stock_pool.groupby('thscode').filter(
    lambda x: x['volume'].mean() > 5e5
)

# 3. 保存股票池
save_path = '../../data/processed/stock_pool.csv'
stock_pool.to_csv(save_path, index=False)

print('Stock pool saved:', save_path)


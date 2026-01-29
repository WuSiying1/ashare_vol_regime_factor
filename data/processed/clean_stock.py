import pandas as pd

# ======================
# 1. 读取原始 Excel 数据
# ======================
raw_path = '../../data/raw/600519_maotai_adj.xlsx'
df = pd.read_excel(raw_path)

# ======================
# 2. 字段重命名（统一研究规范）
# ======================
df = df.rename(columns={
    'time': 'date',
    'thscode': 'code'
})

# 转换日期格式
df['date'] = pd.to_datetime(df['date'])

# ======================
# 3. 排序（时间序列研究的硬性要求）
# ======================
df = df.sort_values('date').reset_index(drop=True)

# ======================
# 4. 剔除异常交易日
# ======================
# 剔除停牌（成交量为 0）
df = df[df['volume'] > 0]

# 剔除 ST（如果有）
df = df[~df['code'].str.contains('ST', na=False)]

# ======================
# 5. 缺失值处理
# ======================
df = df.fillna(method='ffill')

# ======================
# 6. 保留核心字段（非常重要）
# ======================
df = df[
    ['date', 'open', 'high', 'low', 'close', 'volume', 'amount', 'code']
]

# ======================
# 7. 保存为 processed 数据
# ======================
save_path = '../../data/processed/600519_maotai_cleaned.csv'
df.to_csv(save_path, index=False)

print('Cleaned stock data saved:', save_path)

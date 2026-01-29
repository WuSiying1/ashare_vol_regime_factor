## Day 1

Initialized project structure and defined research scope.

## Day 2

今天完成了：
- 清洗股票日线数据（剔除停牌/ST股、缺失值处理）
- 生成股票池（上市 > 120 日，成交量 > 50 万股）
- 数据保存到 data/processed/

遇到问题：
- 初次处理 CSV 路径容易写错
- volume=0 判定停牌时注意复权前后差异

## Day 3

使用后复权贵州茅台，计算日收益率并以沪深300作为 benchmark，得到超额收益序列，为后续 alpha/因子研究提供基础

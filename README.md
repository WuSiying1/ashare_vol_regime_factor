# ashare_vol_regime_factor
Regime-dependent multi-factor research in China A-share market

project structure

ashare_vol_regime_factor/
│
├── data/
│   ├── raw/          # 原始数据（不动）
│   ├── processed/    # 清洗后的数据
│
├── src/
│   ├── data/         # 数据清洗、股票池
│   ├── factors/      # 因子构造
│   ├── backtest/     # 回测逻辑
│   └── utils/        # 通用函数
│
├── research/
│   ├── notes.md      # 每天研究记录
│   └── figures/
│
├── results/
│   ├── tables/
│   └── plots/
│
└── README.md

# A股波动率状态下的多因子研究

本项目研究A股市场中，不同市场波动率状态下，
常见股票因子的有效性差异，并构建状态自适应的多因子投资策略。

当前进度：
- Day 1：项目结构与研究问题定义

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd  


def _ensure_columns(df: pd.DataFrame, required: Iterable[str]) -> None:
    missing = [column for column in required if column not in df.columns]
    if missing:
        raise ValueError(f'Missing required columns: {missing}')


def load_returns(returns_path: Path) -> pd.DataFrame:
    df = pd.read_csv(returns_path, parse_dates=['time'])
    _ensure_columns(df, ['time', 'ret_stock', 'ret_excess'])
    return df.sort_values('time').reset_index(drop=True)


def compute_rolling_vol(
    df: pd.DataFrame,
    window: int,
    annualization_factor: float = np.sqrt(252),
) -> pd.DataFrame:
    df = df.copy()
    df['vol_20'] = (
        df['ret_stock']
        .rolling(window=window, min_periods=window)
        .std()
        * annualization_factor
    )
    return df.dropna(subset=['vol_20']).reset_index(drop=True)


def label_volatility_regime(
    df: pd.DataFrame,
    low_quantile: float,
    high_quantile: float,
) -> pd.DataFrame:
    df = df.copy()
    low_q = df['vol_20'].quantile(low_quantile)
    high_q = df['vol_20'].quantile(high_quantile)

    def classify(vol: float) -> str:
        if vol >= high_q:
            return 'high'
        if vol <= low_q:
            return 'low'
        return 'mid'

    df['vol_regime'] = df['vol_20'].apply(classify)
    return df


def compute_forward_returns(df: pd.DataFrame, horizon: int) -> pd.DataFrame:
    df = df.copy()
    df['ret_excess_fwd_5'] = df['ret_excess'].shift(-horizon)
    return df


def save_dataframe(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    print(f'Saved: {path}')


def summarize_by_regime(df: pd.DataFrame) -> pd.Series:
    _ensure_columns(df, ['vol_regime', 'ret_excess_fwd_5'])
    return df.groupby('vol_regime')['ret_excess_fwd_5'].mean()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description='Compute volatility regimes based on rolling stock returns.'
    )

    project_root = Path(__file__).resolve().parents[2]
    default_returns = project_root / 'data' / 'processed' / 'returns.csv'
    default_vol = project_root / 'data' / 'processed' / 'vol_with_return.csv'
    default_regime = project_root / 'data' / 'processed' / 'vol_regime.csv'

    parser.add_argument(
        '--returns-path',
        type=Path,
        default=default_returns,
        help='Input path for returns CSV.',
    )
    parser.add_argument(
        '--vol-path',
        type=Path,
        default=default_vol,
        help='Output path for intermediate volatility CSV.',
    )
    parser.add_argument(
        '--regime-path',
        type=Path,
        default=default_regime,
        help='Output path for volatility regime CSV.',
    )
    parser.add_argument(
        '--window',
        type=int,
        default=20,
        help='Rolling window length in trading days.',
    )
    parser.add_argument(
        '--horizon',
        type=int,
        default=5,
        help='Forward return horizon in trading days.',
    )
    parser.add_argument(
        '--low-quantile',
        type=float,
        default=0.3,
        help='Lower quantile threshold for volatility regime.',
    )
    parser.add_argument(
        '--high-quantile',
        type=float,
        default=0.7,
        help='Upper quantile threshold for volatility regime.',
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if not args.returns_path.exists():
        raise FileNotFoundError(f'Returns file not found: {args.returns_path}')

    returns = load_returns(args.returns_path)
    vol = compute_rolling_vol(returns, args.window)
    save_dataframe(vol, args.vol_path)

    labeled = label_volatility_regime(
        vol,
        low_quantile=args.low_quantile,
        high_quantile=args.high_quantile,
    )
    labeled = compute_forward_returns(labeled, args.horizon)
    save_dataframe(labeled, args.regime_path)

    summary = summarize_by_regime(labeled)
    print('Mean forward excess returns by volatility regime:')
    print(summary)


if __name__ == '__main__':
    main()

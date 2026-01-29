from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable

import pandas as pd


def _ensure_columns(df: pd.DataFrame, required: Iterable[str]) -> None:
    missing = [column for column in required if column not in df.columns]
    if missing:
        raise ValueError(f'Missing required columns: {missing}')


def load_stock(stock_path: Path) -> pd.DataFrame:
    stock = pd.read_csv(stock_path, parse_dates=['time'])
    _ensure_columns(stock, ['time', 'close'])
    return stock.sort_values('time').reset_index(drop=True)


def load_index(index_path: Path) -> pd.DataFrame:
    index = pd.read_excel(index_path)
    _ensure_columns(index, ['time', 'close'])
    index['time'] = pd.to_datetime(index['time'])
    return index.sort_values('time').reset_index(drop=True)


def merge_stock_index(stock: pd.DataFrame, index: pd.DataFrame) -> pd.DataFrame:
    merged = pd.merge(
        stock,
        index[['time', 'close']],
        on='time',
        how='inner',
        suffixes=('_stock', '_index'),
    )
    return merged.sort_values('time').reset_index(drop=True)


def compute_returns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    _ensure_columns(df, ['close_stock', 'close_index'])
    df['ret_stock'] = df['close_stock'].pct_change()
    df['ret_index'] = df['close_index'].pct_change()
    df['ret_excess'] = df['ret_stock'] - df['ret_index']
    return df.dropna().reset_index(drop=True)


def save_dataframe(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    print(f'Saved: {path}')


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description='Merge stock data with index and compute returns.'
    )

    project_root = Path(__file__).resolve().parents[2]
    default_stock = project_root / 'data' / 'processed' / 'stock_pool.csv'
    default_index = project_root / 'data' / 'raw' / 'hs300_index.xlsx'
    default_merged = project_root / 'data' / 'processed' / 'stock_index_merged.csv'
    default_returns = project_root / 'data' / 'processed' / 'returns.csv'

    parser.add_argument(
        '--stock-path',
        type=Path,
        default=default_stock,
        help='Path to the processed stock CSV file.',
    )
    parser.add_argument(
        '--index-path',
        type=Path,
        default=default_index,
        help='Path to the raw index Excel file.',
    )
    parser.add_argument(
        '--merged-path',
        type=Path,
        default=default_merged,
        help='Output path for the merged CSV file.',
    )
    parser.add_argument(
        '--returns-path',
        type=Path,
        default=default_returns,
        help='Output path for the returns CSV file.',
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if not args.stock_path.exists():
        raise FileNotFoundError(f'Stock file not found: {args.stock_path}')
    if not args.index_path.exists():
        raise FileNotFoundError(f'Index file not found: {args.index_path}')

    stock = load_stock(args.stock_path)
    index = load_index(args.index_path)

    merged = merge_stock_index(stock, index)
    save_dataframe(merged, args.merged_path)

    returns = compute_returns(merged)
    save_dataframe(returns, args.returns_path)


if __name__ == '__main__':
    main()


from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable

import pandas as pd


def _ensure_columns(df: pd.DataFrame, required: Iterable[str]) -> None:
	missing = [column for column in required if column not in df.columns]
	if missing:
		raise ValueError(f"Missing required columns: {missing}")


def clean_stock_data(raw_path: Path, cleaned_path: Path) -> pd.DataFrame:
	df = pd.read_excel(raw_path)

	_ensure_columns(
		df,
		[
			'time',
			'open',
			'high',
			'low',
			'close',
			'volume',
			'amount',
			'thscode',
		],
	)

	df['time'] = pd.to_datetime(df['time'])
	df = df.sort_values('time').reset_index(drop=True)
	df = df[df['volume'] > 0]
	df = df[~df['thscode'].str.contains('ST', na=False)]
	df = df.fillna(method='ffill')
	df = df[
		['time', 'open', 'high', 'low', 'close', 'volume', 'amount', 'thscode']
	]

	cleaned_path.parent.mkdir(parents=True, exist_ok=True)
	df.to_csv(cleaned_path, index=False)

	print(f'Cleaned stock data saved: {cleaned_path}')
	return df


def build_stock_pool(
	df: pd.DataFrame,
	pool_path: Path,
	min_history: int = 120,
	min_avg_volume: float = 5e5,
) -> pd.DataFrame:
	_ensure_columns(df, ['thscode', 'volume'])

	pool = df.groupby('thscode').filter(lambda group: len(group) > min_history)
	pool = pool.groupby('thscode').filter(
		lambda group: group['volume'].mean() > min_avg_volume
	)

	pool_path.parent.mkdir(parents=True, exist_ok=True)
	pool.to_csv(pool_path, index=False)

	print(f'Stock pool saved: {pool_path}')
	return pool


def parse_args() -> argparse.Namespace:
	parser = argparse.ArgumentParser(
		description='Clean raw stock data and generate a stock pool.'
	)

	project_root = Path(__file__).resolve().parents[2]
	default_raw = project_root / 'data' / 'raw' / '600519_maotai_adj.xlsx'
	default_cleaned = project_root / 'data' / 'processed' / '600519_maotai_cleaned.csv'
	default_pool = project_root / 'data' / 'processed' / 'stock_pool.csv'

	parser.add_argument(
		'--raw-path',
		type=Path,
		default=default_raw,
		help='Path to the raw Excel file.',
	)
	parser.add_argument(
		'--cleaned-path',
		type=Path,
		default=default_cleaned,
		help='Output path for the cleaned CSV file.',
	)
	parser.add_argument(
		'--pool-path',
		type=Path,
		default=default_pool,
		help='Output path for the stock pool CSV file.',
	)
	parser.add_argument(
		'--min-history',
		type=int,
		default=120,
		help='Minimum trading days since listing.',
	)
	parser.add_argument(
		'--min-avg-volume',
		type=float,
		default=5e5,
		help='Minimum average daily volume.',
	)

	return parser.parse_args()


def main() -> None:
	args = parse_args()

	if not args.raw_path.exists():
		raise FileNotFoundError(f'Raw file not found: {args.raw_path}')

	cleaned_df = clean_stock_data(args.raw_path, args.cleaned_path)
	build_stock_pool(
		cleaned_df,
		args.pool_path,
		min_history=args.min_history,
		min_avg_volume=args.min_avg_volume,
	)


if __name__ == '__main__':
	main()

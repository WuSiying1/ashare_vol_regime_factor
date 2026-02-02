from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable, Sequence

import pandas as pd


def _ensure_columns(df: pd.DataFrame, required: Iterable[str]) -> None:
    missing = [column for column in required if column not in df.columns]
    if missing:
        raise ValueError(f'Missing required columns: {missing}')


def load_vol_regime(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=['time'])
    _ensure_columns(df, ['time', 'vol_regime', 'ret_excess', 'vol_20'])
    return df.sort_values('time').reset_index(drop=True)


def add_forward_return(df: pd.DataFrame, horizon: int) -> pd.DataFrame:
    df = df.copy()
    column_name = f'ret_excess_fwd_{horizon}'
    df[column_name] = df['ret_excess'].shift(-horizon)
    return df.dropna(subset=[column_name]).reset_index(drop=True)


def compute_group_nav(
    df: pd.DataFrame,
    horizon: int,
    regimes: Sequence[str],
) -> pd.DataFrame:
    column_name = f'ret_excess_fwd_{horizon}'
    _ensure_columns(df, ['time', 'vol_regime', column_name])
    filtered = df[df['vol_regime'].isin(regimes)].copy()
    if filtered.empty:
        raise ValueError('No data available for specified regimes.')

    filtered['nav'] = (
        (1 + filtered[column_name])
        .groupby(filtered['vol_regime'])
        .cumprod()
    )

    nav = filtered.pivot(index='time', columns='vol_regime', values='nav')
    nav = nav.sort_index().reset_index()
    return nav


def compute_ic(df: pd.DataFrame, horizon: int) -> tuple[float, pd.Series]:
    column_name = f'ret_excess_fwd_{horizon}'
    _ensure_columns(df, ['vol_20', column_name, 'time'])

    ic = df[['vol_20', column_name]].corr().iloc[0, 1]

    by_year = (
        df.assign(year=df['time'].dt.year)
        .groupby('year')
        .apply(lambda x: x[['vol_20', column_name]].corr().iloc[0, 1])
    )

    return ic, by_year


def save_dataframe(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    print(f'Saved: {path}')


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description='Compute NAV by volatility regime and IC statistics.'
    )

    project_root = Path(__file__).resolve().parents[2]
    default_input = project_root / 'data' / 'processed' / 'vol_regime.csv'
    default_nav = project_root / 'data' / 'processed' / 'vol_regime_nav.csv'
    default_ic = project_root / 'data' / 'processed' / 'vol_ic_by_year.csv'

    parser.add_argument(
        '--input-path',
        type=Path,
        default=default_input,
        help='Path to the volatility regime CSV file.',
    )
    parser.add_argument(
        '--nav-path',
        type=Path,
        default=default_nav,
        help='Output path for regime NAV CSV.',
    )
    parser.add_argument(
        '--ic-path',
        type=Path,
        default=default_ic,
        help='Output path for yearly IC CSV.',
    )
    parser.add_argument(
        '--horizon',
        type=int,
        default=1,
        help='Forward return horizon in trading days.',
    )
    parser.add_argument(
        '--regimes',
        nargs='+',
        default=['high', 'low'],
        help='Regime labels to include in NAV calculation.',
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if not args.input_path.exists():
        raise FileNotFoundError(f'Input file not found: {args.input_path}')

    vol_regime = load_vol_regime(args.input_path)
    vol_regime = add_forward_return(vol_regime, args.horizon)

    nav = compute_group_nav(vol_regime, args.horizon, args.regimes)
    save_dataframe(nav, args.nav_path)

    ic, ic_by_year = compute_ic(vol_regime, args.horizon)
    save_dataframe(ic_by_year.reset_index(name='ic'), args.ic_path)

    print(f'Information Coefficient (overall): {ic:.6f}')
    print('Information Coefficient by year:')
    print(ic_by_year)


if __name__ == '__main__':
    main()

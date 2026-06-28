"""行情数据加载模块，支持 yfinance 期货/股票."""

from __future__ import annotations

import pandas as pd
import yfinance as yf

# yfinance interval -> (period 参数, 最大回溯说明)
INTERVAL_MAP = {
    "1m": ("7d", 7),
    "2m": ("60d", 60),
    "5m": ("60d", 60),
    "15m": ("60d", 60),
    "30m": ("60d", 60),
    "1h": ("730d", 730),
    "1d": ("2y", 730),
    "1wk": ("5y", 1825),
}

DEFAULT_SYMBOLS = {
    "ES": "ES=F",
    "MES": "MES=F",
    "NQ": "NQ=F",
    "CL": "CL=F",
    "GC": "GC=F",
}


def resolve_symbol(symbol: str) -> str:
    """将简称转为 yfinance ticker，如 ES -> ES=F."""
    upper = symbol.upper().strip()
    return DEFAULT_SYMBOLS.get(upper, symbol)


def load_ohlcv(
    symbol: str,
    interval: str = "5m",
    bars: int = 120,
) -> pd.DataFrame:
    """
    拉取 OHLCV 数据并标准化列名。

    Returns:
        DataFrame with columns: open, high, low, close, volume
    """
    ticker = resolve_symbol(symbol)
    if interval not in INTERVAL_MAP:
        raise ValueError(f"不支持的周期: {interval}，可选: {list(INTERVAL_MAP)}")

    period, _ = INTERVAL_MAP[interval]
    raw = yf.download(
        ticker,
        period=period,
        interval=interval,
        progress=False,
        auto_adjust=True,
    )

    if raw.empty:
        raise RuntimeError(f"无法获取 {ticker} 的数据，请检查品种名或网络")

    if isinstance(raw.columns, pd.MultiIndex):
        raw.columns = raw.columns.get_level_values(0)

    df = raw.rename(
        columns={
            "Open": "open",
            "High": "high",
            "Low": "low",
            "Close": "close",
            "Volume": "volume",
        }
    )
    df = df[["open", "high", "low", "close", "volume"]].dropna()
    df.index = pd.to_datetime(df.index)

    if len(df) > bars:
        df = df.iloc[-bars:]

    return df

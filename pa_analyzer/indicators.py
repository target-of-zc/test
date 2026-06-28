"""技术指标：EMA、ATR 等."""

from __future__ import annotations

import numpy as np
import pandas as pd


def ema(series: pd.Series, period: int = 20) -> pd.Series:
    return series.ewm(span=period, adjust=False).mean()


def atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    high, low, close = df["high"], df["low"], df["close"]
    prev_close = close.shift(1)
    tr = pd.concat(
        [
            high - low,
            (high - prev_close).abs(),
            (low - prev_close).abs(),
        ],
        axis=1,
    ).max(axis=1)
    return tr.ewm(span=period, adjust=False).mean()


def ema_slope(series: pd.Series, lookback: int = 3) -> pd.Series:
    """EMA 斜率（百分比变化）."""
    shifted = series.shift(lookback)
    return ((series - shifted) / shifted.replace(0, np.nan)) * 100


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["ema20"] = ema(out["close"], 20)
    out["atr14"] = atr(out, 14)
    out["ema20_slope"] = ema_slope(out["ema20"], 3)
    out["ema20_distance"] = ((out["close"] - out["ema20"]) / out["ema20"]) * 100
    return out

"""市场结构分析：摆动点、趋势、BOS/CHoCH，参考 mes-futures-trading-bot."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass
class SwingPoint:
    index: int
    timestamp: str
    price: float
    kind: str  # "high" | "low"


def find_swing_points(df: pd.DataFrame, left: int = 2, right: int = 2) -> list[SwingPoint]:
    """识别摆动高点/低点."""
    swings: list[SwingPoint] = []
    highs = df["high"].values
    lows = df["low"].values

    for i in range(left, len(df) - right):
        window_high = highs[i - left : i + right + 1]
        window_low = lows[i - left : i + right + 1]
        ts = str(df.index[i])

        if highs[i] == window_high.max():
            swings.append(SwingPoint(i, ts, float(highs[i]), "high"))
        if lows[i] == window_low.min():
            swings.append(SwingPoint(i, ts, float(lows[i]), "low"))

    return swings


def analyze_structure(df: pd.DataFrame) -> dict:
    """
    根据最近摆动点判断市场结构与突破事件。

    Returns:
        dict with trend, last_swing_high/low, events
    """
    swings = find_swing_points(df)
    highs = [s for s in swings if s.kind == "high"]
    lows = [s for s in swings if s.kind == "low"]

    result: dict = {
        "trend": "range",
        "last_swing_high": highs[-1].price if highs else None,
        "last_swing_low": lows[-1].price if lows else None,
        "events": [],
    }

    if len(highs) >= 2 and len(lows) >= 2:
        hh = highs[-1].price > highs[-2].price
        hl = lows[-1].price > lows[-2].price
        lh = highs[-1].price < highs[-2].price
        ll = lows[-1].price < lows[-2].price

        if hh and hl:
            result["trend"] = "uptrend"
        elif lh and ll:
            result["trend"] = "downtrend"

    close = float(df["close"].iloc[-1])
    if result["last_swing_high"] and close > result["last_swing_high"]:
        result["events"].append("bos_bullish")
    if result["last_swing_low"] and close < result["last_swing_low"]:
        result["events"].append("bos_bearish")

    # CHoCH：趋势中反向突破前摆动点
    if result["trend"] == "uptrend" and result["last_swing_low"]:
        if close < result["last_swing_low"]:
            result["events"].append("choch_bearish")
    if result["trend"] == "downtrend" and result["last_swing_high"]:
        if close > result["last_swing_high"]:
            result["events"].append("choch_bullish")

    return result

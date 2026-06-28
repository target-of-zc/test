"""K 线形态识别，参考 stolgo / PA_Agent."""

from __future__ import annotations

import pandas as pd


def classify_bar(row: pd.Series) -> str:
    """单根 K 线形态分类."""
    body_ratio = row.get("body_ratio", 0)
    upper = row.get("upper_wick_ratio", 0)
    lower = row.get("lower_wick_ratio", 0)
    direction = row.get("bar_direction", "bull")

    if body_ratio < 0.1:
        return "doji"
    if row.get("inside_bar"):
        streak = int(row.get("inside_streak", 0))
        if streak >= 2:
            return "iii" if streak >= 3 else "ii"
        return "inside_bar"
    if row.get("outside_bar"):
        return "outside_bar"

    if direction == "bull":
        if lower > 0.6 and body_ratio < 0.35:
            return "hammer"
        if body_ratio > 0.65:
            return "trend_bull"
        return "signal_bull"

    if upper > 0.6 and body_ratio < 0.35:
        return "shooting_star"
    if body_ratio > 0.65:
        return "trend_bear"
    return "signal_bear"


def detect_patterns(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["bar_type"] = out.apply(classify_bar, axis=1)

    # 吞没形态（双 K）
    out["pattern"] = "none"
    for i in range(1, len(out)):
        prev, cur = out.iloc[i - 1], out.iloc[i]
        if (
            prev["bar_direction"] == "bear"
            and cur["bar_direction"] == "bull"
            and cur["close"] > prev["open"]
            and cur["open"] < prev["close"]
        ):
            out.iat[i, out.columns.get_loc("pattern")] = "bullish_engulfing"
        elif (
            prev["bar_direction"] == "bull"
            and cur["bar_direction"] == "bear"
            and cur["close"] < prev["open"]
            and cur["open"] > prev["close"]
        ):
            out.iat[i, out.columns.get_loc("pattern")] = "bearish_engulfing"

    return out

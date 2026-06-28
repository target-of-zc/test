"""K 线几何特征，参考 PA_Agent / Al Brooks 风格."""

from __future__ import annotations

import pandas as pd


def _safe_ratio(num: pd.Series, den: pd.Series) -> pd.Series:
    return (num / den.replace(0, float("nan"))).fillna(0)


def add_bar_features(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    body = (out["close"] - out["open"]).abs()
    full_range = out["high"] - out["low"]
    upper_wick = out["high"] - out[["open", "close"]].max(axis=1)
    lower_wick = out[["open", "close"]].min(axis=1) - out["low"]

    out["body_ratio"] = _safe_ratio(body, full_range)
    out["upper_wick_ratio"] = _safe_ratio(upper_wick, full_range)
    out["lower_wick_ratio"] = _safe_ratio(lower_wick, full_range)
    out["close_position"] = _safe_ratio(
        out["close"] - out["low"], full_range
    )
    out["bar_direction"] = (out["close"] >= out["open"]).map(
        {True: "bull", False: "bear"}
    )

    # 内包 / 外包线
    prev_high = out["high"].shift(1)
    prev_low = out["low"].shift(1)
    out["inside_bar"] = (out["high"] <= prev_high) & (out["low"] >= prev_low)
    out["outside_bar"] = (out["high"] >= prev_high) & (out["low"] <= prev_low)

    # 连续内包计数 (ii / iii)
    inside = out["inside_bar"].astype(int)
    streak = inside.groupby((inside != inside.shift()).cumsum()).cumsum()
    out["inside_streak"] = streak * inside

    # 跳空
    out["gap"] = "none"
    out.loc[out["low"] > out["high"].shift(1), "gap"] = "gap_up"
    out.loc[out["high"] < out["low"].shift(1), "gap"] = "gap_down"

    return out

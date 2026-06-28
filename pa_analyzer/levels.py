"""支撑阻力关键位，参考 stolgo / mes-futures-trading-bot."""

from __future__ import annotations

import pandas as pd

from .structure import find_swing_points


def compute_levels(df: pd.DataFrame, tolerance_pct: float = 0.15) -> dict:
  """
  从摆动高低点聚类出支撑/阻力区。

  Args:
      tolerance_pct: 合并相近价位的百分比容差
  """
  swings = find_swing_points(df)
  if not swings:
    return {"support": [], "resistance": []}

  def cluster_prices(prices: list[float]) -> list[dict]:
    if not prices:
      return []
    prices = sorted(prices)
    clusters: list[list[float]] = [[prices[0]]]
    for p in prices[1:]:
      ref = clusters[-1][-1]
      if abs(p - ref) / ref * 100 <= tolerance_pct:
        clusters[-1].append(p)
      else:
        clusters.append([p])

    return [
      {
        "price": round(sum(c) / len(c), 2),
        "touches": len(c),
        "zone_low": round(min(c), 2),
        "zone_high": round(max(c), 2),
      }
      for c in clusters
    ]

  support_prices = [s.price for s in swings if s.kind == "low"]
  resistance_prices = [s.price for s in swings if s.kind == "high"]

  close = float(df["close"].iloc[-1])
  supports = cluster_prices(support_prices)
  resistances = cluster_prices(resistance_prices)

  # 标记当前价附近的关键位
  for level in supports + resistances:
    level["distance_pct"] = round(
      (close - level["price"]) / level["price"] * 100, 3
    )

  return {
    "support": sorted(supports, key=lambda x: abs(x["distance_pct"]))[:5],
    "resistance": sorted(resistances, key=lambda x: abs(x["distance_pct"]))[:5],
  }


def detect_breakout(df: pd.DataFrame, levels: dict) -> dict:
  """检测是否突破最近阻力/跌破支撑."""
  if len(df) < 2:
    return {"breakout": "none"}

  prev_close = float(df["close"].iloc[-2])
  cur_close = float(df["close"].iloc[-1])
  cur_high = float(df["high"].iloc[-1])
  cur_low = float(df["low"].iloc[-1])

  resistances = levels.get("resistance", [])
  supports = levels.get("support", [])

  result = {"breakout": "none", "detail": None}

  if resistances:
    r = resistances[0]["price"]
    if prev_close <= r < cur_close:
      result = {"breakout": "bullish", "detail": f"收盘突破阻力 {r}"}
    elif cur_high > r and cur_close < r:
      result = {"breakout": "failed_bullish", "detail": f"上探阻力 {r} 后回落"}

  if supports:
    s = supports[0]["price"]
    if prev_close >= s > cur_close:
      result = {"breakout": "bearish", "detail": f"收盘跌破支撑 {s}"}
    elif cur_low < s and cur_close > s:
      result = {"breakout": "failed_bearish", "detail": f"下探支撑 {s} 后反弹"}

  return result

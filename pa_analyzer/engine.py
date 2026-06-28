"""分析引擎：串联数据加载、特征、形态、结构."""

from __future__ import annotations

import json
from datetime import datetime, timezone

import pandas as pd

from .bar_features import add_bar_features
from .indicators import add_indicators
from .levels import compute_levels, detect_breakout
from .loader import load_ohlcv, resolve_symbol
from .patterns import detect_patterns
from .structure import analyze_structure


def run_analysis(
  symbol: str,
  interval: str = "5m",
  bars: int = 120,
) -> dict:
  """执行完整 PA 分析，返回结构化 JSON."""
  ticker = resolve_symbol(symbol)
  df = load_ohlcv(symbol, interval=interval, bars=bars)
  df = add_indicators(df)
  df = add_bar_features(df)
  df = detect_patterns(df)

  structure = analyze_structure(df)
  levels = compute_levels(df)
  breakout = detect_breakout(df, levels)

  last = df.iloc[-1]
  recent = df.tail(10)

  bar_summary = []
  for idx, row in recent.iterrows():
    bar_summary.append(
      {
        "time": str(idx),
        "open": round(float(row["open"]), 2),
        "high": round(float(row["high"]), 2),
        "low": round(float(row["low"]), 2),
        "close": round(float(row["close"]), 2),
        "bar_type": row["bar_type"],
        "pattern": row["pattern"],
        "inside_bar": bool(row["inside_bar"]),
        "gap": row["gap"],
      }
    )

  signal_hints = _build_signal_hints(last, structure, breakout, levels)

  return {
    "meta": {
      "symbol": symbol,
      "ticker": ticker,
      "interval": interval,
      "bars": len(df),
      "generated_at": datetime.now(timezone.utc).isoformat(),
      "disclaimer": "仅供研究学习，不构成投资建议",
    },
    "snapshot": {
      "close": round(float(last["close"]), 2),
      "ema20": round(float(last["ema20"]), 2),
      "atr14": round(float(last["atr14"]), 4),
      "ema20_slope": round(float(last["ema20_slope"]), 4),
      "ema20_distance_pct": round(float(last["ema20_distance"]), 4),
      "bar_type": last["bar_type"],
      "pattern": last["pattern"],
      "gap": last["gap"],
    },
    "structure": structure,
    "levels": levels,
    "breakout": breakout,
    "signal_hints": signal_hints,
    "recent_bars": bar_summary,
  }


def _build_signal_hints(
  last: pd.Series,
  structure: dict,
  breakout: dict,
  levels: dict,
) -> list[str]:
  """基于规则生成可量化的 PA 提示（非交易建议）."""
  hints: list[str] = []

  trend = structure.get("trend", "range")
  hints.append(f"当前结构趋势: {trend}")

  if last["inside_bar"]:
    hints.append("最新 K 线为内包线，等待突破方向")
  if int(last.get("inside_streak", 0)) >= 2:
    hints.append("连续内包 (ii/iii)，波动收缩，关注突破")

  if breakout["breakout"] != "none":
    hints.append(f"突破信号: {breakout['breakout']} - {breakout.get('detail', '')}")

  for event in structure.get("events", []):
    hints.append(f"结构事件: {event}")

  dist = float(last["ema20_distance"])
  if abs(dist) < 0.1:
    hints.append("价格贴近 EMA20，关注均线反应")
  elif dist > 0.3:
    hints.append("价格明显高于 EMA20，注意回调风险")
  elif dist < -0.3:
    hints.append("价格明显低于 EMA20，注意反弹可能")

  if levels.get("resistance"):
    r = levels["resistance"][0]
    hints.append(f"最近阻力: {r['price']} (距离 {r['distance_pct']}%)")
  if levels.get("support"):
    s = levels["support"][0]
    hints.append(f"最近支撑: {s['price']} (距离 {s['distance_pct']}%)")

  return hints


def to_json(result: dict, compact: bool = False) -> str:
  if compact:
    return json.dumps(result, ensure_ascii=False, separators=(",", ":"))
  return json.dumps(result, ensure_ascii=False, indent=2)

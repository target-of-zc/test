#!/usr/bin/env python3
"""Price Action Analyzer CLI - 价格行为分析命令行工具."""

from __future__ import annotations

import argparse
import json
import sys

from pa_analyzer.engine import run_analysis, to_json


def _print_report(result: dict) -> None:
    meta = result["meta"]
    snap = result["snapshot"]
    structure = result["structure"]

    print("=" * 50)
    print(f" PA Analyzer | {meta['symbol']} ({meta['ticker']})")
    print(f" 周期 {meta['interval']} | {meta['bars']} 根 K 线")
    print(f" {meta['disclaimer']}")
    print("=" * 50)

    print(f"\n最新价 {snap['close']}  EMA20 {snap['ema20']}  ATR14 {snap['atr14']}")
    print(f"K线类型: {snap['bar_type']}  形态: {snap['pattern']}  跳空: {snap['gap']}")
    print(f"\n市场结构 趋势: {structure['trend']}")
    if structure.get("events"):
        print(f"事件: {', '.join(structure['events'])}")

    levels = result["levels"]
    if levels.get("resistance"):
        print("\n阻力位:")
        for r in levels["resistance"][:3]:
            print(f"  {r['price']}  (触及 {r['touches']} 次, 距离 {r['distance_pct']}%)")
    if levels.get("support"):
        print("\n支撑位:")
        for s in levels["support"][:3]:
            print(f"  {s['price']}  (触及 {s['touches']} 次, 距离 {s['distance_pct']}%)")

    breakout = result["breakout"]
    if breakout["breakout"] != "none":
        print(f"\n突破: {breakout['detail']}")

    print("\nPA 提示:")
    for hint in result["signal_hints"]:
        print(f"  - {hint}")

    print("\n最近 10 根 K 线:")
    print(f"{'时间':<20} {'收盘':>8} {'类型':<14} {'形态'}")
    for bar in result["recent_bars"]:
        print(
            f"{bar['time'][:16]:<20} {bar['close']:>8} "
            f"{bar['bar_type']:<14} {bar['pattern']}"
        )


def cmd_analyze(args: argparse.Namespace) -> int:
    try:
        result = run_analysis(
            symbol=args.symbol,
            interval=args.interval,
            bars=args.bars,
        )
    except Exception as exc:
        print(f"分析失败: {exc}", file=sys.stderr)
        return 1

    if args.json:
        print(to_json(result, compact=args.compact))
    else:
        _print_report(result)
    return 0


def cmd_symbols(_: argparse.Namespace) -> int:
    from pa_analyzer.loader import DEFAULT_SYMBOLS

    print(f"{'简称':<8} yfinance Ticker")
    print("-" * 24)
    for k, v in DEFAULT_SYMBOLS.items():
        print(f"{k:<8} {v}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="价格行为 (Price Action) 分析工具 — 面向 ES/NQ 等期货",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_analyze = sub.add_parser("analyze", help="分析品种")
    p_analyze.add_argument("symbol", nargs="?", default="ES", help="品种，如 ES、NQ")
    p_analyze.add_argument("-i", "--interval", default="5m", help="K线周期")
    p_analyze.add_argument("-n", "--bars", type=int, default=120, help="K线数量")
    p_analyze.add_argument("--json", action="store_true", help="输出 JSON")
    p_analyze.add_argument("-c", "--compact", action="store_true", help="紧凑 JSON")
    p_analyze.set_defaults(func=cmd_analyze)

    p_symbols = sub.add_parser("symbols", help="列出内置品种")
    p_symbols.set_defaults(func=cmd_symbols)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())

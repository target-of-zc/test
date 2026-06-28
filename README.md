# PA Analyzer

面向 **ES / NQ / MES** 等市场的 **价格行为 (Price Action) 分析 CLI 工具**。

将 [PA_Agent](https://github.com/1997liuyh-boop/PA_Agent)、[stolgo](https://github.com/stockalgo/stolgo)、[mes-futures-trading-bot](https://github.com/chang-pro/mes-futures-trading-bot) 等主流项目的核心思路整合为可运行的 Python 工具：

- **K 线几何特征**：内包/外包、ii/iii、实体比、跳空（参考 PA_Agent / Al Brooks）
- **形态识别**：锤子线、吞没、十字星等（参考 stolgo）
- **市场结构**：摆动点、趋势、BOS / CHoCH（参考 mes-futures-trading-bot）
- **支撑阻力**：摆动高低点聚类关键位
- **结构化 JSON 输出**：便于接入 AI 或后续回测

> **免责声明**：本项目仅供学习与研究，不构成任何投资建议。实盘交易有风险。

## 安装

```bash
pip install -r requirements.txt
```

## 快速开始

```bash
# 分析 ES（E-mini 标普）5 分钟图
python main.py analyze ES

# 指定周期与 K 线数量
python main.py analyze ES -i 15m -n 200

# 输出 JSON（可对接 AI / 自动化）
python main.py analyze ES --json

# 查看内置品种
python main.py symbols
```

## 输出示例

终端会显示：

- 最新价、EMA20、ATR14
- K 线类型与形态
- 市场结构趋势与 BOS/CHoCH 事件
- 支撑/阻力位
- 最近 10 根 K 线摘要

JSON 模式输出完整结构化数据，字段包括 `snapshot`、`structure`、`levels`、`signal_hints`、`recent_bars` 等。

## 项目结构

```
pa_analyzer/
  loader.py        # yfinance 数据加载
  indicators.py    # EMA、ATR
  bar_features.py  # K 线几何特征
  patterns.py      # 形态识别
  structure.py     # 市场结构
  levels.py        # 支撑阻力 + 突破检测
  engine.py        # 分析引擎
main.py            # CLI 入口
```

## 支持品种

| 简称 | Ticker |
|------|--------|
| ES   | ES=F   |
| MES  | MES=F  |
| NQ   | NQ=F   |
| CL   | CL=F   |
| GC   | GC=F   |

也可直接传入 yfinance ticker，如 `SPY`、`ES=F`。

## 数据来源

默认使用 [yfinance](https://github.com/ranaroussi/yfinance) 免费数据。

- 分钟级数据有回溯天数限制（如 5m 约 60 天）
- 存在约 15 分钟延迟，**不适合直接用于实盘下单**
- 严肃回测建议使用 IB / MT5 等数据源（后续可扩展）

## 后续计划

- [ ] 接入 MT5 / IB 实时数据
- [ ] 简单 PA 策略回测模块
- [ ] 会话过滤（RTH 开盘时段）
- [ ] AI 分析接口（对接 LLM）

## License

MIT

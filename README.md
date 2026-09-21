# Factor Forge Public

[![Version](https://img.shields.io/badge/version-v0.4.1-blue)](https://github.com/damobianyuan0325/factor-forge-public/tree/v0.4.1)
[![Python](https://img.shields.io/badge/python-%3E%3D3.11-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-23%20passed-brightgreen)](#测试与质量门禁)

量化研究、因果回放、模拟交易与交易系统架构工具箱。

An open-source toolkit for quantitative research, causal replay, paper trading,
and trading-system architecture.

> **Research use only:** this repository is not a trading bot and is not a
> ready-to-deploy order execution system. Do not connect it directly to a real
> account or use the examples to place real-money orders.

---

## 中文

### 项目定位

> **重要说明：本仓库只供量化研究、架构学习、因果回放和模拟实验使用。它不是可直接部署的交易机器人，也不是完整的实盘下单系统。请勿把仓库中的示例、模拟 Broker 或执行组件直接连接真实账户和真实资金。**

Factor Forge Public 将真实量化系统中具有通用价值的架构重新实现为安全、可读、可测试的公开版本。项目重点不是提供一个承诺盈利的策略，而是展示如何把数据、因子、策略、回放、模拟盘、风控和订单执行组织成一条可验证的链路。

公开版与私有生产系统完全分离，不继承私有仓库历史，也不包含真实账户、交易凭据、生产服务配置、私有策略参数或第三方原始数据。仓库中出现的“实时”“执行”“订单”等接口用于研究系统边界、模拟流程和测试设计，不代表已经具备真实交易所接入所需的完整安全能力。

### 当前版本

- 版本：`v0.4.1`
- Python：`>= 3.11`
- 许可证：MIT
- 测试：23 项通过
- 默认执行环境：研究与模拟盘
- 真实交易所：只提供抽象接口，不提供可直接下单的实现

### 核心原则

1. **一个策略入口**：回放、模拟盘和实时模式调用同一个 `Strategy.evaluate()`。
2. **严格因果数据**：策略只能看到决策时刻已经收盘且已经可得的数据。
3. **分层解耦**：数据、因子、信号、风控和执行互不越权。
4. **信号不是订单**：`SignalPlan` 必须通过仓位计算和风险检查后才能进入 Broker。
5. **成本必须显式**：手续费、滑点和成交限制属于策略评价的一部分。
6. **先验证稳定性**：优先使用样本外、walk-forward、额外成本和删除最佳交易测试。
7. **默认不接真实资金**：仓库自带的唯一 Broker 实现是 `PaperBroker`。

### 架构

```text
历史数据源 -> 逐根回放入口 ----\
                                 -> 数据健康门 -> 因子注册表 -> SignalEngine
实时收盘K线 -> 实时快照入口 ----/                              |
                                                                v
                                                    同一个 Strategy.evaluate()
                                                                |
                                                                v
                                                          SignalPlan
                                                                |
                                              +-----------------+-----------------+
                                              |                                   |
                                              v                                   v
                                         研究记录                          仓位与 RiskEngine
                                                                                  |
                                                                                  v
                                                                          ExecutionService
                                                                                  |
                                                        +-------------------------+----------------+
                                                        |                                          |
                                                        v                                          v
                                                   PaperBroker                            私有 Broker 适配器
                                                   模拟成交                                真实交易所边界
```

### 功能状态

| 板块 | 负责内容 | 当前状态 |
| --- | --- | --- |
| 数据模型 | 标准 OHLCV、研究事件、时间和价格验证 | 已提供 |
| 数据接口 | 历史/实时数据源协议、轮询调度 | 已提供抽象 |
| 数据健康 | 连续性、陈旧度、未来数据、未收盘数据检查 | 已提供 |
| 因子系统 | 因子协议、注册表、目录和特征富化 | 已提供 |
| 研究工具 | 事件研究、前向收益、MFE/MAE、汇总统计 | 已提供 |
| 稳健性 | 时间切分、walk-forward、成本和删最佳交易压力测试 | 已提供 |
| 策略系统 | 注册表、统一输入、统一输出、示例策略 | 已提供 |
| 历史回放 | 逐根 K 线推进，禁止暴露未来数据 | 已提供 |
| 实时入口 | 已收盘快照、事件总线、线程安全市场状态 | 已提供 |
| 模拟盘 | 市价/限价模拟、费用、滑点、持仓和盈亏 | 已提供简化模型 |
| 风控 | 单笔、总敞口、权益比例和最低权益限制 | 已提供基础门禁 |
| 组合风控 | 最大持仓数、单日亏损和连续亏损熔断 | 已提供会话级门禁 |
| 执行编排 | 信号转订单、风控前置、Broker 调用 | 已提供 |
| 执行可靠性 | 订单状态机、读请求退避、写超时先对账、精确 payload 审批 | 已提供通用组件 |
| 幂等执行 | 相同策略决策生成确定性客户端订单号 | 已提供 |
| 审计 | 结构化研究和执行事件 | 已提供内存及 SQLite 实现 |
| 数据导入 | 标准 CSV 解析、去重和决策时点可得性检查 | 已提供 |
| 绩效统计 | 复利收益、最大回撤、胜率、Profit Factor、连续亏损 | 已提供 |
| 通知 | 无外发的协议、空实现和内存实现 | 已提供安全边界 |
| 真实交易所 | 签名、账户、下单、撤单和对账 | 仅定义私有扩展边界 |

### 项目目录

```text
src/factor_forge_public/
├── brokers/       # Broker 抽象与 PaperBroker
├── config/        # 回放、模拟盘和私有实盘共用运行假设
├── data/          # 数据提供接口、调度和健康检查
├── execution/     # 订单模型、状态机、预检、重试、仓位与执行编排
├── factors/       # 因子协议、注册表、平均K线和K线形态
├── monitoring/    # 结构化审计事件与安全通知边界
├── realtime/      # 事件总线和线程安全市场状态
├── research/      # 事件研究、前向收益、切分与压力测试
├── strategies/    # 可公开的示例策略
├── engine.py      # 统一信号引擎
├── live.py        # 实时/模拟快照入口
├── models.py      # 标准 Candle 与 ResearchEvent
├── replay.py      # 因果逐根回放入口
├── runtime.py     # RunMode、StrategyInput、SignalPlan
└── strategy.py    # Strategy 与 StrategyRegistry
```

### 安装

安装仅用于本地研究、测试和阅读代码。请使用隔离的开发环境，不要在安装后配置真实 API Key，也不要把示例 Broker 替换成真实下单接口后直接投入资金。

```bash
git clone https://github.com/damobianyuan0325/factor-forge-public.git
cd factor-forge-public
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
```

Windows PowerShell：

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
```

### 快速开始：事件研究

仓库自带的示例只使用合成数据：

```bash
python examples/synthetic_event_study.py
```

它会依次完成：生成合成 K 线、检测成交量异常、计算未来 4/12 根 K 线收益、汇总正收益比例与最大有利/不利波动。

核心调用方式：

```python
from factor_forge_public.research import (
    evaluate_forward_returns,
    summarize_returns,
    volume_spike_events,
)

events = volume_spike_events(candles, lookback=20, multiplier=2.0)
outcomes = evaluate_forward_returns(candles, events, horizons=(4, 12, 24))
summary = summarize_returns(outcomes)
```

未来收益只在事件生成完成后计算，不能作为事件条件或策略输入。

### 快速开始：同一策略用于回放和实时入口

```python
from factor_forge_public.engine import SignalEngine
from factor_forge_public.live import evaluate_closed_snapshot
from factor_forge_public.replay import replay_closed_candles
from factor_forge_public.strategies import MovingAverageCross
from factor_forge_public.strategy import StrategyRegistry

registry = StrategyRegistry()
registry.register(MovingAverageCross(fast_window=5, slow_window=20))
engine = SignalEngine(registry)

replay_plans = replay_closed_candles(
    engine,
    strategy_id="example.moving_average_cross",
    candles=candles,
    warmup_bars=21,
)

live_plan = evaluate_closed_snapshot(
    engine,
    strategy_id="example.moving_average_cross",
    candles=candles,
)
```

在可见 K 线完全相同时，最后一个回放结果必须与实时入口结果一致。测试会检查这一约束。

### 快速开始：模拟下单与风控

```python
from factor_forge_public.brokers import PaperBroker
from factor_forge_public.execution.service import ExecutionService
from factor_forge_public.risk import RiskEngine, RiskLimits

broker = PaperBroker(
    initial_cash=10_000.0,
    fee_bps=4.0,
    slippage_bps=2.0,
)
risk = RiskEngine(
    RiskLimits(
        max_order_notional=1_000.0,
        max_total_notional=5_000.0,
        max_equity_fraction_per_order=0.20,
    )
)
execution = ExecutionService(broker=broker, risk_engine=risk)

result = execution.submit_market_signal(
    signal_plan,
    quantity=0.01,
    timestamp_ms=signal_plan.observed_at_ms,
)
```

`ExecutionService` 不允许信号绕过风险检查。真实 Broker 应在私有仓库实现，并继续遵守同一个接口和风险前置顺序。

### 统一运行配置

```json
{
  "profile_id": "research-default",
  "symbols": ["BTC-USDT"],
  "timeframes": ["15m"],
  "capital": {
    "initial_equity": 10000,
    "equity_fraction_per_order": 0.1,
    "leverage": 1
  },
  "costs": {
    "fee_bps_per_side": 4,
    "slippage_bps_per_side": 2
  },
  "guards": {
    "maximum_order_notional": 1000,
    "maximum_total_notional": 5000,
    "maximum_open_positions": 1
  }
}
```

```python
from factor_forge_public.config import load_runtime_profile

profile = load_runtime_profile("runtime-profile.json")
```

同一份成本、资金和风险假设应同时用于回放、模拟盘和私有实盘适配器，避免结果因配置漂移而失真。

### 编写自己的策略

1. 继承 `Strategy`。
2. 声明稳定的 `strategy_id`、`version` 和 `minimum_candles`。
3. 只在 `evaluate()` 中读取 `StrategyInput`。
4. 不根据 `RunMode` 改变策略规则。
5. 返回 `SignalPlan`，不要直接调用 Broker。
6. 添加 live/replay 一致性测试和前缀不变性测试。

### 研究验证清单

在把研究结论称为“可能有效”之前，至少检查：

- 信号只使用当时已经可得的数据。
- 训练集与测试集严格按时间隔离。
- 手续费、滑点、资金费率和成交失败已经建模。
- 参数轻微变化后结果没有立即崩溃。
- 删除最赚钱的少数交易后仍有合理表现。
- 多个独立市场阶段中存在正向证据。
- 最大回撤、连续亏损和尾部风险可以承受。
- 回放、模拟盘和实时影子运行使用相同策略代码。

### PaperBroker 的已知限制

`PaperBroker` 是研究模型，不是交易所撮合模拟器。当前不完整模拟：

- 限价单只允许使用提交时点之后的 K 线成交，避免同 K 线回看偏差

- 盘口队列位置和排队成交概率
- 部分成交与撤单竞争
- 强平、自动减仓和保险基金
- 资金费率、借贷利息和保证金梯度
- 网络超时、请求状态不确定与交易所停机
- 极端行情中的跳空和止损穿透

因此模拟收益不能直接视为可实盘收益。

### 安全边界

仓库刻意不包含：

- 私有策略版本、机会库和优化参数
- API Key、私钥、账户号、Broker ID 和通知目标
- 真实交易所签名、生产下单、撤单和账户读取代码
- 本机绝对路径、LaunchAgent 和生产服务配置
- CoinAnk 或其他第三方原始数据
- SQLite 数据库、订单台账、日志和私人回测报告
- 私有仓库 Git 历史

请不要在 issue、测试样例或提交中发布真实凭据。若凭据曾经进入 Git 历史，应立即轮换凭据并清理完整历史，仅删除当前文件是不够的。

### 测试与质量门禁

```bash
pytest
```

当前测试覆盖：

- Candle 数据验证
- 平均 K 线因果计算
- 事件检测前缀不变性
- 未来数据和未收盘 K 线拦截
- live/replay 策略结果一致性
- 模拟盘手续费、持仓与已实现盈亏
- 超限订单风险拒绝
- 数据连续性与陈旧度检查
- 轮询调度确定性
- 事件订阅者故障隔离
- walk-forward 时间边界
- 成本和删除最佳交易压力测试

### 版本规则

项目遵循语义化版本：

- `MAJOR`：不兼容的公共接口变化
- `MINOR`：向后兼容的新模块或能力
- `PATCH`：向后兼容的修复和文档改进

当前稳定标签：`v0.4.1`。

### 路线图

- 更严格的回测成交模型和资金曲线统计
- 通用止盈、止损和订单生命周期状态机
- 参数敏感性与分阶段报告
- 可插拔数据存储接口
- 研究结果导出和可视化
- 更多不包含私有 alpha 的教学策略

### 贡献

欢迎提交通用研究工具、测试、文档和安全修复。请勿提交真实凭据、生产日志、第三方受限数据或无法说明来源的策略材料。

### 风险声明

本项目仅用于研究和教育，不构成投资建议，也不提供可直接运行的实盘交易方案。历史回放和模拟交易不能代表未来收益。仓库中的 `PaperBroker`、订单模型、执行编排、重试和风控组件均为研究示例，未覆盖真实交易所全部成交规则、故障模式、权限控制和资金安全要求。维护者不建议也不支持将本仓库直接用于真实下单；任何人不得把示例代码的存在理解为实盘适用性或收益保证。

---

## English

### Purpose

> **Important: this repository is for quantitative research, architecture
> study, causal replay, and paper experiments only. It is not a deployable
> trading bot or a complete live-order system. Do not connect its examples,
> paper broker, or execution components directly to a real account or real
> capital.**

Factor Forge Public reimplements reusable lessons from a real quantitative
system as a safe, readable, and tested open-source project. It does not promise
a profitable strategy. Its purpose is to show how market data, factors,
strategies, causal replay, paper trading, risk controls, and order execution can
form one verifiable pipeline.

The public project is fully separated from the private production system. It
does not inherit private Git history or include real accounts, credentials,
production services, private strategy parameters, or third-party raw data.
References to live data, execution, or orders describe research boundaries,
simulated workflows, and testable interfaces; they do not imply production
readiness or complete exchange safety controls.

### Current release

- Version: `v0.4.1`
- Python: `>= 3.11`
- License: MIT
- Tests: 23 passing
- Default environment: research and paper trading
- Live exchanges: abstract boundary only; no ready-to-trade implementation

### Core principles

1. **One strategy entrypoint:** replay, paper, and live modes call the same
   `Strategy.evaluate()` method.
2. **Causal inputs:** strategies may only read data closed and observable at the
   decision timestamp.
3. **Separated responsibilities:** data, factors, signals, risk, and execution
   cannot silently bypass each other.
4. **A signal is not an order:** every `SignalPlan` must pass sizing and risk
   controls before reaching a Broker.
5. **Explicit costs:** fees, slippage, and fill constraints belong in evaluation.
6. **Stability before peak returns:** use out-of-sample, walk-forward, extra-cost,
   and best-trade-removal tests.
7. **No real capital by default:** `PaperBroker` is the only included Broker.

### Architecture

```text
historical source -> candle replay ----\
                                       -> health gate -> factors -> SignalEngine
closed live data -> snapshot adapter --/                              |
                                                                        v
                                                            Strategy.evaluate()
                                                                        |
                                                                        v
                                                                   SignalPlan
                                                                        |
                                                     +------------------+---------------+
                                                     |                                  |
                                                     v                                  v
                                                research log                    sizing + RiskEngine
                                                                                        |
                                                                                        v
                                                                                ExecutionService
                                                                                        |
                                                             +--------------------------+--------------+
                                                             |                                         |
                                                             v                                         v
                                                        PaperBroker                        private Broker adapter
```

### Feature status

| Module | Responsibility | Status |
| --- | --- | --- |
| Data models | Normalized OHLCV, research events, time and price validation | Included |
| Data boundary | Historical/live provider protocol and polling scheduler | Abstract interface |
| Data health | Continuity, staleness, future-data, and open-candle checks | Included |
| Factors | Protocol, registry, catalog, and feature enrichment | Included |
| Research | Event studies, forward returns, MFE/MAE, summary statistics | Included |
| Robustness | Time splits, walk-forward, cost and best-trade-removal stress | Included |
| Strategies | Registry, shared input/output contract, example strategy | Included |
| Replay | Candle-by-candle causal evaluation | Included |
| Realtime | Closed snapshots, event bus, thread-safe market state | Included |
| Paper trading | Market/limit simulation, fees, slippage, positions, PnL | Simplified model |
| Risk | Per-order, total-exposure, equity-fraction, and minimum-equity limits | Basic gates |
| Portfolio risk | Open-position, daily-loss, and consecutive-loss circuit breakers | Session-level gate included |
| Execution | Signal-to-order orchestration with risk first | Included |
| Execution reliability | Order lifecycle, read backoff, write reconciliation, exact-payload approval | Generic components included |
| Idempotency | Deterministic client order IDs for identical strategy decisions | Included |
| Audit | Structured research and execution events | In-memory and SQLite implementations |
| Data import | Normalized CSV parsing, duplicate checks, point-in-time availability | Included |
| Performance | Compounded return, drawdown, win rate, profit factor, loss streak | Included |
| Notifications | Protocol, null sink, and memory sink with no external delivery | Safe boundary included |
| Live exchange | Signing, accounts, orders, cancellation, reconciliation | Private extension only |

### Repository layout

```text
src/factor_forge_public/
├── brokers/       # Broker boundary and PaperBroker
├── config/        # Shared runtime assumptions
├── data/          # Provider protocol, scheduler, and health checks
├── execution/     # Orders, lifecycle, preflight, retry, sizing, orchestration
├── factors/       # Factor protocol, registry, Heikin-Ashi, candle shape
├── monitoring/    # Structured audit events and safe notification boundary
├── realtime/      # Event bus and thread-safe market state
├── research/      # Events, returns, splits, and stress tests
├── strategies/    # Public example strategies
├── engine.py      # Shared signal engine
├── live.py        # Live/paper closed-snapshot adapter
├── models.py      # Candle and ResearchEvent
├── replay.py      # Causal candle replay
├── runtime.py     # RunMode, StrategyInput, SignalPlan
└── strategy.py    # Strategy and StrategyRegistry
```

### Installation

Installation is intended for local research, testing, and source-code study.
Use an isolated development environment. Do not configure real API credentials
or replace the example broker with a live adapter and then deploy real capital.

```bash
git clone https://github.com/damobianyuan0325/factor-forge-public.git
cd factor-forge-public
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
```

On Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
```

### Quick start: event study

The included example uses synthetic data only:

```bash
python examples/synthetic_event_study.py
```

```python
from factor_forge_public.research import (
    evaluate_forward_returns,
    summarize_returns,
    volume_spike_events,
)

events = volume_spike_events(candles, lookback=20, multiplier=2.0)
outcomes = evaluate_forward_returns(candles, events, horizons=(4, 12, 24))
summary = summarize_returns(outcomes)
```

Forward outcomes are calculated only after event generation and must never feed
back into event conditions or strategy inputs.

### Quick start: one strategy for replay and live inputs

```python
from factor_forge_public.engine import SignalEngine
from factor_forge_public.live import evaluate_closed_snapshot
from factor_forge_public.replay import replay_closed_candles
from factor_forge_public.strategies import MovingAverageCross
from factor_forge_public.strategy import StrategyRegistry

registry = StrategyRegistry()
registry.register(MovingAverageCross(fast_window=5, slow_window=20))
engine = SignalEngine(registry)

replay_plans = replay_closed_candles(
    engine,
    strategy_id="example.moving_average_cross",
    candles=candles,
    warmup_bars=21,
)
live_plan = evaluate_closed_snapshot(
    engine,
    strategy_id="example.moving_average_cross",
    candles=candles,
)
```

For identical visible closed candles, the final replay result must equal the
live-adapter result. Tests enforce this invariant.

### Quick start: paper execution and risk

```python
from factor_forge_public.brokers import PaperBroker
from factor_forge_public.execution.service import ExecutionService
from factor_forge_public.risk import RiskEngine, RiskLimits

broker = PaperBroker(initial_cash=10_000.0, fee_bps=4.0, slippage_bps=2.0)
risk = RiskEngine(
    RiskLimits(
        max_order_notional=1_000.0,
        max_total_notional=5_000.0,
        max_equity_fraction_per_order=0.20,
    )
)
execution = ExecutionService(broker=broker, risk_engine=risk)

result = execution.submit_market_signal(
    signal_plan,
    quantity=0.01,
    timestamp_ms=signal_plan.observed_at_ms,
)
```

`ExecutionService` never allows a signal to bypass risk checks. Real Broker
implementations should remain private and preserve the same risk-first order.

### Shared runtime profile

```json
{
  "profile_id": "research-default",
  "symbols": ["BTC-USDT"],
  "timeframes": ["15m"],
  "capital": {
    "initial_equity": 10000,
    "equity_fraction_per_order": 0.1,
    "leverage": 1
  },
  "costs": {
    "fee_bps_per_side": 4,
    "slippage_bps_per_side": 2
  },
  "guards": {
    "maximum_order_notional": 1000,
    "maximum_total_notional": 5000,
    "maximum_open_positions": 1
  }
}
```

```python
from factor_forge_public.config import load_runtime_profile

profile = load_runtime_profile("runtime-profile.json")
```

Replay, paper, and private live adapters should use the same capital, cost, and
risk assumptions to avoid silent configuration drift.

### Implementing a strategy

1. Subclass `Strategy`.
2. Declare stable `strategy_id`, `version`, and `minimum_candles` values.
3. Read only `StrategyInput` inside `evaluate()`.
4. Do not change trading rules based on `RunMode`.
5. Return a `SignalPlan`; never call a Broker directly.
6. Add replay/live parity and prefix-invariance tests.

### Research validation checklist

Before describing a result as potentially useful, verify that:

- every signal uses only information available at the decision timestamp;
- training and test periods are separated chronologically;
- fees, slippage, funding, and failed fills are represented;
- small parameter changes do not immediately destroy results;
- results remain reasonable after removing the best trades;
- evidence exists across multiple independent market regimes;
- drawdown, loss streaks, and tail risk are tolerable; and
- replay, paper, and live-shadow modes run the same strategy code.

### PaperBroker limitations

`PaperBroker` is a research model, not an exchange matching-engine simulator. It
only allows limit fills from candles later than submission, preventing same-bar
hindsight. It does not fully model queue position, partial fills, cancel races, liquidation,
auto-deleveraging, funding, margin tiers, network uncertainty, exchange outages,
gaps, or stop-price penetration. Paper results are not directly executable
performance estimates.

### Security boundary

This repository deliberately excludes:

- private strategy versions, opportunity libraries, and optimized parameters;
- API keys, private keys, accounts, broker identifiers, and notification targets;
- live exchange signing, account access, production orders, and cancellation;
- local absolute paths, production services, and deployment configuration;
- third-party restricted datasets;
- databases, order ledgers, logs, private reports, and private Git history.

Never post real credentials in issues, fixtures, or commits. If a credential
enters Git history, rotate it immediately and purge the full history; deleting
the latest file is not sufficient.

### Tests and quality gates

```bash
pytest
```

Coverage includes candle validation, causal Heikin-Ashi, event-prefix
invariance, future/open-candle rejection, replay/live parity, paper fees and PnL,
risk rejection, data continuity and staleness, deterministic polling, subscriber
failure isolation, walk-forward boundaries, and robustness stress tests.

### Versioning

The project follows semantic versioning:

- `MAJOR`: incompatible public API changes
- `MINOR`: backward-compatible modules and capabilities
- `PATCH`: backward-compatible fixes and documentation updates

Current stable tag: `v0.4.1`.

### Roadmap

- More realistic fill and equity-curve modeling
- Generic stop-loss, take-profit, and order-lifecycle state machines
- Parameter-sensitivity and regime reports
- Pluggable storage interfaces
- Research export and visualization
- Additional educational strategies without private alpha

### Contributing

Contributions to generic research tools, tests, documentation, and security are
welcome. Do not submit real credentials, production logs, restricted third-party
data, or strategy material without clear redistribution rights.

### Disclaimer

This project is for research and education only. It is neither investment
advice nor a ready-to-run live trading solution. Historical replay and paper
trading do not predict future performance. `PaperBroker`, order models,
execution orchestration, retry logic, and risk components are research examples
that do not cover every exchange rule, failure mode, permission control, or
capital-safety requirement. The maintainers do not recommend or support using
this repository directly for real-money order placement, and no included
example should be interpreted as live suitability or a performance guarantee.

## License

[MIT](LICENSE)

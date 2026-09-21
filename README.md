# Factor Forge Public

## 中文说明

Factor Forge Public 是一个面向量化研究、因果回放、模拟交易和交易系统架构学习的开源框架。

本项目来自真实量化系统的架构经验，但公开版经过重新设计与脱敏，不包含私有策略、生产凭据、真实交易数据、本机路径、通知目标或交易所私有实现。

### 设计原则

- 实盘、模拟盘和历史回放使用同一个策略入口。
- 策略只能读取决策时刻已经收盘、已经可见的数据。
- 数据接入、策略判断、风险检查和订单执行彼此分离。
- 研究事件不等于交易信号，交易信号也不等于允许下单。
- 回测必须考虑手续费、滑点、资金费率和成交不确定性。
- 优先检验样本外稳定性与参数敏感性，而不是追求最高历史收益。

### 系统板块

#### 1. 市场数据层

位置：`factor_forge_public.data`

负责定义统一的数据提供接口。历史数据库、文件和实时行情服务都可以实现 `MarketDataProvider`，但必须只返回指定时间点之前已经收盘的 K 线。公开版不包含任何交易所密钥、第三方付费数据或真实历史数据库。

#### 2. 标准数据模型

位置：`factor_forge_public.models`

负责标准化 OHLCV K 线和研究事件，并验证时间、价格范围与数据完整性。其他模块只依赖标准模型，不直接依赖某一家交易所的数据格式。

#### 3. 因子与特征层

位置：`factor_forge_public.factors`

负责从历史可见数据生成可复现特征。当前包含因果版本的平均 K 线转换。原始 K 线仍然是事实数据，衍生 K 线只用于研究和策略判断。

#### 4. 研究与事件分析

位置：`factor_forge_public.research`

负责事件检测、前向收益标注、最大有利波动、最大不利波动和汇总统计。事件先被独立检测，未来收益只能在离线评价阶段计算，不能反向进入事件条件。

#### 5. 统一策略接口

位置：`factor_forge_public.strategy`、`factor_forge_public.runtime`

每个策略只实现一个 `Strategy.evaluate()`。策略代码不得根据 `LIVE` 或 `REPLAY` 编写两套判断逻辑。运行模式只描述数据来自哪里，不改变策略规则。相同的已收盘 K 线输入，实盘模式和回放模式必须生成相同的 `SignalPlan`。

#### 6. 信号引擎

位置：`factor_forge_public.engine`

负责策略注册、最小数据长度检查和统一调用。`SignalPlan` 只是结构化研究信号，不会直接绕过风控发往交易所。

#### 7. 历史回放入口

位置：`factor_forge_public.replay`

回放器按照时间顺序逐根增加已收盘 K 线。每次策略调用只能看到当时已经出现的前缀数据，因此不会把后续 K 线暴露给策略。

#### 8. 实时与模拟入口

位置：`factor_forge_public.live`

实时入口接收最新的已收盘 K 线快照，并调用与回放完全相同的 `SignalEngine` 和策略对象。该入口只生成信号，不包含交易所请求。

#### 9. 风控与仓位管理

位置：`factor_forge_public.risk`、`factor_forge_public.execution.sizing`

负责检查单笔名义价值、总风险敞口、账户权益比例和最低权益，并按照权益比例、杠杆及合约最小数量计算仓位。所有订单必须先通过风控。

#### 10. 订单与执行编排

位置：`factor_forge_public.execution`

负责标准订单、成交、持仓和账户模型。`ExecutionService` 将策略信号转换为订单意图，执行风险检查，然后才调用 Broker。公开版不会自动连接真实交易所。

#### 11. 模拟盘

位置：`factor_forge_public.brokers.paper`

`PaperBroker` 提供确定性的研究模拟：

- 市价单按参考价加滑点成交。
- 限价单只能在后续传入的 K 线触及价格后成交。
- 计算手续费、持仓均价、已实现盈亏和未实现盈亏。
- 检查 `reduce_only`，避免模拟减仓单反向扩大仓位。

这是简化成交模型，不能替代盘口队列、部分成交、爆仓、资金费率和交易所故障模拟。

#### 12. 交易所适配边界

位置：`factor_forge_public.brokers.base`

`Broker` 定义提交订单、取消订单和查询账户的抽象接口。开发者可以在自己的私有项目中实现真实交易所适配器。为避免误下单和凭据泄露，本仓库不提供任何真实交易所签名代码、API 地址、账户读取或生产下单实现。

#### 13. 审计与可观测性

位置：`factor_forge_public.monitoring`

负责记录数据、信号、风控和执行阶段的结构化事件。当前公开版提供内存审计实现，实际项目可以扩展到数据库或日志平台。

### 统一运行链路

```text
历史数据 -> 逐根回放入口 ----\
                              -> SignalEngine -> 同一个 Strategy.evaluate()
实时收盘K线 -> 实时入口 ------/
                                           |
                                           v
                                      SignalPlan
                                           |
                                           v
                                      RiskEngine
                                           |
                                           v
                                   ExecutionService
                                           |
                          +----------------+----------------+
                          |                                 |
                          v                                 v
                     PaperBroker                    私有 Broker 实现
                     模拟成交                        真实交易所适配
```

### 已排除的私有内容

- 私有策略版本和优化参数
- 实盘账户、API Key、私钥和 Broker ID
- 真实通知目标、用户标识和本机目录
- HTX 或其他交易所的私有签名与生产执行代码
- LaunchAgent、生产服务名和部署配置
- CoinAnk 或其他第三方原始数据
- SQLite 数据库、日志、订单记录和回测报告
- 私有仓库的 Git 历史

### 安装与测试

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
python examples/synthetic_event_study.py
pytest
```

测试包括未来数据拦截、未收盘 K 线拦截，以及相同数据下实盘与回放信号一致性。

### 风险声明

本项目仅用于研究和教育，不构成投资建议。历史回放和模拟交易不能代表未来收益。连接真实资金前，使用者必须自行完成数据质量、交易成本、风控、权限、合规和极端行情测试。

---

## English

Factor Forge Public is an open-source framework for quantitative research,
causal replay, paper trading, and trading-system architecture education.

It reflects lessons from a real quantitative system, but this public edition is
redesigned and sanitized. It contains no private strategies, production
credentials, real trading data, local paths, notification targets, or private
exchange implementations.

### Design principles

- Live, paper, and replay modes use the same strategy entrypoint.
- A strategy may read only data that was closed and observable at decision time.
- Data ingestion, strategy evaluation, risk checks, and execution are separated.
- A research event is not a signal, and a signal is not permission to trade.
- Fees, slippage, funding, and fill uncertainty belong in practical evaluation.
- Out-of-sample stability and parameter sensitivity matter more than peak returns.

### System modules

1. **Market data** (`factor_forge_public.data`) defines a vendor-neutral,
   point-in-time candle provider interface.
2. **Models** (`factor_forge_public.models`) validate normalized OHLCV candles
   and research events.
3. **Factors** (`factor_forge_public.factors`) calculate reproducible features,
   including a causal Heikin-Ashi transformation.
4. **Research** (`factor_forge_public.research`) detects events and evaluates
   forward returns and favorable/adverse excursions offline.
5. **Unified strategies** (`factor_forge_public.strategy`, `.runtime`) expose
   one deterministic `Strategy.evaluate()` method for every runtime mode.
6. **Signal engine** (`factor_forge_public.engine`) routes validated inputs to a
   registered strategy.
7. **Replay** (`factor_forge_public.replay`) advances one closed candle at a time
   without exposing future observations.
8. **Live/paper input** (`factor_forge_public.live`) evaluates a closed snapshot
   through the same engine and strategy used by replay.
9. **Risk and sizing** (`factor_forge_public.risk`, `.execution.sizing`) enforce
   exposure limits and calculate exchange-compatible quantities.
10. **Execution models and orchestration** (`factor_forge_public.execution`)
    convert approved signals into broker requests only after risk checks.
11. **Paper trading** (`factor_forge_public.brokers.paper`) models fees,
    slippage, positions, PnL, market fills, and later-candle limit fills.
12. **Exchange boundary** (`factor_forge_public.brokers.base`) defines the
    interface for private broker adapters without shipping live credentials or
    exchange-specific signing code.
13. **Audit and observability** (`factor_forge_public.monitoring`) record
    structured decisions across the research and execution pipeline.

### One strategy, multiple runtimes

```text
historical candles -> causal replay ----\
                                      -> SignalEngine -> Strategy.evaluate()
closed live candles -> live adapter ---/
                                                |
                                                v
                                           SignalPlan
                                                |
                                                v
                                           RiskEngine
                                                |
                                                v
                                        ExecutionService
                                                |
                               +----------------+----------------+
                               |                                 |
                               v                                 v
                          PaperBroker                  private Broker adapter
```

Given the same visible closed candles, replay and live modes must produce the
same `SignalPlan`. Tests enforce runtime parity and reject future or open candles.

### Deliberately excluded

- Private strategy versions and optimized parameters
- API keys, private keys, account identifiers, and broker identifiers
- Notification targets, personal identifiers, and local machine paths
- Private exchange signing or production execution code
- Production services and deployment configuration
- Third-party raw datasets, databases, logs, order ledgers, and private reports
- Git history from the private repository

### Installation and tests

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
python examples/synthetic_event_study.py
pytest
```

### Disclaimer

This project is for research and education only and is not investment advice.
Historical replay and paper trading do not predict future performance. Users are
responsible for validating data, execution costs, risk controls, permissions,
compliance, and extreme-market behavior before connecting real capital.

## License

MIT

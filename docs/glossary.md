# ShuaiCoin 统一术语表

<!--
版本号:     1.1.0
最后更新:   2026-05-13
作者:       @dev-team
评审人:     @core-team
-->

---

| **版本号** | **日期** | **作者** | **变更说明** |
| 1.1.0 | 2026-05-13 | @dev-team | 全文转换为中文术语定义 |
| 1.0.0 | 2026-05-13 | @dev-team | 初始术语表发布 |

---

## A

**ADR (架构决策记录):** 一种文档，用于记录重要的架构决策及其上下文和后果。

**地址 (Address):** 从用户公钥派生的标识符，用于发送和接收代币。格式为 `0x` 加 40 个十六进制字符。

**异步挖矿 (Async Mining):** 一种非阻塞挖矿模式，PoW 计算在后台线程中运行，客户端通过 `/mine/status/<task_id>` 轮询获取结果。

**异步 (Asynchronous):** 一种执行模型，任务在等待 I/O 时让出控制权，允许其他任务并发继续执行。

## B

**区块 (Block):** 区块链的基本单元，包含一组交易、一个工作量证明哈希、前一个区块的链接和元数据。

**区块高度 (Block Height):** 区块在链中的顺序索引号，从 0 (创世块) 开始。

**区块奖励 (Block Reward):** 矿工成功追加新区块所获得的 SHUAI 代币数量。默认值为 `10.0` 加上总交易费。

## C

**C4 模型 (C4 Model):** 一组分层软件架构图 (上下文、容器、组件、代码)，用于以不同缩放级别描述系统。

**链同步 (Chain Sync):** 对等节点汇聚到单一最长有效链 (规范链) 的过程。

**Coinbase 交易 (Coinbase Transaction):** 每个区块中的第一笔交易，铸币新代币并将费用奖励给矿工。`sender = 0x000000000000_SYSTEM`。

**共识 (Consensus):** 分布式节点就区块链状态达成一致的机制。ShuaiCoin 使用工作量证明 (PoW)。

**合约状态 (Contract State):** 存储在链上的键值对，表示已部署智能合约的持久化数据。

## D

**动态难度调整 (DDA - Dynamic Difficulty Adjustment):** 一种根据最近区块滑动窗口上的平均出块时间重新计算挖矿难度的算法。

**去中心化金融 (DeFi - Decentralized Finance):** 基于区块链技术构建的金融服务，无需中心化中介机构。

**Docker Compose:** 一种通过单个 YAML 文件定义和运行多容器 Docker 应用程序的工具。

## E

**ELK (Elasticsearch, Logstash, Kibana):** 一套广泛使用的集中式日志聚合、搜索和可视化技术栈。

## F

**Flask:** ShuaiCoin 用于 API 和管理面板的 Python Web 微框架。

**分叉 (Fork):** 由两个矿工在相似高度找到有效区块而引起的区块链分叉；通过选择最长链来解决。

**冻结账户 (Frozen Account):** 被管理员暂停了交易和挖矿权限的用户账户。

## G

**Gas:** 智能合约执行中计算成本的度量单位 (继承自以太坊术语)。

**创世块 (Genesis Block):** 区块链中的第一个区块 (`index = 0`)，在系统初始化期间创建，`miner_address = 0xGENESIS_MINER_ACCOUNT`。

**Grafana:** 一种用于监控仪表盘的开源分析和交互式可视化平台。

**Gunicorn:** 一个 Python WSGI HTTP 服务器，用作 ShuaiCoin 的生产应用服务器。

**灰度发布 (Grayscale Release):** 一种渐进式部署策略，在全量上线前将小比例流量路由到新版本。

## H

**哈希 (Hash):** SHA-256 产生的固定长度加密摘要，用于区块链接、交易标识和工作量证明验证。

## J

**JWT (JSON Web Token):** 一种紧凑的、URL 安全的令牌格式，用于无状态 API 身份验证。

## L

**轻节点 (Light Node):** 仅存储区块头并通过 ZK 证明验证交易的节点，而非全量存储链数据。

**Loki:** 一种可水平扩展的高可用多租户日志聚合系统，与 Grafana 集成。

## M

**Mempool:** 等待被打包到区块中的未确认交易集合，存储于数据库中 (`block_index IS NULL`)。

**迁移 (Migration):** 通过 Flask-Migrate 生成的版本化数据库模式变更脚本。

## O

**预言机 (Oracle):** 将链下信息 (如价格数据) 带上区块链的外部数据源。

**ORM (对象关系映射):** 一种使用面向对象编程语言在不同类型系统间转换数据的技术。ShuaiCoin 使用 SQLAlchemy。

## P

**P2P (对等网络):** 一种去中心化的网络架构，节点之间无需中心服务器直接通信。

**Payload:** 附加到交易中的用于智能合约交互的不透明数据，格式为 JSON。

**工作量证明 (PoW - Proof of Work):** 一种共识机制，矿工竞争寻找一个随机数 (proof)，使得 `SHA-256(last_proof \|\| proof)` 以 `N` 个前导零开头。

**Prometheus:** 一种用于指标采集的开源系统监控和告警工具包。

**Promtail:** 一个日志代理，将本地日志内容发送到 Grafana Loki 实例。

## R

**RESTful API:** 一种使用 HTTP 方法 (GET、POST、PUT、DELETE) 和無状态通信设计网络应用程序的架构风格。

**环签名 (Ring Signature):** 一种加密方案，使用户能够以群组成员身份签署交易，同时保护匿名性。

**RPO (恢复点目标):** 以时间度量的最大可接受数据丢失量。

**RTO (恢复时间目标):** 在服务中断后可恢复服务的最大可接受时间。

## S

**Session:** 在浏览器和 Flask 服务器之间使用签名 Cookie 维护的服务器端状态，用于基于 Web 的身份验证。

**SHA-256:** 产生 256 位摘要的安全哈希算法，用于区块哈希、工作量证明和交易标识。

**SHUAI:** ShuaiCoin 区块链的原生加密货币代币。

**分片 (Sharding):** 一种将区块链状态分区到多个并行链 (分片) 上以提高吞吐量的可扩展性技术。

**智能合约 (Smart Contract):** 在链上确定性地执行的用户定义代码，支持 `deploy_contract` 和 `call_contract` 交易类型。

**SQLAlchemy:** ShuaiCoin 用于数据库交互的 Python SQL 工具包和 ORM。

**SPA (单页应用):** 一种动态重写当前页面而非从服务器加载全新页面的 Web 应用程序。

**隐身地址 (Stealth Address):** 为每笔交易生成的一次性地址，用于隐藏接收方的身份。

## T

**TPS (每秒交易数):** 衡量区块链网络每秒能处理多少笔交易的性能指标。

**交易 (Transaction):** 从一个地址到另一个地址的已签名价值转移，记录在区块链上，字段包括：`tx_hash`、`sender`、`recipient`、`amount`、`fee`、`tx_type`、`payload`、`block_index`。

**交易密码 (Tx Password):** 专门用于授权发起交易的辅助密码，与登录密码分离。

## V

**虚拟机 (VM - Virtual Machine):** 智能合约的执行环境；ShuaiVM 是原生 VM，WASM VM 是计划中的扩展。

## W

**WASM (WebAssembly):** 一种用于基于栈的虚拟机的二进制指令格式，可使用 C++ 和 Rust 等语言高效执行智能合约。

**WebSocket:** 一种通过单个 TCP 连接提供全双工通信通道的通信协议，用于实时事件通知。

## Z

**零知识证明 (ZK - Zero-Knowledge Proof):** 一种加密方法，一方可以向另一方证明某个陈述为真，而不透露除陈述有效性之外的任何信息。

**ZK 证明 (ZK Proof):** 一种紧凑的加密证明，使轻量级客户端能够在不下载完整链的情况下验证区块的有效性。

---

*更新本术语表时，请向 `docs/glossary.md` 提交 PR，遵循字母排序约定。*

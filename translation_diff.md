# 翻译变更对照表 (Translation Diff)

<!--
版本号:     1.0.0
最后更新:   2026-05-13
作者:       @dev-team
说明:       逐条列出英文原文与中文译文的对应关系
-->

本文档记录 `项目中文总文档.md` 中所有英文原文与中文译文的对应关系。

---

## 通用术语

| 英文原文 | 中文译文 |
| :--- | :--- |
| Proof of Work (PoW) | 工作量证明 (PoW) |
| Peer-to-Peer (P2P) | 对等网络 (P2P) |
| Zero-Knowledge Proof (ZK) | 零知识证明 (ZK) |
| Decentralized Application (DApp) | 去中心化应用 (DApp) |
| Dynamic Difficulty Adjustment (DDA) | 动态难度调整 (DDA) |
| WebAssembly (WASM) | WebAssembly (WASM) |
| Object-Relational Mapping (ORM) | 对象关系映射 (ORM) |
| Single Page Application (SPA) | 单页应用 (SPA) |
| Distributed Denial of Service (DDOS) | 分布式拒绝服务 (DDOS) |
| Oracle | 预言机 |
| Mempool | 交易池 |
| Token | 令牌 / 代币 |
| Session Cookie | Session Cookie |
| JWT Bearer Token | JWT 持有者令牌 (Bearer Token) |
| Reentrancy | 重入攻击 |
| Turing-complete | 图灵完备 |
| Canary Deployment | 金丝雀部署 |
| Grayscale Release | 灰度发布 |

## API 文档 (docs/API.md)

| 英文原文 | 中文译文 |
| :--- | :--- |
| ShuaiCoin exposes a RESTful API over HTTP/1.1 | ShuaiCoin 在 HTTP/1.1 之上对外暴露 RESTful API |
| Authentication | 身份验证 |
| Unified Response Envelope | 统一响应信封 |
| Human-readable message | 人类可读的提示信息 |
| Rate Limit | 速率限制 |
| Rate limit exceeded | 速率限制已达上限 |
| Backward compatible | 向下兼容 |
| BREAKING | 破坏性变更 |
| Trigger synchronous mining | 触发同步挖矿 |
| Returns a task_id for status polling | 返回 task_id 供轮询状态使用 |
| Verify local blockchain integrity | 校验本地区块链完整性 |
| Submit a new transaction to the mempool | 向交易池提交一笔新交易 |
| Register peer nodes for P2P discovery | 注册对等节点以进行 P2P 发现 |
| Manually trigger chain conflict resolution | 手动触发链冲突解决 |
| Toggle account freeze status | 切换账户冻结状态 |
| View or update system configuration | 查看或更新系统配置 |
| Verify external peer nodes asynchronously | 异步校验外部对等节点 |
| Your account has been frozen by the security center! | 您的账户已被安全中心冻结！ |
| Operation successful | 操作成功 |
| Invalid username or password | 用户名或密码无效 |
| Mining task started | 挖矿任务已启动 |
| Transaction added to mempool | 交易已加入交易池 |
| Connection timeout | 连接超时 |

## 架构文档 (docs/architecture_v2.md)

| 英文原文 | 中文译文 |
| :--- | :--- |
| System Context | 系统上下文 |
| Container Diagram | 容器图 |
| Component Diagram | 组件图 |
| Deployment Diagram | 部署图 |
| Interaction Sequences | 交互时序 |
| Technology Selection Rationale | 技术选型理由 |
| Performance Baseline | 性能基线 |
| Architecture Decision Records (ADR) | 架构决策记录 (ADR) |
| End User | 终端用户 |
| Node Operator | 节点运维者 |
| Metrics collection and alerting | 指标采集与告警 |
| Log aggregation | 日志聚合 |
| Persistent state storage | 持久化状态存储 |
| Cache and rate limit backend | 缓存与速率限制后端 |
| API gateway, admin panel, SPA | API 网关、管理面板、SPA |
| PoW mining, consensus, contract VM | PoW 挖矿、共识、合约虚拟机 |
| Node discovery, chain sync, broadcast | 节点发现、链同步、广播 |
| Key mgmt, signing, address gen | 密钥管理、签名、地址生成 |
| Fee strategy, reward calculation | 手续费策略、奖励计算 |
| Auth, DDOS protection, audit | 认证、DDOS 防护、审计 |
| Real-time event push | 实时事件推送 |
| Query cache, rate limits | 查询缓存、速率限制 |
| On-chain reports, mining stats | 链上报表、挖矿统计 |
| Backup, migration, cleanup | 备份、迁移、清理 |
| Production-spec staging | 生产规格预发布环境 |

## 迁移指南 (docs/architecture.md)

| 英文原文 | 中文译文 |
| :--- | :--- |
| Monolithic Python application | 单体 Python 应用程序 |
| In-memory Python list (lost on restart) | 内存中的 Python 列表 (重启时丢失) |
| Synchronous only, blocking the HTTP request thread | 仅同步模式，阻塞 HTTP 请求线程 |
| Session only (Flask-Login) | 仅 Session (Flask-Login) |
| Inconsistent; some endpoints returned redirects, others JSON | 格式不一致；部分接口返回重定向，部分返回 JSON |
| Manual pytest only. No CI quality gate. | 仅手动 pytest。无 CI 质量门禁。 |
| Evolutionary Map | 演进对照表 |
| Deprecated Component Migration | 废弃组件迁移 |
| Rollback Plan | 回滚方案 |
| Rollback Trigger Conditions | 回滚触发条件 |
| Rollback Decision Matrix | 回滚决策矩阵 |

## 合约开发 (docs/contract_dev.md)

| 英文原文 | 中文译文 |
| :--- | :--- |
| Contract Execution Model | 合约执行模型 |
| Minimal state machine | 最小化状态机 |
| JSON payloads embedded in transactions | 嵌入在交易中的 JSON 负载 |
| Key-Value State Persistence | 键值状态持久化 |
| Token Issuance | 代币发行 |
| Solidity Compatibility (Future EVM Support) | Solidity 兼容性 (未来 EVM 支持) |
| Security Audit Checklist | 安全审计清单 |
| Common Vulnerability Checklist | 常见漏洞清单 |
| Unit Testing | 单元测试 |
| Coverage Requirement | 覆盖率要求 |
| Gas Optimization Strategies | Gas 优化策略 |
| CI Contract Quality Gate | CI 合约质量门禁 |
| Contract Lifecycle Management | 合约生命周期管理 |

## 部署指南 (docs/deploy_v2.1.md + docs/deployment.md)

| 英文原文 | 中文译文 |
| :--- | :--- |
| Environment Requirements | 环境要求 |
| Environment Variables | 环境变量 |
| Secret Management | 密钥管理 |
| One-Click Deploy Script | 一键部署脚本 |
| Pre-flight checks | 预检 |
| Health check | 健康检查 |
| Grayscale Release | 灰度发布 |
| Canary Deployment Architecture | 金丝雀部署架构 |
| Rollback Thresholds | 回滚阈值 |
| Alarm Rules | 告警规则 |
| Production Validation Tests | 生产验证用例 |
| Smoke Test | 冒烟测试 |
| Multi-Region Disaster Recovery Topology | 多区域灾备拓扑 |
| Data Backup and Recovery SOP | 数据备份与恢复 SOP |
| Capacity Planning | 容量规划 |
| Sizing Formula | 容量评估公式 |
| Stress Test Report Template | 压测报告模板 |
| Network Security Group Configuration | 网络安全组配置 |
| Monitoring Dashboard Template | 监控仪表盘模板 |

## 数据库修复报告 (docs/fix_report_db_column.md)

| 英文原文 | 中文译文 |
| :--- | :--- |
| Defect Summary | 缺陷摘要 |
| Root Cause Analysis (5 Whys) | 根因分析 (5 Whys) |
| Impact Assessment Matrix | 影响评估矩阵 |
| Affected Components | 受影响组件 |
| Fix Implementation | 修复实施 |
| Quick Rebuild (Development) | 快速重建 (开发环境) |
| Production Migration (Recommended) | 生产级迁移 (推荐) |
| Data Fix SQL Audit Process | 数据修复 SQL 审计流程 |
| Regression Test Cases | 回归测试用例 |
| Preventive Measures | 预防措施 |
| 48-Hour Post-Fix Monitoring | 修复后 48 小时监控 |
| Lessons Learned | 经验教训 |
| Never use db.create_all() on production databases | 绝不将 db.create_all() 用于生产数据库 |
| Always run flask db migrate --check in CI | 始终在 CI 中运行 flask db migrate --check |

## README 文档

| 英文原文 | 中文译文 |
| :--- | :--- |
| Build Status | 构建状态 |
| Test Coverage | 测试覆盖率 |
| License | 许可证 |
| Docker Ready | Docker |
| Docs | 文档 |
| 30-Second Quick Start | 30 秒快速启动 |
| Troubleshooting | 故障排查速查 |
| Code of Conduct | 贡献者行为准则 |
| Contact & License | 联系方式与许可证 |
| Core Feature Checklist | 核心功能清单 |
| Project Vision | 项目愿景 |

---

*本文档作为 `项目中文总文档.md` 的翻译追溯依据。每条记录按章节分组，按出现顺序排列。*

# ShuaiCoin 文档中心

<!--
版本号:     2.1.0
最后更新:   2026-05-13
作者:       @dev-team
评审人:     @core-team
-->

欢迎查阅 ShuaiCoin 开发者文档。本项目是基于 Python 的全栈区块链实现，提供从核心共识到部署运维的完整文档体系。

---

## 目录指南

| 文档 | 版本 | 最后更新 | 说明 |
| :--- | :--- | :--- | :--- |
| [README.md](../README.md) | 2.1.0 | 2026-05-13 | 项目主页：愿景、快速启动、功能清单、行为准则 |
| [API.md](API.md) | 2.1.0 | 2026-05-13 | RESTful API 规范：请求/响应、鉴权、分页、错误码 |
| [architecture_v2.md](architecture_v2.md) | 2.1.0 | 2026-05-13 | V2 架构设计：C4 模型、时序图、ADR |
| [architecture.md](architecture.md) | 2.1.0 | 2026-05-13 | V1 → V2 迁移指南：演进对 比、回滚方案 |
| [contract_dev.md](contract_dev.md) | 2.1.0 | 2026-05-13 | 智能合约开发：编码规范、审计清单、CI 脚本 |
| [deploy_v2.1.md](deploy_v2.1.md) | 2.1.0 | 2026-05-13 | V2.1 部署指南：一键脚本、灰度发布、告警 |
| [deployment.md](deployment.md) | 2.1.0 | 2026-05-13 | 生产部署：多区域灾备、备份恢复、容量规划 |
| [fix_report_db_column.md](fix_report_db_column.md) | 2.1.0 | 2026-05-13 | DB 修复报告：5 Whys、影响矩阵、48h 监控 |
| [full_architecture_guide.md](full_architecture_guide.md) | 2.1.0 | 2026-05-13 | 全量架构指南：链路追踪、成本、合规、FAQ |
| [interface-changelog.md](interface-changelog.md) | 2.1.0 | 2026-05-13 | 接口变更日志：统一格式、回滚兼容策略 |
| [node_mgmt_audit.md](node_mgmt_audit.md) | 2.1.0 | 2026-05-13 | 节点管理审计：日志格式、ELK、告警阈值 |
| [glossary.md](glossary.md) | 1.0.0 | 2026-05-13 | 统一术语表：中英文对照定义 |

---

## 核心模块说明

| 模块 | 路径 | 职责 |
| :--- | :--- | :--- |
| 核心引擎 | `core/` | 区块链共识、区块生成、合约执行 |
| 数据层 | `db/` | ORM 模型：区块、交易、用户、合约状态 |
| 网络层 | `p2p/` | 节点发现与最长链共识同步 |
| 应用层 | `web/` | Flask 管理后台、API、SPA |
| 钱包 | `wallet/` | 密钥管理、交易签名、地址生成 |
| 安全 | `security/` | DDOS 防护、内容审核、审计日志 |
| 监控 | `monitor/` | Prometheus 指标、告警规则、仪表盘 |
| 缓存 | `cache/` | Redis 与内存缓存 |
| 运维 | `scripts/` | 备份、迁移、清理、部署脚本 |
| 测试 | `tests/` | 单元测试、集成测试、性能测试 |

---

## 更新日志

### 2026-05-13 — 文档体系全面升级 (v2.1.0)

| 文档 | 变更类型 | 变更说明 |
| :--- | :--- | :--- |
| `API.md` | 重写 | 补全 RESTful 规范、鉴权方式、分页规则、错误码映射、版本变更记录 |
| `architecture_v2.md` | 重写 | 新增 C4 模型架构图、交互时序图、技术选型理由、性能基线、ADR 附录 |
| `architecture.md` | 重写 | 新增 V1→V2 差异对 比、废弃组件迁移指南、回滚方案与决策矩阵 |
| `contract_dev.md` | 重写 | 新增 Solidity 规范、审计 Checklist、单元测试覆盖率要求、CI 审计脚本 |
| `deploy_v2.1.md` | 重写 | 新增一键部署脚本 (bash + python)、环境变量清单、密钥管理、灰度发布、生产验证用例 |
| `deployment.md` | 重写 | 新增多区域灾备拓扑、备份/恢复 SOP、容量评估公式、压测报告模板 |
| `fix_report_db_column.md` | 重写 | 新增 5 Whys 根因分析、影响面矩阵、SQL 审计流程、回归测试、48h 监控 |
| `full_architecture_guide.md` | 重写 | 新增 OpenTelemetry 链路追踪、成本模型、GDPR/等保 2.0 合规、FAQ、故障排查决策树 |
| `interface-changelog.md` | 重写 | 统一变更格式、新增回滚兼容策略与通知机制 |
| `node_mgmt_audit.md` | 重写 | 新增 5W1R 审计日志格式、ELK 解析规则、异常告警阈值、季度审计报告模板 |
| `README.md` | 重写 | 新增项目愿景、核心功能清单、30 秒快速启动、badge 徽章、行为准则、联系方式 |
| `glossary.md` | 新增 | 统一术语表，避免中英文混排 |
| `docs/README.md` | 新增 | 文档中心索引与更新日志 |

### 2026-04-30 — 模块化架构重构 (v2.0.0)

- 新增 `architecture_v2.md`：模块化架构设计
- 新增 `deploy_v2.1.md`：Docker 部署方案
- 新增 `interface-changelog.md`：接口变更记录
- 更新 `API.md`：JWT 鉴权、Swagger 文档

### 2026-01-15 — 初始文档发布 (v1.0.0)

- 初始发布 `architecture.md`、`API.md`、`deployment.md`、`contract_dev.md`

---

## 贡献指南

1. 文档使用 Markdown 格式，目录层级不超过 3 级。
2. 代码片段、命令行、路径使用反引号包裹，标注语言类型。
3. 图表统一使用 Mermaid 源码嵌入。
4. 提交前运行 `markdownlint` 和 `cspell` 检查。

---

*术语定义参见 [glossary.md](glossary.md)。*

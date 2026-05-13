# ShuaiCoin Architecture Design Specification V2.0

<!--
Version:     2.1.0
Last Updated: 2026-05-13
Author:      @arch-team
Reviewer:    @core-team
-->

---

**Version** | **Date** | **Author** | **Changes**
2.1.0 | 2026-05-13 | @arch-team | C4 model, ADR appendix, performance baselines, interaction sequences
2.0.0 | 2026-04-30 | @arch-team | Modular redesign with observability, cache, and extensions
1.0.0 | 2026-01-15 | @arch-team | Initial monolithic architecture

---

## 1. C4 Model - Context Diagram

```mermaid
C4Context
    title System Context - ShuaiCoin Blockchain Platform

    Person(user, "End User", "Wallet holder / dApp user")
    Person(admin, "Node Operator", "Manages node lifecycle")
    System(shuai_coin, "ShuaiCoin Blockchain", "PoW consensus, smart contracts, P2P network")
    System_Ext(monitor, "Prometheus + Grafana", "Metrics collection and alerting")
    System_Ext(elk, "Loki + Promtail", "Log aggregation")
    System_Ext(db, "PostgreSQL / SQLite", "Persistent state storage")
    System_Ext(redis, "Redis", "Cache and rate limit backend")

    Rel(user, shuai_coin, "Send transactions, query balances", "HTTPS + WS")
    Rel(admin, shuai_coin, "Manage nodes, configure system", "HTTPS")
    Rel(shuai_coin, db, "Read/write state", "SQLAlchemy")
    Rel(shuai_coin, redis, "Cache queries, apply limits", "RESP")
    Rel(shuai_coin, monitor, "Export metrics", "Prometheus /metrics")
    Rel(shuai_coin, elk, "Ship logs", "Promtail / Loki")
```

## 2. C4 Model - Container Diagram

```mermaid
C4Container
    title Container Diagram - ShuaiCoin V2.1

    Container_Boundary(core_sys, "Core System") {
        Container(web, "Web Layer", "Flask + Gunicorn", "API gateway, admin panel, SPA")
        Container(core, "Core Engine", "Python", "PoW mining, consensus, contract VM")
        Container(db_cont, "Database", "SQLAlchemy ORM", "Block, tx, user, contract state models")
    }

    Container_Boundary(p2p_net, "P2P Network") {
        Container(p2p, "P2P Module", "Python + HTTP", "Node discovery, chain sync, broadcast")
    }

    Container_Boundary(ext_sys, "Extensions") {
        Container(wallet, "Wallet", "Python + Cryptography", "Key mgmt, signing, address gen")
        Container(plugins, "Plugins", "Python", "Fee strategy, reward calculation")
    }

    Container_Boundary(obs_sys, "Observability") {
        Container(mon, "Monitor", "Prometheus Exporter", "Metrics, alerts, dashboards")
        Container(sec, "Security", "Flask-Limiter + JWT", "Auth, DDOS protection, audit")
        Container(notif, "Notifications", "WebSocket + Email", "Real-time event push")
    }

    Container_Boundary(data_sys, "Data Layer") {
        Container(cache, "Cache", "Redis + Memory", "Query cache, rate limits")
        Container(analytics, "Analytics", "Python", "On-chain reports, mining stats")
        Container(scripts, "Ops Scripts", "Python + Click", "Backup, migration, cleanup")
    }

    Rel(web, core, "Invoke mining, verification", "Function calls")
    Rel(web, p2p, "Register peers, resolve chain", "HTTP")
    Rel(core, db_cont, "Persist blocks and transactions", "ORM")
    Rel(p2p, web, "Sync chain data", "HTTP API")
    Rel(web, cache, "Cache reads", "Redis protocol")
    Rel(sec, web, "Authenticate and rate-limit", "Middleware")
    Rel(mon, core, "Collect metrics", "In-process")
    Rel(analytics, db_cont, "Aggregate data", "SQL")
    Rel(scripts, db_cont, "Backup, migrate", "SQL/file I/O")
```

## 3. C4 Model - Component Diagram (Core Engine)

```mermaid
C4Component
    title Component Diagram - Core Engine

    Container_Boundary(core_engine, "Core Engine (core/)") {
        Component(blockchain, "Blockchain", "Python", "PoW mining, DDA, block creation")
        Component(contract, "ShuaiVM", "Python", "Smart contract execution engine")
        Component(utils, "Utilities", "Python", "Hash, balance, address helpers")
        Component(response, "Response Helpers", "Python", "Unified JSON envelope")
        Component(logging_mod, "Logging", "Python", "Structured logging with trace IDs")
    }

    Component(block_model, "Block Model", "SQLAlchemy", "Block ORM entity")
    Component(tx_model, "Transaction Model", "SQLAlchemy", "Transaction ORM entity")
    Component(user_model, "User Model", "SQLAlchemy", "User ORM entity")

    Rel(blockchain, contract, "Execute contract tx", "Function call")
    Rel(blockchain, block_model, "Persist blocks", "ORM write")
    Rel(blockchain, tx_model, "Update tx status", "ORM write")
    Rel(contract, tx_model, "Read payload", "ORM read")
    Rel(utils, block_model, "Compute hashes", "Function call")
```

## 4. Deployment Diagram

```mermaid
C4Deployment
    title Deployment Diagram - ShuaiCoin V2.1

    Deployment_Node(docker_host, "Docker Host (Linux)") {
        Deployment_Node(postgres_container, "PostgreSQL 12") {
            Container(db_instance, "shuai_coin DB", "PostgreSQL", "Chain state + users")
        }
        Deployment_Node(redis_container, "Redis 6") {
            Container(redis_instance, "Cache Store", "Redis", "Cache + rate limits")
        }
        Deployment_Node(web_container, "Gunicorn (4 workers)") {
            Container(web_app, "Flask App", "Python 3.12", "API + Admin + SPA")
        }
        Deployment_Node(loki_container, "Loki + Promtail") {
            Container(log_collector, "Log Agent", "Promtail", "Log shipping")
        }
    }

    Deployment_Node(prom_node, "Monitor Host") {
        Container(prom, "Prometheus", "Prometheus 2.45", "Metrics scraper")
        Container(graf, "Grafana", "Grafana 10.0", "Dashboards")
    }

    Deployment_Node(browser, "Client Browser") {
        Container(spa_ui, "Vue3 SPA", "Element Plus", "Admin dashboard")
    }

    Rel(spa_ui, web_app, "HTTPS API calls", "https://host:8000")
    Rel(web_app, db_instance, "SQLAlchemy", "tcp://db:5432")
    Rel(web_app, redis_instance, "RESP", "tcp://redis:6379")
    Rel(log_collector, web_app, "Tail logs", "file system")
    Rel(prom, web_app, "Scrape /metrics", "http://web:8000/metrics")
    Rel(graf, prom, "Query metrics", "PromQL")
```

---

## 5. Interaction Sequences

### 5.1 Mining Flow (Synchronous)

```mermaid
sequenceDiagram
    actor User
    participant Web as Flask Web
    participant Core as Blockchain Core
    participant DB as PostgreSQL
    participant Contract as ShuaiVM

    User->>Web: GET /mine
    Web->>Web: Check is_frozen
    alt Account frozen
        Web-->>User: 403 Forbidden
    end
    Web->>DB: SELECT last block
    DB-->>Web: Block(height=N)
    Web->>Core: proof_of_work(last_proof, difficulty)
    Core-->>Web: proof=24581
    Web->>DB: SELECT pending txs (ORDER BY fee DESC)
    DB-->>Web: [tx1, tx2, ...]
    loop Each contract tx
        Web->>Contract: execute_smart_contract(tx)
        Contract->>DB: INSERT/UPDATE contract state
    end
    Web->>Core: create_block(proof, prev_hash, miner_addr)
    Core->>DB: INSERT block, INSERT coinbase, UPDATE txs.block_index
    DB-->>Core: OK
    Core-->>Web: new_block, total_fees
    Web-->>User: 200 {status, data: {index, reward, hash}}
```

### 5.2 Mining Flow (Asynchronous)

```mermaid
sequenceDiagram
    actor Admin
    participant Web as Flask Web
    participant Thread as Background Thread
    participant DB as PostgreSQL

    Admin->>Web: POST /mine/async
    Web->>Web: Generate task_id (UUID)
    Web->>Web: Store task: {status: "processing"}
    Web->>Thread: Start background_mining(task_id, addr)
    Web-->>Admin: 200 {task_id}
    Thread->>Thread: Acquire app_context
    Thread->>DB: Query last block
    Thread->>Thread: proof_of_work()
    Thread->>Core: create_block()
    Thread->>DB: Commit block + txs
    Thread->>Web: Update task: {status: "success", block_index, reward}
    Admin->>Web: GET /mine/status/<task_id>
    Web-->>Admin: 200 {status: "success", block_index, reward}
```

### 5.3 Chain Verification Flow

```mermaid
sequenceDiagram
    actor User
    participant Web as Flask Web
    participant DB as PostgreSQL

    User->>Web: GET /verify
    Web->>DB: SELECT all blocks ORDER BY index ASC
    DB-->>Web: [block_0, block_1, ..., block_N]
    loop Each block
        Web->>Web: Compute hash_block(block_dict)
        Web->>Web: Compare computed vs stored hash
        Web->>Web: Verify previous_hash links
    end
    alt All blocks valid
        Web-->>User: 200 {corrupted_blocks: []}
    else Corrupted found
        Web-->>User: 200 {corrupted_blocks: [45, 46]}
    end
```

### 5.4 P2P Node Registration & Sync

```mermaid
sequenceDiagram
    actor Operator
    participant NodeA as Node A (self)
    participant NodeB as Node B (peer)

    Operator->>NodeA: POST /api/p2p/register {nodes: ["http://B:5000"]}
    NodeA->>NodeA: register_node("http://B:5000")
    NodeA-->>Operator: 200 {total_nodes: [...]}

    Note over NodeA: On conflict or manual trigger
    Operator->>NodeA: GET /api/p2p/resolve
    NodeA->>NodeB: GET http://B:5000/api/chain
    NodeB-->>NodeA: {chain: [...], length: 150}
    NodeA->>NodeA: Compare lengths
    alt Remote chain longer
        NodeA->>DB: REPLACE local chain with remote
        NodeA-->>Operator: "Chain replaced"
    else Local chain longer
        NodeA-->>Operator: "Chain is authoritative"
    end
```

---

## 6. Technology Selection Rationale

| Component | Choice | Rationale |
| :--- | :--- | :--- |
| **Web Framework** | Flask 3.x | Lightweight, mature, large ecosystem. Sufficient for ShuaiCoin's API-centric design. FastAPI considered but Flask aligns with existing team skills. |
| **ORM** | SQLAlchemy 2.x | Industry-standard Python ORM with Flask-SQLAlchemy integration. Supports SQLite (dev) and PostgreSQL (prod). |
| **Production Server** | Gunicorn 21.x | Pre-fork worker model. 4 workers optimal for I/O-bound blockchain API. |
| **Database** | PostgreSQL 12+ | ACID compliance, JSONB support for transaction payloads. SQLite for development convenience. |
| **Cache** | Redis 7.x | Sub-millisecond latency, built-in TTL, rate-limit counters via INCR. |
| **Auth** | PyJWT + Flask-Login | JWT for API clients, Session for web UI. Dual auth without coupling. |
| **Monitoring** | Prometheus + Grafana | Industry standard. Pull-based model avoids agent overhead. |
| **Logging** | Loki + Promtail | Lightweight alternative to ELK. Native Grafana integration. |
| **CLI** | Click 8.x | Pythonic, composable commands. Better than argparse for multi-command tools. |
| **Crypto** | Cryptography 41.x | FIPS 140-2 compliant. Used for key management and signing. |
| **Migrations** | Flask-Migrate (Alembic) | Versioned, reversible schema changes. CI-integrated drift detection. |

---

## 7. Performance Baseline

| Metric | Target | Measurement Method |
| :--- | :--- | :--- |
| **Block time** | 30 seconds (target) | `TARGET_BLOCK_TIME` config, monitored via DDA |
| **Sync PoW** | < 5 seconds per block | `log_api_call` duration metric |
| **Async PoW** | Background, non-blocking | Task status polling |
| **Chain verification** | < 2 seconds for 1000 blocks | `/verify` endpoint timing |
| **Wallet balance query** | < 50 ms | `GET /api/wallet/<addr>` |
| **Chain API** | < 100 ms (cached) | `GET /api/chain` with Redis |
| **Transaction submit** | < 200 ms | `POST /api/transactions/new` |
| **API throughput** | > 200 req/s (single node) | Gunicorn 4 workers |
| **Cache hit rate** | > 80% | Redis `INFO stats` |
| **Alert latency** | < 30 seconds | Prometheus `evaluation_interval` |

---

## 8. Architecture Decision Records (ADR)

### ADR-001: SQLite for Development, PostgreSQL for Production

**Status:** Accepted
**Date:** 2026-01-15
**Context:** Need a database that works with zero configuration for local development but scales for production deployment.
**Decision:** Use SQLite via environment-variable-switched `DATABASE_URL`. Default SQLite, override to PostgreSQL in Docker/production.
**Consequences:**
- Positive: Zero-config dev experience. Single binary for CI.
- Negative: SQLite lacks concurrent write support; dev-prod parity gap. Mitigated by CI testing on PostgreSQL.

### ADR-002: Dual Auth (Session + JWT)

**Status:** Accepted
**Date:** 2026-04-30
**Context:** Web UI users expect session-based auth. API clients need stateless JWT.
**Decision:** Keep Flask-Login sessions for web routes. Add JWT via PyJWT for `/api/*` endpoints. `admin_required` decorator checks both.
**Consequences:**
- Positive: No breaking change for web users. API clients get Bearer token support.
- Negative: Two auth code paths increase maintenance. Token revocation requires blacklist.

### ADR-003: Synchronous to Async Mining Migration

**Status:** Accepted
**Date:** 2026-05-13
**Context:** Synchronous PoW blocks the request thread, causing timeouts on slow hardware.
**Decision:** Keep `GET /mine` as synchronous. Add `POST /mine/async` + `GET /mine/status/<task_id>` for admin-only async mining.
**Consequences:**
- Positive: No breaking change. Admin gets non-blocking option.
- Negative: In-memory task store lost on restart. Future: persist tasks in Redis.

### ADR-004: In-Memory Mempool to Database Mempool

**Status:** Accepted
**Date:** 2026-04-30
**Context:** In-memory transaction pool lost on restart and was inaccessible to multi-process Gunicorn workers.
**Decision:** Store pending transactions in the `Transaction` table with `block_index IS NULL`. Query mempool via SQLAlchemy.
**Consequences:**
- Positive: Survives restarts. Visible to all Gunicorn workers.
- Negative: Additional DB load. Fee-based sorting at query time.

### ADR-005: Rate Limiting via Flask-Limiter with Redis Backend

**Status:** Accepted
**Date:** 2026-05-13
**Context:** Public endpoints need protection against abuse.
**Decision:** Use Flask-Limiter with Redis storage backend. Apply 10/min on `/mine` and `/verify`. 200/min global default.
**Consequences:**
- Positive: Easy to configure per-endpoint. Redis ensures consistency across workers.
- Negative: Redis dependency for rate limiting. Single point of failure mitigated by Redis health checks.

### ADR-006: ShuaiVM - JSON Payload Contract Engine

**Status:** Accepted
**Date:** 2026-01-15
**Context:** Need a simple but extensible smart contract system.
**Decision:** Implement a minimal VM that parses `payload` JSON. Supports `store` (KV state) and `mint_token` actions. No Turing-complete execution.
**Consequences:**
- Positive: No gas metering complexity. No reentrancy risk. Simple to audit.
- Negative: Limited expressiveness. WASM extension planned for complex logic.

---

*For terminology definitions, see [glossary.md](glossary.md).*
*For v1 to v2 migration details, see [architecture.md](architecture.md).*

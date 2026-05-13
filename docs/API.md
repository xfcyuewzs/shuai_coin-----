# ShuaiCoin RESTful API Specification

<!--
Version:     2.1.0
Last Updated: 2026-05-13
Author:      @api-team
Reviewer:    @core-team
-->

---

**Version** | **Date** | **Author** | **Changes**
2.1.0 | 2026-05-13 | @api-team | Complete RESTful specification rewrite
2.0.0 | 2026-04-30 | @api-team | Added async mining, node verify endpoints
1.0.0 | 2026-01-15 | @api-team | Initial API documentation

---

## 1. Overview

ShuaiCoin exposes a RESTful API over HTTP/1.1. All endpoints are served by Flask under the base URL:

```
http://<host>:<PORT>
```

### 1.1 Authentication

The API supports two authentication mechanisms:

| Method | Scope | How |
| :--- | :--- | :--- |
| **Session Cookie** | Web UI (`/login`) | `Set-Cookie: session=<signed>` |
| **JWT Bearer Token** | API clients (`/api/login`) | `Authorization: Bearer <token>` |

**JWT Structure:**

```json
{
  "exp": 1718230400,
  "iat": 1718144000,
  "sub": 1,
  "is_admin": true
}
```

* Algorithm: `HS256`
* TTL: 24 hours
* Secret: `config/settings.py::SECRET_KEY`

### 1.2 Unified Response Envelope

All API responses follow this structure:

```json
{
  "status": "success",
  "message": "Human-readable message",
  "data": {}
}
```

**Error Response:**

```json
{
  "status": "error",
  "message": "Human-readable error description",
  "data": null
}
```

### 1.3 Status Codes

| Code | Meaning | When |
| :--- | :--- | :--- |
| `200` | OK | Request succeeded |
| `201` | Created | Resource created (future) |
| `400` | Bad Request | Invalid input / missing parameters |
| `401` | Unauthorized | Missing or invalid credentials |
| `403` | Forbidden | Authenticated but insufficient permissions / account frozen |
| `404` | Not Found | Resource does not exist |
| `429` | Too Many Requests | Rate limit exceeded |
| `451` | Blocked | Content rejected by moderator |
| `500` | Internal Server Error | Unhandled server exception |

### 1.4 Pagination

Endpoints returning collections support cursor-based pagination:

**Request:**

```http
GET /api/chain?limit=20&offset=40
```

| Parameter | Type | Default | Max |
| :--- | :--- | :--- | :--- |
| `limit` | `integer` | `20` | `100` |
| `offset` | `integer` | `0` | N/A |

**Response:**

```json
{
  "status": "success",
  "data": {
    "items": [],
    "total": 1250,
    "limit": 20,
    "offset": 40
  }
}
```

### 1.5 Error Code Map

| `err_code` | HTTP Status | Description |
| :--- | :--- | :--- |
| `AUTH_001` | `401` | Token expired |
| `AUTH_002` | `401` | Invalid credentials |
| `AUTH_003` | `403` | Not an admin |
| `AUTH_004` | `403` | Account frozen |
| `VAL_001` | `400` | Missing required field |
| `VAL_002` | `400` | Invalid field type |
| `VAL_003` | `400` | Insufficient balance |
| `RATE_001` | `429` | Rate limit exceeded |
| `MOD_001` | `451` | Content blocked by moderator |
| `CHAIN_001` | `500` | Mining failed |
| `CHAIN_002` | `500` | Block creation failed |
| `NODE_001` | `400` | Node registration failed |

---

## 2. Authentication

### 2.1 POST /api/login

Obtain a JWT token for API access.

**Request:**

```http
POST /api/login
Content-Type: application/json

{
  "username": "admin",
  "password": "admin123"
}
```

**Response (200):**

```json
{
  "status": "success",
  "message": "Operation successful",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIs...",
    "username": "admin",
    "is_admin": true
  }
}
```

**Response (401):**

```json
{
  "status": "error",
  "message": "Invalid username or password",
  "data": null
}
```

### 2.2 POST /login

Web session-based login (form POST). Redirects to `/` on success.

**Request:**

```http
POST /login
Content-Type: application/x-www-form-urlencoded

username=admin&password=admin123
```

### 2.3 POST /register

Register a new user account.

**Request:**

```http
POST /register
Content-Type: application/x-www-form-urlencoded

username=new_user&password=secure_pass&tx_password=tx_secure_pass
```

### 2.4 GET /logout

Logout (Flask-Login `logout_user`).

---

## 3. Blockchain

### 3.1 GET /api/chain

Retrieve the full blockchain.

**Authentication:** None (public)

**Request:**

```http
GET /api/chain?limit=20&offset=0
```

**Response (200):**

```json
{
  "chain": [
    {
      "index": 1,
      "timestamp": 1718144000.123,
      "transactions": "[{...}]",
      "proof": 24581,
      "previous_hash": "0",
      "hash": "0000a1b2c3...",
      "difficulty": 4
    }
  ],
  "length": 142
}
```

### 3.2 GET /api/chain/block/<index\>

Retrieve a single block by index.

**Authentication:** None (public)

**Response (200):**

```json
{
  "status": "success",
  "data": {
    "index": 5,
    "timestamp": 1718144500.456,
    "transactions": "[{...}]",
    "proof": 98523,
    "previous_hash": "0000d4e5f6...",
    "hash": "0000f7a8b9...",
    "difficulty": 4
  }
}
```

**Response (404):**

```json
{
  "status": "error",
  "message": "Block not found",
  "data": null
}
```

---

## 4. Mining

### 4.1 GET /mine

Trigger synchronous mining. Returns block data immediately.

**Authentication:** Session required.
**Rate Limit:** 10 requests per minute.

**Request:**

```http
GET /mine
Cookie: session=...
```

**Response (200):**

```json
{
  "status": "success",
  "message": "Mining succeeded! Reward: 10.5 SHUAI",
  "data": {
    "index": 143,
    "reward": 10.5,
    "hash": "0000a1b2c3d4..."
  }
}
```

**Response (403):**

```json
{
  "status": "error",
  "message": "Your account has been frozen by the security center!",
  "data": null
}
```

### 4.2 POST /mine/async

Trigger asynchronous mining. Returns a `task_id` for status polling.

**Authentication:** Admin only (Session or JWT).
**Rate Limit:** 10 requests per minute.

**Request:**

```http
POST /mine/async
Authorization: Bearer eyJhbGciOi...
```

**Response (200):**

```json
{
  "status": "success",
  "message": "Mining task started",
  "data": {
    "task_id": "550e8400-e29b-41d4-a716-446655440000"
  }
}
```

### 4.3 GET /mine/status/<task_id\>

Poll asynchronous mining task status.

**Authentication:** Admin only.

**Request:**

```http
GET /mine/status/550e8400-e29b-41d4-a716-446655440000
```

**Response (200) - Processing:**

```json
{
  "status": "success",
  "data": {
    "status": "processing",
    "start_time": 1718144000.123
  }
}
```

**Response (200) - Completed:**

```json
{
  "status": "success",
  "data": {
    "status": "success",
    "block_index": 143,
    "reward": 10.5,
    "end_time": 1718144032.456
  }
}
```

**Response (404):**

```json
{
  "status": "error",
  "message": "Task not found",
  "data": null
}
```

---

## 5. Chain Verification

### 5.1 GET /verify

Verify local blockchain integrity. Checks hashes and previous-hash linkage.

**Authentication:** All logged-in users.
**Rate Limit:** 10 requests per minute.

**Response (200) - Healthy:**

```json
{
  "status": "success",
  "message": "Blockchain verification completed!",
  "data": {
    "corrupted_blocks": []
  }
}
```

**Response (200) - Corrupted:**

```json
{
  "status": "error",
  "message": "Warning: Chain data anomaly!",
  "data": {
    "corrupted_blocks": [45, 46, 47]
  }
}
```

---

## 6. Transactions

### 6.1 POST /api/transactions/new

Submit a new transaction to the mempool.

**Authentication:** None (public API).

**Request:**

```http
POST /api/transactions/new
Content-Type: application/json

{
  "sender": "0xabcd1234...",
  "recipient": "0xefgh5678...",
  "amount": 5.0,
  "fee": 0.1,
  "type": "transfer",
  "payload": ""
}
```

**Response (200):**

```json
{
  "status": "success",
  "message": "Transaction added to mempool",
  "data": {
    "tx_hash": "a1b2c3d4e5f6..."
  }
}
```

### 6.2 POST /transactions/new

Web form-based transaction submission (authenticated).

**Authentication:** Session required.

**Request:**

```http
POST /transactions/new
Content-Type: application/x-www-form-urlencoded

recipient=0xtarget&amount=5.0&fee=0.1&tx_password=user_tx_pass
```

---

## 7. Wallet

### 7.1 GET /api/wallet/<address\>

Query balance for a given address.

**Authentication:** None (public).

**Request:**

```http
GET /api/wallet/0xabcd1234abcd1234abcd1234abcd1234abcd1234
```

**Response (200):**

```json
{
  "status": "success",
  "data": {
    "address": "0xabcd1234abcd1234abcd1234abcd1234abcd1234",
    "balance": 150.25
  }
}
```

---

## 8. P2P Network

### 8.1 POST /api/p2p/register

Register peer nodes for P2P discovery.

**Authentication:** None (public).

**Request:**

```http
POST /api/p2p/register
Content-Type: application/json

{
  "nodes": [
    "http://192.168.1.100:5000",
    "http://192.168.1.101:5000"
  ]
}
```

**Response (200):**

```json
{
  "status": "success",
  "message": "Nodes added",
  "data": {
    "total_nodes": ["http://192.168.1.100:5000", "http://192.168.1.101:5000"]
  }
}
```

### 8.2 GET /api/p2p/resolve

Manually trigger chain conflict resolution (longest-chain consensus).

**Authentication:** None (public).

---

## 9. Admin

### 9.1 GET /admin/api/users

List all registered users.

**Authentication:** Admin only (Session or JWT).

**Response (200):**

```json
{
  "status": "success",
  "data": [
    {
      "id": 1,
      "username": "admin",
      "address": "0xADMIN_MASTER_WALLET",
      "is_admin": true,
      "is_frozen": false
    }
  ]
}
```

### 9.2 POST /admin/toggle_freeze/<user_id\>

Toggle account freeze status.

**Authentication:** Admin only (Session).

**Request:**

```http
POST /admin/toggle_freeze/3
Cookie: session=...
```

### 9.3 GET /admin/api/logs

Retrieve the last 100 admin audit log entries.

**Authentication:** Admin only.

**Response (200):**

```json
{
  "status": "success",
  "data": [
    {
      "id": 42,
      "admin_name": "admin",
      "action": "Froze user account: alice",
      "timestamp": "2026-05-13 10:30:00.123456"
    }
  ]
}
```

### 9.4 GET/POST /admin/api/config

View or update system configuration.

**Authentication:** Admin only.

**GET Response (200):**

```json
{
  "status": "success",
  "data": {
    "DIFFICULTY": 4,
    "BLOCK_REWARD": 10.0,
    "PORT": 5000
  }
}
```

### 9.5 POST /admin/api/nodes/verify

Verify external peer nodes asynchronously (TCP handshake + API health check).

**Authentication:** Admin only.
**Permission:** `node:verify`

**Request:**

```http
POST /admin/api/nodes/verify
Authorization: Bearer eyJhbGciOi...
Content-Type: application/json

{
  "nodes": [
    {"id": "node-1", "ip": "192.168.1.100", "port": 5000},
    {"id": "node-2", "ip": "192.168.1.101", "port": 5000}
  ]
}
```

**Response (200):**

```json
{
  "status": "success",
  "data": {
    "valid": [
      {"id": "node-1", "status": "UP"}
    ],
    "invalid": [
      {"id": "node-2", "reason": "Connection timeout"}
    ]
  }
}
```

---

## 10. Explorer

### 10.1 GET /explorer

Search blocks, transactions, or addresses.

**Authentication:** Session required.

**Request:**

```http
GET /explorer?q=123
GET /explorer?q=a1b2c3d4e5f67890abcdef1234567890abcdef1234567890abcdef1234567890
GET /explorer?q=0xabcd1234abcd1234abcd1234abcd1234abcd1234
```

### 10.2 GET /history

View personal transaction history.

**Authentication:** Session required.

### 10.3 GET /spa

Load the Single Page Application interface.

**Authentication:** Session required.

---

## 11. Rate Limiting

| Endpoint | Limit | Scope |
| :--- | :--- | :--- |
| `GET /mine` | 10/min | Per user |
| `POST /mine/async` | 10/min | Per admin |
| `GET /verify` | 10/min | Per user |
| `POST /api/login` | 20/min | Per IP |
| Global default | 200/min | Per IP |

Rate limit headers returned on all responses:

```http
X-RateLimit-Limit: 10
X-RateLimit-Remaining: 7
X-RateLimit-Reset: 1718144120
```

When exceeded, `429 Too Many Requests` is returned:

```json
{
  "status": "error",
  "message": "Rate limit exceeded. Try again in 45 seconds.",
  "data": null
}
```

---

## 12. Version Changelog

### v2.1.0 (2026-05-13)

| Change | Type | Endpoint | Compatibility |
| :--- | :--- | :--- | :--- |
| Added async mining | `add` | `POST /mine/async` | Backward compatible |
| Added mining status polling | `add` | `GET /mine/status/<task_id>` | Backward compatible |
| Added node verification | `add` | `POST /admin/api/nodes/verify` | Backward compatible |
| Unified response format | `modify` | All endpoints | **BREAKING** (new envelope) |
| Rate limiting headers | `add` | All endpoints | Backward compatible |

### v2.0.0 (2026-04-30)

| Change | Type | Endpoint | Compatibility |
| :--- | :--- | :--- | :--- |
| JWT auth support | `add` | `POST /api/login` | Backward compatible |
| `/verify` opened to all users | `modify` | `GET /verify` | Backward compatible |
| Non-redirect mine response | `modify` | `GET /mine` | **BREAKING** (JSON instead of redirect) |
| Added Swagger docs | `add` | `GET /apidocs` | Backward compatible |

### v1.0.0 (2026-01-15)

Initial release with Session-based authentication and synchronous mining.

---

*For terminology definitions, see [glossary.md](glossary.md).*

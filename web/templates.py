# shuai_coin/web/templates.py

BASE_HTML = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Shuai币 V2 核心网络</title>
    <!-- Element Plus & Vue 3 CDN -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/element-plus/dist/index.css">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/vue@3/dist/vue.global.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/element-plus"></script>
    <script src="https://cdn.jsdelivr.net/npm/axios/dist/axios.min.js"></script>
    <style> 
        .masked { font-family: monospace; background: #e9ecef; padding: 2px 6px; border-radius: 4px; } 
        body.dark-mode { background-color: #1a1a1a; color: #f0f0f0; }
        .dark-mode .card { background-color: #2d2d2d; border-color: #444; color: #f0f0f0; }
        .dark-mode .navbar { background-color: #000 !important; }
        .dark-mode .table { color: #f0f0f0; }
        .dark-mode .table-light { background-color: #3d3d3d; color: #fff; }
    </style>
</head>
<body class="bg-light">
    <div id="app_base">
        <nav class="navbar navbar-expand-lg navbar-dark bg-dark mb-4 shadow">
            <div class="container">
                <a class="navbar-brand" href="/">🪙 ShuaiCoin Ultimate</a>
                <div class="d-flex align-items-center">
                    {% if current_user.is_authenticated %}
                        <a href="/explorer" class="btn btn-outline-info btn-sm me-2">🔍 数据终端</a>
                        <a href="/history" class="btn btn-outline-light btn-sm me-2">📜 资产流水</a>
                        <a href="/spa" class="btn btn-outline-success btn-sm me-2">🚀 Web3 DApp</a>
                        {% if current_user.is_admin %}
                            <a href="/admin" class="btn btn-warning btn-sm me-2">⚙️ 节点管理</a>
                        {% endif %}
                        <button class="btn btn-sm btn-outline-secondary me-2" @click="toggleDarkMode">🌓</button>
                        <a href="/logout" class="btn btn-danger btn-sm">退出</a>
                    {% else %}
                        <a href="/login" class="btn btn-outline-light btn-sm me-2">节点接入</a>
                        <a href="/register" class="btn btn-primary btn-sm">创建钱包</a>
                    {% endif %}
                </div>
            </div>
        </nav>
        <div class="container">
            {% with messages = get_flashed_messages(with_categories=true) %}
              {% if messages %}{% for category, message in messages %}
                <div class="alert alert-{{ category }} alert-dismissible fade show shadow-sm">
                  {{ message }} <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                </div>
              {% endfor %}{% endif %}
            {% endwith %}
            {% block content %}{% endblock %}
        </div>
    </div>
    <script>
        const { createApp } = Vue;
        
        // 全局 Axios 拦截器
        axios.interceptors.request.use(config => {
            const token = localStorage.getItem('admin_token');
            if (token) config.headers.Authorization = `Bearer ${token}`;
            return config;
        });

        axios.interceptors.response.use(
            response => response,
            error => {
                if (error.response && (error.response.status === 401 || error.response.status === 403)) {
                    ElementPlus.ElMessage.error('登录失效或权限不足');
                    setTimeout(() => location.href = '/login', 1500);
                } else {
                    ElementPlus.ElMessage.error(error.response?.data?.msg || '服务器错误');
                }
                return Promise.reject(error);
            }
        );

        createApp({
            delimiters: ['[[', ']]'],
            data() {
                return { 
                    isDark: localStorage.getItem('dark-mode') === 'true',
                    verifyResult: null,
                    balance_val: null,
                    chain_list: []
                }
            },
            mounted() {
                if(this.isDark) document.body.classList.add('dark-mode');
                // 初始化时如果页面有初始数据，可以加载进来
                // 或者通过 API 加载
                this.refreshData();
            },
            methods: {
                toggleDarkMode() {
                    this.isDark = !this.isDark;
                    document.body.classList.toggle('dark-mode');
                    localStorage.setItem('dark-mode', this.isDark);
                },
                async refreshData() {
                    try {
                        const addr = '{{ current_user.address if current_user.is_authenticated else "" }}';
                        if (addr) {
                            const resBal = await fetch(`/api/wallet/${addr}`);
                            const dataBal = await resBal.json();
                            this.balance_val = dataBal.data.balance.toFixed(4);
                        }
                        const resChain = await fetch('/api/chain');
                        const dataChain = await resChain.json();
                        this.chain_list = dataChain.chain.slice(-8).reverse();
                    } catch (e) {
                        console.error("Failed to refresh data", e);
                    }
                },
                async handleMine() {
                    try {
                        const response = await fetch('/mine', {method: 'GET', credentials: 'same-origin'});
                        const result = await response.json();
                        if (response.ok && result.status === 'success') {
                            ElementPlus.ElMessage.success(result.message);
                            await this.refreshData();
                        } else {
                            ElementPlus.ElMessage.error(result.message || '挖矿失败');
                        }
                    } catch (error) {
                        ElementPlus.ElMessage.error('网络请求异常');
                    }
                },
                async handleVerify() {
                    try {
                        const response = await fetch('/verify', {method: 'GET', credentials: 'same-origin'});
                        const result = await response.json();
                        this.verifyResult = result;
                        if (response.ok) {
                            if (result.status === 'success') {
                                ElementPlus.ElMessage.success(result.message);
                            } else {
                                ElementPlus.ElMessage.error(result.message);
                            }
                        } else {
                            ElementPlus.ElMessage.error(result.message || '校验失败');
                        }
                    } catch (error) {
                        ElementPlus.ElMessage.error('网络请求异常');
                    }
                }
            }
        }).mount('#app_base');
    </script>
</body>
</html>
"""

INDEX_HTML = BASE_HTML.replace('{% block content %}{% endblock %}', """
<div class="row">
    <div class="col-md-5">
        <div class="card mb-4 shadow-sm border-primary">
            <div class="card-body text-center">
                {% if current_user.is_frozen %}
                    <div class="alert alert-danger">⚠️ 您的账户已被安全中心冻结！</div>
                {% endif %}
                <h5 class="text-muted">可用余额</h5>
                <h1 class="text-primary fw-bold">[[ balance_val || '{{ balance }}' ]] <small class="fs-6">SHUAI</small></h1>
                <p class="mb-3 text-muted small">地址: <span class="masked">{{ current_user.address }}</span></p>
                <button @click="handleMine" class="btn btn-success w-100 mb-2 {{ 'disabled' if current_user.is_frozen }}">⛏️ 提供算力挖矿</button>
                <button @click="handleVerify" class="btn btn-outline-secondary w-100">🛡️ 全网节点校验</button>
                
                <div id="verify-result" v-if="verifyResult" class="mt-3 text-start">
                    <el-alert
                        :title="verifyResult.message"
                        :type="verifyResult.status === 'success' ? 'success' : 'warning'"
                        :description="verifyResult.data && verifyResult.data.corrupted_blocks && verifyResult.data.corrupted_blocks.length ? '异常区块: ' + verifyResult.data.corrupted_blocks.join(', ') : ''"
                        show-icon>
                    </el-alert>
                </div>
            </div>
        </div>
        <div class="card shadow-sm mb-4">
            <div class="card-header bg-white fw-bold">发起链上交易</div>
            <div class="card-body">
                <form action="/transactions/new" method="POST">
                    <div class="mb-2"><input type="text" name="recipient" class="form-control" placeholder="接收方地址" required></div>
                    <div class="row mb-2">
                        <div class="col-8"><input type="number" step="0.01" name="amount" class="form-control" placeholder="转账金额" required></div>
                        <div class="col-4"><input type="number" step="0.01" name="fee" class="form-control" value="{{ config.MIN_FEE }}" required></div>
                    </div>
                    <div class="mb-3"><input type="password" name="tx_password" class="form-control border-danger" placeholder="🔒 交易密码(签名授权)" required></div>
                    <button type="submit" class="btn btn-primary w-100">签名并广播交易</button>
                </form>
            </div>
        </div>
    </div>
    <div class="col-md-7">
        <div class="card shadow-sm mb-3 border-info">
            <div class="card-header bg-info text-white fw-bold">全网实时数据监控</div>
            <div class="card-body row text-center">
                <div class="col-4"><h6>当前高度</h6><h4>{{ chain|length }}</h4></div>
                <div class="col-4"><h6>当前难度</h6><h4>{{ config.DIFFICULTY }}</h4></div>
                <div class="col-4"><h6>待确认交易</h6><h4 class="text-danger">{{ mempool_size }}</h4></div>
            </div>
        </div>
        <div class="card shadow-sm">
            <div class="card-header bg-dark text-white fw-bold">最新出块记录</div>
            <div class="card-body" style="max-height: 400px; overflow-y: auto;">
                <div v-if="chain_list.length === 0">
                    {% for block in chain %}
                    <div class="border-start border-4 border-dark p-2 mb-2 bg-white shadow-sm">
                        <div class="d-flex justify-content-between">
                            <span class="fw-bold text-primary">区块 #{{ block.index }}</span>
                            <span class="badge bg-secondary">难度: {{ block.difficulty }}</span>
                        </div>
                        <div class="small text-muted mt-1 text-truncate">哈希: {{ block.hash }}</div>
                    </div>
                    {% endfor %}
                </div>
                <div v-else>
                    <div v-for="block in chain_list" :key="block.index" class="border-start border-4 border-dark p-2 mb-2 bg-white shadow-sm">
                        <div class="d-flex justify-content-between">
                            <span class="fw-bold text-primary">区块 #[[ block.index ]]</span>
                            <span class="badge bg-secondary">难度: [[ block.difficulty ]]</span>
                        </div>
                        <div class="small text-muted mt-1 text-truncate">哈希: [[ block.hash ]]</div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
""")

AUTH_HTML = BASE_HTML.replace('{% block content %}{% endblock %}', """
<div class="row justify-content-center"><div class="col-md-5"><div class="card mt-5"><div class="card-header bg-primary text-white text-center py-3"><h4>{{ title }}</h4></div><div class="card-body"><form method="POST"><div class="mb-3"><label>用户名</label><input type="text" name="username" class="form-control" required></div><div class="mb-3"><label>登录密码</label><input type="password" name="password" class="form-control" required></div>{% if action == 'register' %}<div class="mb-4"><label class="text-danger fw-bold">交易密码 (转账专用)</label><input type="password" name="tx_password" class="form-control border-danger" required></div>{% endif %}<button type="submit" class="btn btn-primary w-100 btn-lg">{{ title }}</button></form></div></div></div></div>
""")

EXPLORER_HTML = BASE_HTML.replace('{% block content %}{% endblock %}', """
<div class="row mb-4">
    <div class="col-md-6"><div class="card bg-primary text-white p-3 shadow"><h5>全网总产出</h5><h3>{{ supply }} SHUAI</h3></div></div>
    <div class="col-md-6"><div class="card bg-success text-white p-3 shadow"><h5>历史总交易笔数</h5><h3>{{ total_txs }} 笔</h3></div></div>
</div>
<div class="card shadow-sm mb-4">
    <div class="card-body">
        <form method="GET" action="/explorer" class="d-flex">
            <input type="text" name="q" class="form-control me-2" placeholder="搜索 区块高度 / 区块哈希 / 交易哈希 / 钱包地址" value="{{ request.args.get('q', '') }}">
            <button type="submit" class="btn btn-dark px-4">全网搜索</button>
        </form>
    </div>
</div>
{% if result %}
    <div class="alert alert-info">{{ result_msg }}</div>
    <pre class="bg-dark text-light p-3 rounded" style="white-space: pre-wrap;">{{ data }}</pre>
{% endif %}
""")

HISTORY_HTML = BASE_HTML.replace('{% block content %}{% endblock %}', """
<h3 class="mb-4">📜 资产流水明细</h3>
<div class="card shadow-sm">
    <table class="table table-hover align-middle mb-0">
        <thead class="table-light"><tr><th>时间</th><th>交易类型</th><th>金额变动</th><th>手续费</th><th>交易哈希</th></tr></thead>
        <tbody>
            {% for tx in txs %}
            <tr>
                <td>{{ tx.timestamp.strftime('%Y-%m-%d %H:%M') }}</td>
                <td><span class="badge bg-secondary">{{ tx.tx_type }}</span></td>
                <td class="fw-bold {{ 'text-danger' if tx.sender == current_user.address else 'text-success' }}">
                    {{ '-' if tx.sender == current_user.address else '+' }}{{ tx.amount }}
                </td>
                <td>{{ tx.fee }}</td>
                <td class="small masked" title="{{ tx.tx_hash }}">{{ mask(tx.tx_hash) }}</td>
            </tr>
            {% else %}
            <tr><td colspan="5" class="text-center text-muted py-4">暂无任何交易记录</td></tr>
            {% endfor %}
        </tbody>
    </table>
</div>
""")

ADMIN_HTML = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>管理员控制台 - ShuaiCoin</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/element-plus/dist/index.css">
    <script src="https://cdn.jsdelivr.net/npm/vue@3/dist/vue.global.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/element-plus"></script>
    <script src="https://cdn.jsdelivr.net/npm/axios/dist/axios.min.js"></script>
    <style>
        .el-header { background-color: #409EFF; color: white; display: flex; align-items: center; justify-content: space-between; }
        .el-aside { background-color: #f4f4f5; height: calc(100vh - 60px); }
        .admin-main { padding: 20px; }
        .log-area { margin-top: 20px; border-top: 1px solid #eee; padding-top: 10px; font-size: 12px; color: #666; }
    </style>
</head>
<body>
    <div id="admin_app">
        <el-container>
            <el-header>
                <div style="font-weight: bold; font-size: 18px;">🛡️ ShuaiCoin 管理员系统</div>
                <div>
                    <el-button type="info" size="small" @click="goHome">返回主站</el-button>
                    <el-button type="danger" size="small" @click="logout">退出</el-button>
                </div>
            </el-header>
            <el-container>
                <el-aside width="200px">
                    <el-menu default-active="1" @select="handleSelect">
                        <el-menu-item index="1">📊 系统概览</el-menu-item>
                        <el-menu-item index="2">👥 用户列表</el-menu-item>
                        <el-menu-item index="3">📝 内容审核</el-menu-item>
                        <el-menu-item index="4">🔑 权限管理</el-menu-item>
                        <el-menu-item index="5">🖥️ 日志监控</el-menu-item>
                        <el-menu-item index="6">⚙️ 配置中心</el-menu-item>
                    </el-menu>
                </el-aside>
                <el-main class="admin-main">
                    <el-breadcrumb separator="/">
                      <el-breadcrumb-item>管理后台</el-breadcrumb-item>
                      <el-breadcrumb-item>{% raw %}{{ currentMenuName }}{% endraw %}</el-breadcrumb-item>
                    </el-breadcrumb>
                    
                    <div v-if="activeTab === '1'">
                        <el-row :gutter="20" style="margin-top: 20px;">
                            <el-col :span="8"><el-card shadow="hover">区块高度: {% raw %}{{ stats.height }}{% endraw %}</el-card></el-col>
                            <el-col :span="8"><el-card shadow="hover">总交易数: {% raw %}{{ stats.total_transactions }}{% endraw %}</el-card></el-col>
                            <el-col :span="8"><el-card shadow="hover">当前难度: {{ config.DIFFICULTY }}</el-card></el-col>
                        </el-row>
                    </div>

                    <div v-if="activeTab === '2'" style="margin-top: 20px;">
                        <el-table :data="users" style="width: 100%" stripe border>
                            <el-table-column prop="username" label="用户名"></el-table-column>
                            <el-table-column prop="address" label="钱包地址" show-overflow-tooltip></el-table-column>
                            <el-table-column label="状态">
                                <template #default="scope">
                                    <el-tag :type="scope.row.is_frozen ? 'danger' : 'success'">
                                        {% raw %}{{ scope.row.is_frozen ? '已冻结' : '正常' }}{% endraw %}
                                    </el-tag>
                                </template>
                            </el-table-column>
                            <el-table-column label="操作">
                                <template #default="scope">
                                    <el-button size="small" :type="scope.row.is_frozen ? 'success' : 'warning'" @click="toggleFreeze(scope.row)">
                                        {% raw %}{{ scope.row.is_frozen ? '解冻' : '冻结' }}{% endraw %}
                                    </el-button>
                                </template>
                            </el-table-column>
                        </el-table>
                    </div>

                    <div v-if="activeTab === '5'" style="margin-top: 20px;">
                        <el-table :data="logs" style="width: 100%" height="400">
                            <el-table-column prop="timestamp" label="时间" width="180"></el-table-column>
                            <el-table-column prop="admin_name" label="管理员" width="120"></el-table-column>
                            <el-table-column prop="action" label="操作内容"></el-table-column>
                        </el-table>
                    </div>
                    
                    <div class="log-area">
                        <strong>最近操作记录 (Real-time):</strong>
                        <ul>
                            <li v-for="log in logs.slice(0, 20)" :key="log.id">
                                {% raw %}[{{ log.timestamp }}] {{ log.admin_name }}: {{ log.action }}{% endraw %}
                            </li>
                        </ul>
                    </div>
                </el-main>
            </el-container>
        </el-container>
    </div>
    <script>
        const { createApp } = Vue;

        // 全局 Axios 拦截器
        axios.interceptors.request.use(config => {
            const token = localStorage.getItem('admin_token');
            if (token) config.headers.Authorization = `Bearer ${token}`;
            return config;
        });

        axios.interceptors.response.use(
            response => response,
            error => {
                if (error.response && (error.response.status === 401 || error.response.status === 403)) {
                    ElementPlus.ElMessage.error('登录失效或权限不足');
                    setTimeout(() => location.href = '/login', 1500);
                } else {
                    ElementPlus.ElMessage.error(error.response?.data?.msg || '服务器错误');
                }
                return Promise.reject(error);
            }
        );

        createApp({
            data() {
                return {
                    activeTab: '1',
                    currentMenuName: '系统概览',
                    users: [],
                    logs: [],
                    stats: {},
                    config: {}
                }
            },
            mounted() {
                this.fetchStats();
                this.fetchUsers();
                this.fetchLogs();
                this.fetchConfig();
            },
            methods: {
                handleSelect(key) {
                    this.activeTab = key;
                    const names = {'1':'系统概览', '2':'用户列表', '3':'内容审核', '4':'权限管理', '5':'日志监控', '6':'配置中心'};
                    this.currentMenuName = names[key];
                },
                async fetchStats() {
                    // 模拟从后端 API 获取
                    this.stats = { height: 100, total_transactions: 1250 };
                },
                async fetchUsers() {
                    const res = await axios.get('/admin/api/users');
                    this.users = res.data.data;
                },
                async fetchLogs() {
                    const res = await axios.get('/admin/api/logs');
                    this.logs = res.data.data;
                },
                async fetchConfig() {
                    const res = await axios.get('/admin/api/config');
                    this.config = res.data.data;
                },
                async toggleFreeze(user) {
                    // 这里对接原有的同步 POST 路由或新增 API
                    location.href = `/admin/toggle_freeze/${user.id}`;
                },
                goHome() { location.href = '/'; },
                logout() { location.href = '/logout'; }
            }
        }).use(ElementPlus).mount('#admin_app');
    </script>
</body>
</html>
"""

SPA_HTML = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>ShuaiChain DApp</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/axios/dist/axios.min.js"></script>
</head>
<body class="bg-light">
    <nav class="navbar navbar-dark bg-dark mb-4"><div class="container"><span class="navbar-brand">🌐 Web3 DApp</span><a href="/" class="btn btn-sm btn-outline-light">返回主站</a></div></nav>
    <div class="container">
        <div class="row">
            <div class="col-md-5">
                <div class="card p-4 mb-4">
                    <h5>输入钱包地址授权</h5>
                    <input type="text" id="walletInput" class="form-control mb-3">
                    <button class="btn btn-primary w-100" onclick="login()">连接</button>
                    <h2 class="mt-3 text-success"><span id="balance">0.00</span> SHUAI</h2>
                </div>
                <div class="card p-4 border-info">
                    <h5 class="text-info">智能合约 (ShuaiVM)</h5>
                    <input type="text" id="scKey" class="form-control mb-2" placeholder="键">
                    <input type="text" id="scValue" class="form-control mb-2" placeholder="值">
                    <button class="btn btn-info text-white w-100" onclick="deployContract()">写入链上状态</button>
                </div>
            </div>
            <div class="col-md-7">
                <div class="card p-4 mb-4">
                    <h5>P2P 同步控制台</h5>
                    <div class="input-group mb-2"><input type="text" id="peerUrl" class="form-control" placeholder="127.0.0.1:5001"><button class="btn btn-secondary" onclick="addPeer()">添加 Peer</button></div>
                    <button class="btn btn-danger w-100" onclick="syncP2P()">强制拉取全网最长链</button>
                </div>
            </div>
        </div>
    </div>
    <script>
        let wallet = "";
        function login() { wallet = document.getElementById('walletInput').value; refreshData(); }
        async function refreshData() {
            const res = await axios.get(`/api/wallet/${wallet}`);
            document.getElementById('balance').innerText = res.data.data.balance.toFixed(2);
        }
        async function deployContract() {
            const tx = { sender: wallet, recipient: "0xCONTRACT_" + Date.now(), amount: 0, fee: 0.1, type: 'deploy_contract', payload: JSON.stringify({ action: "store", key: document.getElementById('scKey').value, value: document.getElementById('scValue').value }) };
            await axios.post('/api/transactions/new', tx); alert("智能合约部署已广播");
        }
        async function addPeer() { await axios.post('/api/p2p/register', { nodes: [document.getElementById('peerUrl').value] }); alert("节点已添加"); }
        async function syncP2P() { const res = await axios.get('/api/p2p/resolve'); alert(res.data.message); }
    </script>
</body>
</html>
"""

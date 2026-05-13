import json
from time import time
from datetime import datetime
from flask import Blueprint, render_template_string, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from werkzeug.security import check_password_hash

from db import db
from db.models import Block, Transaction, User, AdminLog
from core.blockchain import create_block, proof_of_work, get_pending_transactions
from core.utils import calculate_balance, generate_tx_hash
from config.settings import Config
from p2p.network import resolve_conflicts, register_node, network_peers
from core.response import success_res, error_res
from security.auth import admin_required, require_permission

# 导入所有 HTML 模板
from web.templates import INDEX_HTML, SPA_HTML, EXPLORER_HTML, HISTORY_HTML, ADMIN_HTML

routes_bp = Blueprint('routes', __name__)


from security.anti_ddos import limiter
import uuid
import threading
import logging

# 异步任务追踪
mining_tasks = {}

# ================= 首页与基本功能 =================
@routes_bp.route('/')
@login_required
def index():
    pending_txs = get_pending_transactions()
    balance = calculate_balance(current_user.address, pending_txs=pending_txs)
    chain = Block.query.order_by(Block.index.desc()).limit(8).all()
    return render_template_string(INDEX_HTML, balance=round(balance, 4), chain=chain,
                                  mempool_size=len(pending_txs))


def log_api_call(endpoint, status_code, start_time):
    duration = (time() - start_time) * 1000
    logging.info(f"API_CALL | {endpoint} | {request.method} | {current_user.id if current_user.is_authenticated else 'anon'} | {request.remote_addr} | {status_code} | {duration:.2f}ms")

@routes_bp.route('/mine')
@login_required
@limiter.limit("10 per minute")
def mine():
    start_t = time()
    if current_user.is_frozen: 
        log_api_call('mine', 403, start_t)
        return jsonify({"status": "error", "message": "您的账户已被安全中心冻结！", "data": None}), 403
    
    last_block = Block.query.order_by(Block.index.desc()).first()
    if not last_block:
        log_api_call('mine', 400, start_t)
        return jsonify({"status": "error", "message": "区块链尚未初始化", "data": None}), 400
    
    try:
        proof = proof_of_work(last_block.proof, Config.DIFFICULTY)
        new_block, fees = create_block(proof, last_block.hash, current_user.address)
        
        log_api_call('mine', 200, start_t)
        return jsonify({
            "status": "success", 
            "message": f"⛏️ 挖矿成功！获得 {Config.BLOCK_REWARD + fees} SHUAI",
            "data": {
                "index": new_block.index,
                "reward": Config.BLOCK_REWARD + fees,
                "hash": new_block.hash
            }
        }), 200
    except Exception as e:
        logging.error(f"Mining failed: {str(e)}")
        return jsonify({"status": "error", "message": f"挖矿失败: {str(e)}", "data": None}), 500


@routes_bp.route('/mine/async', methods=['POST'])
@admin_required
@limiter.limit("10 per minute")
def mine_async():
    """
    异步挖矿接口 (仅限管理员)
    ---
    tags:
      - Node Management
    responses:
      200:
        description: 挖矿任务已启动
        schema:
          properties:
            code: {type: integer, example: 0}
            data: {properties: {task_id: {type: string}}}
    """
    start_t = time()
    task_id = str(uuid.uuid4())
    mining_tasks[task_id] = {"status": "processing", "start_time": time()}
    
    miner_address = current_user.address
    
    def background_mining(app_context, tid, addr):
        with app_context:
            try:
                last_block = Block.query.order_by(Block.index.desc()).first()
                proof = proof_of_work(last_block.proof, Config.DIFFICULTY)
                new_block, fees = create_block(proof, last_block.hash, addr)
                mining_tasks[tid] = {
                    "status": "success", 
                    "block_index": new_block.index,
                    "reward": Config.BLOCK_REWARD + fees,
                    "end_time": time()
                }
            except Exception as e:
                logging.error(f"Async mining failed: {str(e)}", exc_info=True)
                mining_tasks[tid] = {"status": "failed", "error": str(e)}

    from flask import current_app
    thread = threading.Thread(target=background_mining, args=(current_app.app_context(), task_id, miner_address))
    thread.start()
    
    log_api_call('mine_async', 200, start_t)
    return success_res({"task_id": task_id}, msg="Mining task started")


@routes_bp.route('/mine/status/<task_id>', methods=['GET'])
@admin_required
def mine_status(task_id):
    """
    查询异步挖矿进度 (仅限管理员)
    ---
    tags:
      - Node Management
    parameters:
      - name: task_id
        in: path
        type: string
        required: true
    responses:
      200:
        description: 任务状态
    """
    start_t = time()
    task = mining_tasks.get(task_id)
    if not task:
        log_api_call(f'mine_status/{task_id}', 404, start_t)
        return error_res("Task not found", status_code=404)
    log_api_call(f'mine_status/{task_id}', 200, start_t)
    return success_res(task)


@routes_bp.route('/verify', methods=['GET', 'POST'])
@login_required
@limiter.limit("10 per minute")
def verify_chain():
    """
    校验本地链完整性 (普通用户也可调用)
    """
    start_t = time()
    blocks = Block.query.order_by(Block.index.asc()).all()
    corrupted_blocks = []
    
    from core.utils import hash_block
    
    for i in range(len(blocks)):
        block = blocks[i]
        block_dict = {
            'index': block.index,
            'timestamp': block.timestamp,
            'transactions': json.loads(block.transactions),
            'proof': block.proof,
            'previous_hash': block.previous_hash,
            'difficulty': block.difficulty
        }
        if block.hash != hash_block(block_dict):
            corrupted_blocks.append(block.index)
            continue
            
        if i > 0:
            if block.previous_hash != blocks[i-1].hash:
                corrupted_blocks.append(block.index)

    if corrupted_blocks:
        log_api_call('verify', 200, start_t)
        return jsonify({
            "status": "error",
            "message": "警告：链数据异常！",
            "data": {"corrupted_blocks": corrupted_blocks}
        }), 200
    
    log_api_call('verify', 200, start_t)
    return jsonify({
        "status": "success",
        "message": "区块链校验完成！",
        "data": {"corrupted_blocks": []}
    }), 200


@routes_bp.route('/transactions/new', methods=['POST'])
@login_required
def new_transaction():
    if current_user.is_frozen: return redirect(url_for('routes.index'))
    amount = float(request.form['amount'])
    fee = float(request.form['fee'])

    if not check_password_hash(current_user.tx_password_hash, request.form['tx_password']):
        flash('交易密码错误', 'danger')
        return redirect(url_for('routes.index'))

    pending_txs = get_pending_transactions()
    if calculate_balance(current_user.address, pending_txs) < (amount + fee):
        flash('余额不足', 'warning')
        return redirect(url_for('routes.index'))

    tx_hash = generate_tx_hash(current_user.address, request.form['recipient'], amount, fee, time())
    
    new_tx = Transaction(
        tx_hash=tx_hash, sender=current_user.address, recipient=request.form['recipient'],
        amount=amount, fee=fee, tx_type='transfer', block_index=None
    )
    db.session.add(new_tx)
    db.session.commit()
    
    flash('✅ 交易已入池等待打包', 'info')
    return redirect(url_for('routes.index'))


# ================= 页面路由 (修复 404) =================
@routes_bp.route('/explorer')
@login_required
def explorer():
    # 统计信息
    total_supply = db.session.query(db.func.sum(Transaction.amount)).filter_by(tx_type='mine').scalar() or 0.0
    total_txs = Transaction.query.count()

    q = request.args.get('q', '').strip()
    result, data, msg = False, "", ""

    if q:
        result = True
        if q.isdigit():
            block = Block.query.filter_by(index=int(q)).first()
            if block:
                data, msg = f"区块哈希: {block.hash}\n难度: {block.difficulty}\n交易数: {len(json.loads(block.transactions))}\n时间: {block.timestamp}", "✅ 找到区块"
        elif len(q) == 64:
            tx = Transaction.query.filter_by(tx_hash=q).first()
            if tx:
                data, msg = f"发送方: {tx.sender}\n接收方: {tx.recipient}\n金额: {tx.amount}\n手续费: {tx.fee}\n区块高度: {tx.block_index}", "✅ 找到交易"
            else:
                blk = Block.query.filter_by(hash=q).first()
                if blk: data, msg = f"高度: {blk.index}\n前序哈希: {blk.previous_hash}", "✅ 找到区块"
        else:
            txs = Transaction.query.filter((Transaction.sender == q) | (Transaction.recipient == q)).count()
            data, msg = f"地址: {q}\n余额: {calculate_balance(q, get_pending_transactions())}\n参与交易笔数: {txs}", "✅ 找到地址统计信息"

        if not data:
            msg = "🚫 404 - 全网链上未找到该数据"

    return render_template_string(EXPLORER_HTML, supply=total_supply, total_txs=total_txs, result=result, data=data,
                                  result_msg=msg)


@routes_bp.route('/history')
@login_required
def history():
    from core.utils import mask_address
    txs = Transaction.query.filter(
        (Transaction.sender == current_user.address) | (Transaction.recipient == current_user.address)
    ).order_by(Transaction.id.desc()).all()
    return render_template_string(HISTORY_HTML, txs=txs, mask=mask_address)


@routes_bp.route('/spa')
@login_required
def spa():
    return render_template_string(SPA_HTML)


@routes_bp.route('/admin')
@login_required
def admin():
    if not current_user.is_admin:
        flash('🚫 无权限访问管理员控制台', 'danger')
        return redirect(url_for('routes.index'))
    return render_template_string(ADMIN_HTML)


@routes_bp.route('/admin/toggle_freeze/<int:user_id>', methods=['POST', 'GET'])
@login_required
def toggle_freeze(user_id):
    if not current_user.is_admin:
        flash('🚫 无权限执行此操作', 'danger')
        return redirect(url_for('routes.index'))
        
    u = User.query.get(user_id)
    if u:
        u.is_frozen = not u.is_frozen
        action = "冻结" if u.is_frozen else "解冻"
        # 记录不可篡改日志
        log = AdminLog(admin_name=current_user.username, action=f"{action}了用户账户: {u.username}")
        db.session.add(log)
        db.session.commit()
        flash(f'已成功{action}用户 {u.username}', 'success')
    return redirect(url_for('routes.admin'))


# ================= 管理员 API (JWT 鉴权) =================
@routes_bp.route('/admin/api/users', methods=['GET'])
@admin_required
def admin_get_users():
    """
    获取所有用户列表 (管理员)
    ---
    tags:
      - Admin
    security:
      - Bearer: []
    responses:
      200:
        description: 用户列表
    """
    users = User.query.all()
    user_list = [{"id": u.id, "username": u.username, "address": u.address, "is_admin": u.is_admin, "is_frozen": u.is_frozen} for u in users]
    return success_res(user_list)

@routes_bp.route('/admin/api/logs', methods=['GET'])
@admin_required
def admin_get_logs():
    """
    获取系统操作日志 (管理员)
    ---
    tags:
      - Admin
    security:
      - Bearer: []
    """
    logs = AdminLog.query.order_by(AdminLog.id.desc()).limit(100).all()
    log_list = [{"id": l.id, "admin_name": l.admin_name, "action": l.action, "timestamp": str(l.timestamp)} for l in logs]
    return success_res(log_list)

@routes_bp.route('/admin/api/config', methods=['GET', 'POST'])
@admin_required
def admin_config():
    """
    系统配置管理 (管理员)
    ---
    tags:
      - Admin
    """
    if request.method == 'POST':
        data = request.get_json()
        # 这里可以扩展持久化配置逻辑
        return success_res(msg="配置更新成功 (模拟)")
    
    return success_res({
        "DIFFICULTY": Config.DIFFICULTY,
        "BLOCK_REWARD": Config.BLOCK_REWARD,
        "PORT": Config.PORT
    })


# ================= RESTful API (供P2P和SPA调用) =================
@routes_bp.route('/api/chain', methods=['GET'])
def get_chain():
    """
    获取全网区块数据
    ---
    tags:
      - Blockchain
    """
    blocks = Block.query.order_by(Block.index.asc()).all()
    chain = [{'index': b.index, 'timestamp': b.timestamp, 'transactions': b.transactions,
              'proof': b.proof, 'previous_hash': b.previous_hash, 'hash': b.hash, 'difficulty': b.difficulty} for b in
             blocks]
    return jsonify({'chain': chain, 'length': len(chain)}), 200


@routes_bp.route('/api/wallet/<address>', methods=['GET'])
def get_wallet(address):
    """
    查询地址余额
    ---
    tags:
      - Wallet
    """
    bal = calculate_balance(address, get_pending_transactions())
    return success_res({'address': address, 'balance': bal})

@routes_bp.route('/api/transactions/new', methods=['POST'])
def api_new_tx():
    """
    API 发起新交易
    ---
    tags:
      - Transaction
    """
    data = request.get_json()
    if not data: return error_res("Invalid data")
    
    tx_hash = generate_tx_hash(data['sender'], data['recipient'], float(data['amount']), float(data['fee']), time(), data.get('payload', ''))
    new_tx = Transaction(
        tx_hash=tx_hash, sender=data['sender'], recipient=data['recipient'],
        amount=float(data['amount']), fee=float(data['fee']), tx_type=data.get('type', 'transfer'),
        payload=data.get('payload', ''), block_index=None
    )
    db.session.add(new_tx)
    db.session.commit()
    return success_res({'tx_hash': tx_hash}, msg="Transaction added to mempool")

@routes_bp.route('/api/p2p/register', methods=['POST'])
def api_register_nodes():
    nodes = request.get_json().get('nodes')
    if nodes:
        for node in nodes: register_node(node)
    return success_res({'total_nodes': list(network_peers)}, msg="Nodes added")

import aiohttp
import asyncio
import socket

# ... 现有导入 ...

@routes_bp.route('/admin/api/nodes/verify', methods=['POST'])
@admin_required
@require_permission('node:verify')
async def verify_external_nodes():
    """
    全网节点异步校验
    ---
    tags:
      - Admin
    """
    data = request.get_json()
    nodes = data.get('nodes', [])
    
    results = {"valid": [], "invalid": []}
    
    async def verify_single_node(node):
        target = f"{node['ip']}:{node['port']}"
        start_time = time()
        
        try:
            # 1. TCP 握手校验 (使用 socket 模拟超时)
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(0.2)
                s.connect((node['ip'], int(node['port'])))
            
            # 2. API 校验 (aiohttp)
            async with aiohttp.ClientSession() as session:
                async with session.get(f"http://{target}/api/chain", timeout=2.0) as resp:
                    if resp.status == 200:
                        chain_data = await resp.json()
                        local_height = Block.query.count()
                        remote_height = chain_data.get('length', 0)
                        
                        if abs(local_height - remote_height) <= 3:
                            results["valid"].append({"id": node['id'], "status": "UP"})
                            return
                        else:
                            results["invalid"].append({"id": node['id'], "reason": "Height out of sync"})
                    else:
                        results["invalid"].append({"id": node['id'], "reason": f"HTTP {resp.status}"})
        except Exception as e:
            results["invalid"].append({"id": node['id'], "reason": str(e)})

    # 并发控制
    sem = asyncio.Semaphore(100)
    async def sem_verify(node):
        async with sem:
            await verify_single_node(node)

    await asyncio.gather(*[sem_verify(n) for n in nodes])
    
    return success_res(results)

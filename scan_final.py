#!/usr/bin/env python3
"""scan_final.py - Fixed dependency graph"""
import os, ast
from collections import defaultdict

BASE = r'.'
SKIP_DIRS = {'.git', '.idea', '__pycache__', '.pytest_cache', 'node_modules', '.vscode', 'logs', 'logs_test', 'instance', 'backup', '.github'}

path2mod = {}
mod2path = {}
for root, dirs, files in os.walk(BASE):
    dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
    for f in files:
        if not f.endswith('.py'):
            continue
        rp = os.path.relpath(os.path.join(root, f), BASE).replace(os.sep, '/')
        fp = './' + rp
        mod = rp[:-3].replace('/', '.')
        if mod.endswith('.__init__'):
            mod = mod[:-9]
        path2mod[fp] = mod
        mod2path[mod] = fp
        if mod:
            mod2path[mod] = fp

def resolve_target(target):
    """Resolve module 'core.blockchain' -> ['./core/blockchain.py']"""
    results = []
    parts = target.split('.')
    # 1. Exact module match
    if target in mod2path:
        results.append(mod2path[target])
    # 2. As __init__.py
    init_path = '/'.join(parts) + '/__init__.py'
    fp = './' + init_path
    if os.path.exists(fp):
        results.append(fp)
    # 3. As .py file
    file_path = '/'.join(parts) + '.py'
    fp = './' + file_path
    if os.path.exists(fp):
        results.append(fp)
    return results

imports_fp = defaultdict(set)
for fp in path2mod:
    try:
        tree = ast.parse(open(fp, 'r', encoding='utf-8', errors='ignore').read())
    except:
        continue
    targets = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            targets.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            base = node.module or ''
            lvl = node.level
            if lvl > 0:
                cur_mod = path2mod.get(fp, '')
                parts = cur_mod.split('.')
                if lvl <= len(parts):
                    base = '.'.join(parts[:-lvl]) + ('.' + base if base else '')
            if base:
                targets.append(base)
    for t in targets:
        resolved = resolve_target(t)
        for rf in resolved:
            imports_fp[fp].add(rf)

entry_fps = ['./run.py', './cli/main.py', './web/__init__.py']
entry_fps = [f for f in entry_fps if os.path.exists(f)]
print(f'入口: {entry_fps}')

visited_fps = set()
queue = list(entry_fps)
while queue:
    fp = queue.pop(0)
    if fp in visited_fps:
        continue
    visited_fps.add(fp)
    for dep_fp in imports_fp.get(fp, set()):
        if dep_fp not in visited_fps and os.path.exists(dep_fp):
            queue.append(dep_fp)

all_py_files = set(path2mod.keys())
unused_py = all_py_files - visited_fps

print(f'Python: {len(all_py_files)} total / {len(visited_fps)} reachable / {len(unused_py)} orphan')
print()
print('=== 可达模块 ===')
for fp in sorted(visited_fps):
    deps = imports_fp.get(fp, set())
    internal = [d for d in deps if d in visited_fps]
    mod = path2mod.get(fp, '?')
    print(f'  {mod:30s}  -> {[path2mod.get(d, d.split("/")[-1]) for d in internal[:8]]}')

print()
print('=== 孤儿模块 (未被入口引用) ===')
orphan_by_dir = defaultdict(list)
orphan_total = 0
for fp in sorted(unused_py):
    sz = os.path.getsize(fp)
    orphan_total += sz
    d = '/'.join(fp.split('/')[1:-1]) or '(root)'
    orphan_by_dir[d].append((fp, sz))

for d in sorted(orphan_by_dir.keys()):
    items = orphan_by_dir[d]
    subtotal = sum(sz for _, sz in items)
    print(f'  [{d}/]  {len(items)} files, {subtotal/1024:.1f} KB')
    for fp, sz in items:
        mod = path2mod.get(fp, '?')
        print(f'    - {fp.split("/")[-1]:30s} ({mod})')

print(f'\n孤儿总计: {orphan_total/1024:.1f} KB')

# === Cleanup summary ===
print()
print('='*60)
print('清理候选清单')
print('='*60)

all_files = []
for root, dirs, files in os.walk(BASE):
    dirs[:] = [d for d in dirs if d not in {'.git', '.idea'}]
    for f in files:
        rp = os.path.relpath(os.path.join(root, f), BASE).replace(os.sep, '/')
        if rp.startswith('scan_'):
            continue
        all_files.append('./' + rp)

def size(paths):
    return sum(os.path.getsize(p) for p in paths if os.path.exists(p))

cleanup_groups = {
    'A. 日志文件': [f for f in all_files if 'logs/' in f or f.endswith('.log')],
    'B. 数据库文件': [f for f in all_files if 'instance/' in f or '.db' in f],
    'C. 备份文件': [f for f in all_files if '.bak' in f or '.backup' in f],
    'D. __pycache__': [f for f in all_files if '__pycache__' in f],
    'E. 临时索引': [f for f in all_files if f.endswith('文件目录.txt')],
    'F. 空白__init__': [fp for fp in unused_py if fp.endswith('__init__.py') and size([fp]) == 0],
    'G. 孤儿功能模块': [fp for fp in unused_py if not fp.endswith('__init__.py') or size([fp]) > 0],
    'H. 扫描脚本': ['./scan_project.py', './scan_v2.py', './scan_final.py', './scan_result.json'],
}

total_all = size(all_files)
total_del = 0
for label, files in cleanup_groups.items():
    sz = size(files)
    if sz == 0 and not files:
        continue
    total_del += sz
    print(f'  {label}: {len(files)} files, {sz/1024:.1f} KB')

print(f'\n项目总大小: {total_all/1024:.1f} KB')
print(f'可删除总计: {total_del/1024:.1f} KB ({total_del/total_all*100:.1f}%)')
print(f'删除后大小: {(total_all-total_del)/1024:.1f} KB')
print(f'缩减比例: {total_del/total_all*100:.1f}%')

# Check test reachability
test_files = [fp for fp in all_files if 'tests/' in fp and fp.endswith('.py')]
test_reachable = [fp for fp in test_files if fp in visited_fps]
print(f'\n测试文件: {len(test_files)} total, {len(test_reachable)} reachable from entry points')

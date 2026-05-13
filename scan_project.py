#!/usr/bin/env python3
"""scan_project.py - 全项目文件清单扫描 + 依赖关系分析"""
import os, json, re, ast
from collections import defaultdict

BASE = r'.'
EXCLUDE_DIRS = {'.git', '.idea', '__pycache__', '.pytest_cache', 'node_modules', '.vscode', 'logs', 'backup', 'instance'}

# ========== 阶段1: 文件清单 ==========
file_inventory = []
dir_map = defaultdict(list)

for root, dirs, files in os.walk(BASE):
    dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
    for f in files:
        fp = os.path.join(root, f).replace(os.sep, '/')
        try:
            size = os.path.getsize(fp)
        except OSError:
            size = 0
        ext = os.path.splitext(f)[1].lower()
        file_inventory.append({'path': fp, 'size': size, 'ext': ext, 'name': f})
        dir_map[root.replace(os.sep, '/')].append(f)

file_inventory.sort(key=lambda x: x['size'], reverse=True)
total_size = sum(x['size'] for x in file_inventory)

print(f'=== 文件清单 ({len(file_inventory)} 个文件, {total_size/1024/1024:.2f} MB) ===')
print()
for d in sorted(dir_map.keys()):
    print(f'  {d}/  ({len(dir_map[d])} files)')

print()
print('--- 最大的 20 个文件 ---')
for fi in file_inventory[:20]:
    print(f'  {fi["path"]:65s}  {fi["size"]/1024:8.1f} KB')

# ========== 阶段2: Python import 依赖分析 ==========
print()
print('=== 阶段2: Python import 依赖分析 ===')

all_modules = set()
for fi in file_inventory:
    if fi['ext'] == '.py' and not fi['path'].startswith('./tests/'):
        mod = fi['path'][2:-3].replace('/', '.')
        all_modules.add(mod)
    elif fi['ext'] == '.py' and fi['path'].startswith('./tests/'):
        mod = fi['path'][2:-3].replace('/', '.')
        all_modules.add(mod)

imports_graph = defaultdict(set)
for fi in file_inventory:
    if fi['ext'] != '.py':
        continue
    if fi['path'] in ('./__init__.py',):
        continue
    try:
        with open(fi['path'], 'r', encoding='utf-8', errors='ignore') as fh:
            source = fh.read()
    except:
        continue
    try:
        tree = ast.parse(source)
    except:
        continue
    current_mod = fi['path'][2:-3].replace('/', '.')
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports_graph[current_mod].add(alias.name.split('.')[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports_graph[current_mod].add(node.module.split('.')[0])

# Find entry points
entry_points = ['run', 'web', 'tests']
used_modules = set()

def dfs(mod):
    if mod in used_modules:
        return
    used_modules.add(mod)
    for imp in imports_graph.get(mod, set()):
        if imp in imports_graph or imp in all_modules:
            dfs(imp)

for ep in entry_points:
    dfs(ep)

# Also mark test files as used if they import project modules
for mod in all_modules:
    if mod.startswith('tests.'):
        used_modules.add(mod)

print(f'  入口模块: {entry_points}')
print(f'  总 Python 模块: {len(all_modules)}')
print(f'  被引用模块: {len(used_modules)}')

orphan_modules = all_modules - used_modules
orphan_files = []

for fi in file_inventory:
    if fi['ext'] != '.py':
        continue
    mod = fi['path'][2:-3].replace('/', '.')
    if mod in orphan_modules:
        orphan_files.append(fi)

print(f'  孤儿模块: {len(orphan_modules)}')

# ========== 阶段3: 其他可疑文件 ==========
print()
print('=== 阶段3: 其他可疑文件识别 ===')

# Identify large non-code files
large_non_code = [fi for fi in file_inventory if fi['size'] > 50*1024 and fi['ext'] not in ('.py', '.md')]
print(f'  大文件 (>50KB, 非代码/文档): {len(large_non_code)}')
for fi in large_non_code:
    print(f'    {fi["path"]}  ({fi["size"]/1024:.1f} KB)')

# Check for duplicate/similar files
print()
print('=== 阶段4: 疑似重复/冗余文件 ===')

# Check PYXCACHE files
pycache_files = [fi for fi in file_inventory if '__pycache__' in fi['path']]
print(f'  __pycache__ 下的文件: {len(pycache_files)}')

# Check for .db files
db_files = [fi for fi in file_inventory if fi['ext'] == '.db']
print(f'  数据库文件: {len(db_files)}')
for fi in db_files:
    print(f'    {fi["path"]}  ({fi["size"]/1024:.1f} KB)')

# Check for log files
log_files = [fi for fi in file_inventory if fi['ext'] == '.log']
print(f'  日志文件: {len(log_files)}')
for fi in log_files:
    print(f'    {fi["path"]}  ({fi["size"]/1024:.1f} KB)')

# Check for .bak files
bak_files = [fi for fi in file_inventory if fi['ext'] == '.bak']
print(f'  备份文件: {len(bak_files)}')
for fi in bak_files:
    print(f'    {fi["path"]}  ({fi["size"]/1024:.1f} KB)')

# Check for special files
special_files = [fi for fi in file_inventory if fi['name'] in ('文件目录.txt',)]
print(f'  特殊文件: {len(special_files)}')
for fi in special_files:
    print(f'    {fi["path"]}  ({fi["size"]/1024:.1f} KB)')

# Save results
output = {
    'total_files': len(file_inventory),
    'total_size_mb': total_size / 1024 / 1024,
    'orphan_modules': sorted(list(orphan_modules)),
    'large_non_code': [{'path': f['path'], 'size_kb': f['size']/1024} for f in large_non_code],
    'db_files': [f['path'] for f in db_files],
    'log_files': [f['path'] for f in log_files],
    'bak_files': [f['path'] for f in bak_files],
    'special_files': [f['path'] for f in special_files],
}
with open('scan_result.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print()
print('=== 扫描结果已保存至 scan_result.json ===')

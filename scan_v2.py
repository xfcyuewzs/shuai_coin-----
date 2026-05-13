#!/usr/bin/env python3
"""scan_v2.py - 精确依赖分析 (full module path resolution)"""
import os, ast, sys
from collections import defaultdict

BASE = r'.'
EXCLUDE_DIRS = {'.git', '.idea', '__pycache__', '.pytest_cache', 'node_modules', '.vscode'}

# Build reverse: relative_path -> module_name
path_to_mod = {}
mod_to_path = {}

for root, dirs, files in os.walk(BASE):
    dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
    for f in files:
        if not f.endswith('.py'):
            continue
        fp = os.path.join(root, f).replace(os.sep, '/')
        if fp == './scan_project.py' or fp == './scan_v2.py':
            continue
        rel = fp[2:]
        mod = rel[:-3].replace('/', '.')
        path_to_mod[fp] = mod
        mod_to_path[mod] = fp

all_py_files = set(path_to_mod.keys())
all_mods = set(path_to_mod.values())

# Parse every Python file and extract ALL imports (fully qualified)
imports_graph = defaultdict(set)  # module -> set of imported modules
used_files = set()

for fp, mod in path_to_mod.items():
    try:
        with open(fp, 'r', encoding='utf-8', errors='ignore') as fh:
            source = fh.read()
    except:
        continue
    try:
        tree = ast.parse(source)
    except:
        continue
    used_files.add(fp)
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                full = alias.name
                imports_graph[mod].add(full)
        elif isinstance(node, ast.ImportFrom):
            base = node.module or ''
            level = node.level  # relative import level
            if level > 0:
                parts = mod.split('.')
                if level <= len(parts):
                    base = '.'.join(parts[:-(level)]) + ('.' + base if base else '')
            for alias in node.names:
                full = base + '.' + alias.name if base else alias.name
                imports_graph[mod].add(full)

# Resolve: given a module string, find all actual files that could match
def resolve_module(target):
    """Find all .py files that match the target module path"""
    results = set()
    # exact match
    if target in mod_to_path:
        results.add(mod_to_path[target])
    # also match packages (e.g. 'core' matches 'core/__init__.py')
    init_path = target.replace('.', '/') + '/__init__.py'
    if init_path in path_to_mod:
        results.add(init_path)
    # check sub-modules: if target is 'core', also resolve all 'core.xxx'
    for fp1, mod1 in path_to_mod.items():
        if mod1 == target or mod1.startswith(target + '.'):
            results.add(fp1)
    return results

# Walk from entry points
entry_files = set()
for ep_base in ['run.py', 'web/__init__.py', 'cli/main.py']:
    fp = './' + ep_base
    if fp in path_to_mod:
        entry_files.add(fp)

print(f'入口文件: {entry_files}')

# BFS traversal
visited_mods = set()
queue = list(entry_files)

while queue:
    fp = queue.pop(0)
    if fp in visited_mods:
        continue
    visited_mods.add(fp)
    mod = path_to_mod.get(fp)
    if not mod:
        continue
    for imported in imports_graph.get(mod, set()):
        resolved = resolve_module(imported)
        for rf in resolved:
            if rf not in visited_mods:
                queue.append(rf)

print(f'总 py 文件: {len(all_py_files)}')
print(f'可达 py 文件: {len(visited_mods)}')

unused = all_py_files - visited_mods

# ========== Check special categories ==========
print()
print('=== 按目录统计未引用文件 ===')
unused_by_dir = defaultdict(list)
for fp in sorted(unused):
    d = '/'.join(fp.split('/')[:-1])
    unused_by_dir[d].append(fp)

for d in sorted(unused_by_dir.keys()):
    files = unused_by_dir[d]
    total = sum(os.path.getsize(f) for f in files)
    print(f'  {d}/  ({len(files)} files, {total/1024:.1f} KB)')
    for f in files:
        print(f'    {f.split("/")[-1]}')

# ========== Check other file types ==========
print()
print('=== 非 Python 文件 ===')
other_files = []
for root, dirs, files in os.walk(BASE):
    dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
    for f in files:
        fp = os.path.join(root, f).replace(os.sep, '/')
        if fp.startswith('./scan') or fp.startswith('./_'):
            continue
        if not f.endswith('.py'):
            other_files.append(fp)

for f in sorted(other_files):
    sz = os.path.getsize(f) if os.path.exists(f) else 0
    print(f'  {f}  ({sz/1024:.1f} KB)')

# ========== Identify deletable candidates ==========
print()
print('=== 待删除候选 ===')
print()
print('A. 孤儿 Python 模块:')
delete_candidates = []
for fp in sorted(unused):
    sz = os.path.getsize(fp)
    delete_candidates.append(('orphan_py', fp, sz))
    print(f'  [orphan] {fp}  ({sz}B)')

# For non-Python files, check if they are referenced by any used code
used_file_content = ''
for fp in visited_mods:
    try:
        with open(fp, 'r', encoding='utf-8', errors='ignore') as fh:
            used_file_content += fh.read()
    except:
        pass

print()
print('B. 未被引用的非 Python 文件:')
for fp in sorted(other_files):
    name = fp.split('/')[-1]
    # Check if referenced anywhere in used code
    if name in used_file_content or name.replace('.', r'\.') in used_file_content:
        continue
    # Common config files that are always needed
    if name in ('requirements.txt', 'Dockerfile', 'docker-compose.yml',
                '.pre-commit-config.yaml', 'CODEOWNERS', '.gitignore', 'CACHEDIR.TAG'):
        continue
    sz = os.path.getsize(fp)
    delete_candidates.append(('unreferenced', fp, sz))
    print(f'  [unref] {fp}  ({sz}B)')

# Calculate savings
orphan_size = sum(sz for cat, fp, sz in delete_candidates if cat == 'orphan_py')
unref_size = sum(sz for cat, fp, sz in delete_candidates if cat == 'unreferenced')
total_del_size = orphan_size + unref_size
total_proj_size = sum(os.path.getsize(fp) for fp in all_py_files) + sum(os.path.getsize(fp) for fp in other_files if os.path.exists(fp))

print()
print(f'=== 清理预估 ===')
print(f'  项目总大小: {total_proj_size/1024:.1f} KB')
print(f'  可删除文件数: {len(delete_candidates)}')
print(f'  孤儿模块大小: {orphan_size/1024:.1f} KB')
print(f'  未引用文件大小: {unref_size/1024:.1f} KB')
print(f'  预计释放: {total_del_size/1024:.1f} KB ({total_del_size/total_proj_size*100:.1f}%)')

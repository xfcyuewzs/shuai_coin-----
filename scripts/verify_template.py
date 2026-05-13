from jinja2 import Environment, Template
import sys

try:
    with open('web/templates.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 模拟从 templates.py 中提取 ADMIN_HTML
    # 这里我们直接执行 templates.py 并获取变量
    namespace = {}
    exec(content, namespace)
    admin_html = namespace.get('ADMIN_HTML')
    
    if admin_html:
        Template(admin_html)
        print("✅ ADMIN_HTML template compiled successfully")
    else:
        print("❌ ADMIN_HTML not found in templates.py")
        
except Exception as e:
    print(f"❌ Template compilation failed: {e}")
    sys.exit(1)

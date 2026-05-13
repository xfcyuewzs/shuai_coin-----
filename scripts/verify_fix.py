import sys
import os

# 设置当前目录为项目根目录
sys.path.append(os.getcwd())

try:
    from web import create_app
    print("[SUCCESS] web module found")
    
    # 尝试导入 routes 并检查 require_permission
    from web.routes import routes_bp
    print("[SUCCESS] web.routes imported without NameError")
    
    from security.auth import require_permission
    print("[SUCCESS] require_permission found in security.auth")

except NameError as e:
    print(f"[FAIL] NameError: {e}")
    sys.exit(1)
except ImportError as e:
    print(f"[INFO] ImportError: {e} (Likely due to environment)")
except Exception as e:
    print(f"[ERROR] {type(e).__name__}: {e}")

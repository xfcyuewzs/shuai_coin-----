import requests
import time

BASE_URL = "http://127.0.0.1:5000"

def test_endpoints():
    endpoints = [
        ("/", 200),
        ("/explorer", 200),
        ("/history", 200),
        ("/spa", 200),
        ("/admin", 200),
        ("/api/chain", 200),
        ("/apidocs/", 200),
    ]
    
    # 注意：这些页面需要登录，所以在测试前我们需要先模拟登录或者在测试模式下运行
    # 这里我们只检查接口是否注册（如果返回 302 重定向到登录页，也说明路由存在）
    
    print("--- Web Endpoint Verification ---")
    for path, expected in endpoints:
        try:
            url = f"{BASE_URL}{path}"
            res = requests.get(url, allow_redirects=False, timeout=5)
            status = res.status_code
            # 如果重定向到登录页 (302)，说明路由已注册且受保护
            result = "PASS" if status in [expected, 302] else "FAIL"
            print(f"Path: {path:15} | Status: {status} | Result: {result}")
        except Exception as e:
            print(f"Path: {path:15} | Error: {str(e)}")

if __name__ == "__main__":
    # 提醒：运行此脚本前请确保 run.py 已启动
    print("Ensure 'python run.py' is running in another terminal.")
    test_endpoints()

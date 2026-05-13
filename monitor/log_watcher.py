import time
import json
import os
import requests
import logging

# 告警配置
ALERT_WEBHOOK = "https://ops.example.com/alert"
LOG_DIR = "logs"
ERROR_THRESHOLD = 10
CRITICAL_THRESHOLD = 1
WINDOW_SIZE = 60 # 1分钟

def watch_logs():
    print("👀 Log watcher started...")
    last_positions = {}
    
    while True:
        try:
            error_count = 0
            critical_count = 0
            recent_logs = []

            for filename in os.listdir(LOG_DIR):
                if not filename.endswith(".log"): continue
                
                path = os.path.join(LOG_DIR, filename)
                with open(path, 'r', encoding='utf-8') as f:
                    # 移动到上次读取的位置
                    f.seek(last_positions.get(path, 0))
                    
                    for line in f:
                        try:
                            entry = json.loads(line)
                            level = entry.get("level")
                            if level == "ERROR": error_count += 1
                            if level == "CRITICAL": critical_count += 1
                            recent_logs.append(entry)
                        except: continue
                    
                    last_positions[path] = f.tell()

            # 检查告警阈值
            if error_count >= ERROR_THRESHOLD or critical_count >= CRITICAL_THRESHOLD:
                print(f"🚨 Threshold reached! Errors: {error_count}, Criticals: {critical_count}")
                payload = {
                    "alert": "Log anomaly detected",
                    "error_count": error_count,
                    "critical_count": critical_count,
                    "recent_logs": recent_logs[-50:] # 附带最近50条
                }
                try:
                    requests.post(ALERT_WEBHOOK, json=payload, timeout=5)
                except: pass

        except Exception as e:
            print(f"Error in watcher: {e}")
            
        time.sleep(WINDOW_SIZE)

if __name__ == '__main__':
    watch_logs()

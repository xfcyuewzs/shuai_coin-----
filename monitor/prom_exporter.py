from prometheus_client import start_http_server, Gauge
from web import create_app
from db.models import Block, Transaction
import time

# 定义指标
BLOCK_HEIGHT = Gauge('shuai_coin_block_height', 'Current block height of the chain')
TOTAL_TXS = Gauge('shuai_coin_total_transactions', 'Total number of transactions on chain')

app = create_app()

def update_metrics():
    while True:
        with app.app_context():
            height = Block.query.count()
            txs = Transaction.query.count()
            BLOCK_HEIGHT.set(height)
            TOTAL_TXS.set(txs)
        time.sleep(15) # 每15秒抓取一次

if __name__ == '__main__':
    start_http_server(8000) # 暴露在 8000 端口，供 Prometheus 拉取
    print("📊 Prometheus Metrics Exporter running on port 8000")
    update_metrics()
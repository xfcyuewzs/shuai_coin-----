import click
import requests

NODE_URL = "http://127.0.0.1:5000"

@click.group()
def cli():
    """🪙 ShuaiCoin CLI 节点管理工具"""
    pass

@cli.command()
def info():
    """查看全网状态"""
    try:
        res = requests.get(f"{NODE_URL}/api/chain", timeout=3)
        if res.status_code == 200:
            data = res.json()
            click.secho(f"✅ 当前网络高度: {data['length']}", fg="green")
            click.secho(f"🔗 节点地址: {NODE_URL}", fg="blue")
    except:
        click.secho("❌ 节点离线，请确认 run.py 是否启动", fg="red")

# 导入并添加其他子命令组
from .wallet_cli import wallet
cli.add_command(wallet)

if __name__ == '__main__':
    cli()

import click
import requests
import json
from .main import NODE_URL

@click.group()
def wallet():
    """👛 钱包操作命令"""
    pass

@wallet.command()
@click.argument('username')
def create(username):
    """创建一个新钱包地址"""
    res = requests.post(f"{NODE_URL}/register", data={
        'username': username,
        'password': 'default_password',
        'tx_password': 'default_tx_password'
    })
    if res.status_code == 200:
        click.secho(f"✅ 钱包创建成功: {username}", fg="green")
    else:
        click.secho("❌ 创建失败", fg="red")

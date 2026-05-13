TRANSLATIONS = {
    'zh': {
        'title': 'Shuai币核心网络',
        'balance': '可用余额',
        'mine': '开始挖矿',
        'send': '发送交易',
        'address': '钱包地址'
    },
    'en': {
        'title': 'ShuaiCoin Core Network',
        'balance': 'Available Balance',
        'mine': 'Start Mining',
        'send': 'Send Transaction',
        'address': 'Wallet Address'
    }
}

def get_text(key, lang='zh'):
    """简单的国际化文本获取工具"""
    return TRANSLATIONS.get(lang, TRANSLATIONS['zh']).get(key, key)

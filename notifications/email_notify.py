def send_email(subject, body, recipient):
    """
    发送邮件通知 (例如大额交易或节点异常)
    (此处为逻辑占位，实际需配置 SMTP 服务)
    """
    print(f"[EMAIL_NOTIFY] To: {recipient} | Subject: {subject}")

def alert_large_transaction(sender, amount):
    subject = "⚠️ 大额交易预警"
    body = f"地址 {sender} 刚刚发起了一笔金额为 {amount} SHUAI 的交易。"
    send_email(subject, body, "admin@shuaicoin.com")

# -*- coding: utf-8 -*-
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import smtplib
import json
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header

# 加载配置（邮箱配置.json 包含敏感信息，已通过 .gitignore 排除）
# 使用时请：cp 配置/邮箱配置.example.json 配置/邮箱配置.json 并填入真实 SMTP 信息
config_path = os.path.join(os.path.dirname(__file__), "配置", "邮箱配置.json")
if not os.path.exists(config_path):
    example_path = config_path.replace(".json", ".example.json")
    raise FileNotFoundError(
        f"未找到邮箱配置: {config_path}\n"
        f"请复制模板: {example_path}\n"
        f"并填入真实的 SMTP 授权码。"
    )
with open(config_path, "r", encoding="utf-8") as f:
    config = json.load(f)

def send_email(subject, body_md_path, to_email=None):
    """发送邮件，将 MD 文件内容作为正文"""

    # 读取 MD 文件
    with open(body_md_path, "r", encoding="utf-8") as f:
        md_content = f.read()

    if to_email is None:
        to_email = config["recipient_email"]

    # 构造邮件
    msg = MIMEMultipart("alternative")
    msg["From"] = f'{config["sender_name"]} <{config["sender_email"]}>'
    msg["To"] = to_email
    msg["Subject"] = Header(subject, "utf-8")

    # 纯文本 + HTML 双版本
    html_content = md_content.replace("\n", "<br>\n")
    msg.attach(MIMEText(md_content, "plain", "utf-8"))
    msg.attach(MIMEText(html_content, "html", "utf-8"))

    try:
        server = smtplib.SMTP_SSL(config["smtp_server"], config["smtp_port"])
        server.login(config["sender_email"], config["auth_code"])
        server.sendmail(config["sender_email"], to_email, msg.as_string())
        server.quit()
        print(f"[OK] Email sent to {to_email}")
        return True
    except Exception as e:
        print(f"[FAIL] Email send failed: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("用法: python send_email.py <邮件主题> <MD文件路径> [收件人]")
        sys.exit(1)

    subject = sys.argv[1]
    body_path = sys.argv[2]
    recipient = sys.argv[3] if len(sys.argv) > 3 else None

    send_email(subject, body_path, recipient)

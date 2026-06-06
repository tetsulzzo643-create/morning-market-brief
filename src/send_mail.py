"""
send_mail.py — Gmail SMTP でメール送信するモジュール
"""
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def send_gmail(subject: str, body: str) -> None:
    """
    環境変数から送信情報を読み込んで Gmail で送信する。

    必要な環境変数:
        GMAIL_ADDRESS     — 送信元・送信先 Gmail アドレス
        GMAIL_APP_PASSWORD — Gmail アプリパスワード
        MAIL_TO           — 宛先アドレス（複数可、カンマ区切り）
    """
    gmail_address  = os.environ["GMAIL_ADDRESS"]
    app_password   = os.environ["GMAIL_APP_PASSWORD"]
    mail_to        = os.environ["MAIL_TO"]

    recipients = [addr.strip() for addr in mail_to.split(",") if addr.strip()]

    msg = MIMEMultipart()
    msg["From"]    = gmail_address
    msg["To"]      = ", ".join(recipients)
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain", "utf-8"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(gmail_address, app_password)
        server.sendmail(gmail_address, recipients, msg.as_string())

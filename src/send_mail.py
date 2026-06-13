"""
send_mail.py — Gmail SMTP でメール送信するモジュール
"""
import os
import smtplib
import sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def send_gmail(subject: str, body: str) -> None:
    """
    環境変数から送信情報を読み込んで Gmail で送信する。

    必要な環境変数:
        GMAIL_ADDRESS      — 送信元 Gmail アドレス
        GMAIL_APP_PASSWORD — Gmail アプリパスワード（Googleアカウント→セキュリティ→アプリパスワード）
        MAIL_TO            — 宛先アドレス（複数可、カンマ区切り）
    """
    missing = [v for v in ("GMAIL_ADDRESS", "GMAIL_APP_PASSWORD", "MAIL_TO") if not os.environ.get(v)]
    if missing:
        print(f"[ERROR] 以下の環境変数が設定されていません: {', '.join(missing)}", file=sys.stderr)
        raise EnvironmentError(f"Missing environment variables: {missing}")

    gmail_address = os.environ["GMAIL_ADDRESS"]
    app_password  = os.environ["GMAIL_APP_PASSWORD"]
    mail_to       = os.environ["MAIL_TO"]

    recipients = [addr.strip() for addr in mail_to.split(",") if addr.strip()]

    msg = MIMEMultipart()
    msg["From"]    = gmail_address
    msg["To"]      = ", ".join(recipients)
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain", "utf-8"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(gmail_address, app_password)
            server.sendmail(gmail_address, recipients, msg.as_string())
    except smtplib.SMTPAuthenticationError:
        print(
            "[ERROR] Gmail SMTP 認証失敗 (535)。GMAIL_APP_PASSWORD が無効または失効しています。\n"
            "  → Googleアカウント → セキュリティ → アプリパスワード で再発行し、\n"
            "    GitHub リポジトリ → Settings → Secrets → GMAIL_APP_PASSWORD を更新してください。",
            file=sys.stderr,
        )
        raise
    except smtplib.SMTPException as e:
        print(f"[ERROR] Gmail 送信エラー: {e}", file=sys.stderr)
        raise

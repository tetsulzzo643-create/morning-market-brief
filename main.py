"""
main.py — 朝の市況レポート自動配信スクリプト

使い方:
    python main.py            # メール送信
    python main.py --dry-run  # 本文を標準出力のみ（送信しない）
"""
import argparse
import datetime
import sys

sys.stdout.reconfigure(encoding="utf-8")

from dotenv import load_dotenv

load_dotenv()

from src.collect import market_data as collect_data  # テーマ変更時はここを書き換え
from src.summarize import summarize
from src.send_mail import send_gmail


def main() -> None:
    parser = argparse.ArgumentParser(description="朝の市況レポートを生成・送信する")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="メール送信せず、本文を標準出力に表示する",
    )
    args = parser.parse_args()

    print("市況データを収集しています...")
    raw = collect_data()

    print("Claude で要約しています...")
    body = summarize(raw)

    today   = datetime.date.today().strftime("%Y年%m月%d日")
    subject = f"【朝の市況レポート】{today}"

    if args.dry_run:
        print("\n" + "=" * 60)
        print(f"件名: {subject}")
        print("=" * 60)
        print(body)
        print("=" * 60)
        print("\n[dry-run] メールは送信されませんでした。")
        return

    print("Gmail で送信しています...")
    send_gmail(subject=subject, body=body)
    print("送信完了。")


if __name__ == "__main__":
    main()

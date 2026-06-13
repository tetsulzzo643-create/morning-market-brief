"""
summarize.py — Claude API で市況データを要約するモジュール

使用モデルは環境変数 MODEL で切り替え可能。
デフォルトはコスト重視の claude-haiku-4-5-20251001。
"""
import os
import sys

import anthropic

MODEL_DEFAULT = "claude-haiku-4-5-20251001"

SYSTEM_PROMPT = """あなたは市場アナリストです。
提供された市況データを読み取り、投資家向けの朝の市況レポートを作成してください。
- 読みやすい日本語で箇条書きと見出しを使って整理してください
- 前日比で目立つ動きがあれば強調してください
- 余計な前置きや「以下に」等の冗長な文句は不要です
- 500〜700字程度を目安にまとめてください"""


def summarize(raw_data: str) -> str:
    """
    raw_data: collect.py が返した生データ文字列
    戻り値: Claude が生成した要約テキスト
    """
    model = os.environ.get("MODEL", MODEL_DEFAULT)
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("[ERROR] ANTHROPIC_API_KEY が設定されていません。GitHub Secret を確認してください。", file=sys.stderr)
        raise EnvironmentError("ANTHROPIC_API_KEY is not set")

    client = anthropic.Anthropic()

    try:
        response = client.messages.create(
            model=model,
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": f"以下の市況データを要約してください。\n\n{raw_data}",
                }
            ],
        )
    except anthropic.AuthenticationError:
        print("[ERROR] Claude API 認証失敗 (401)。ANTHROPIC_API_KEY が無効または失効しています。GitHub Secret を更新してください。", file=sys.stderr)
        raise
    except anthropic.APIStatusError as e:
        print(f"[ERROR] Claude API エラー (HTTP {e.status_code}): {e.message}", file=sys.stderr)
        raise

    return response.content[0].text

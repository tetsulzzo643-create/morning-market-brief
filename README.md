# morning-market-brief

毎朝 6:05（JST）に市況レポートを Gmail で自動配信するテンプレートです。  
GitHub Actions + Claude API（Haiku）+ yfinance を使用します。

---

## 必要なもの

| 項目 | 説明 |
|---|---|
| **Anthropic API キー** | [console.anthropic.com](https://console.anthropic.com) でアカウント作成 → API Keys |
| **Gmail アドレス** | 送信に使う Google アカウント |
| **Gmail アプリパスワード** | 通常のパスワードではなく専用パスワードが必要（下記参照） |
| **送信先メールアドレス** | 自分自身でも他のアドレスでも可（複数可） |

### Anthropic API キーの取得

1. [console.anthropic.com](https://console.anthropic.com) にアクセス
2. サインアップまたはログイン
3. 左メニュー「API Keys」→「Create Key」
4. 生成されたキーをコピーして安全な場所に保管

### Gmail アプリパスワードの取得

アプリパスワードは 2 段階認証が有効なアカウントでのみ発行できます。

1. Google アカウントにログイン → [myaccount.google.com/security](https://myaccount.google.com/security)
2. 「2 段階認証プロセス」を有効化（まだの場合）
3. 検索バーで「アプリパスワード」と検索 → 「アプリパスワード」を開く
4. アプリ名（例: `morning-market-brief`）を入力 → 「作成」
5. 表示された 16 文字のパスワードをコピー（スペースなし）

---

## ローカルでの動作確認（--dry-run）

メール送信は行わず、生成されたレポート本文をターミナルに表示します。

```bash
# 1. リポジトリをクローン
git clone https://github.com/your-username/morning-market-brief.git
cd morning-market-brief

# 2. 依存パッケージをインストール
pip install -r requirements.txt

# 3. .env ファイルを作成
cp .env.example .env
# エディタで .env を開き、各変数に値を入力

# 4. dry-run で動作確認
python main.py --dry-run
```

`.env` の記入例:

```
ANTHROPIC_API_KEY=sk-ant-api03-xxxxx
GMAIL_ADDRESS=yourname@gmail.com
GMAIL_APP_PASSWORD=abcd efgh ijkl mnop
MAIL_TO=yourname@gmail.com
```

> **注意:** `.env` ファイルは `.gitignore` に含まれているため、コミットされません。  
> アプリパスワードのスペースは含めても含めなくても動作します。

---

## GitHub Secrets への登録手順

GitHub Actions で定期実行するには、シークレットに API キー等を登録する必要があります。

1. GitHub でリポジトリを開く
2. **Settings** → **Secrets and variables** → **Actions** → **New repository secret**
3. 以下の 4 つを順番に登録する：

| シークレット名 | 値 |
|---|---|
| `ANTHROPIC_API_KEY` | Anthropic の API キー |
| `GMAIL_ADDRESS` | 送信元 Gmail アドレス |
| `GMAIL_APP_PASSWORD` | Gmail アプリパスワード（スペースなし） |
| `MAIL_TO` | 宛先メールアドレス（複数はカンマ区切り） |

### 手動実行で動作確認

登録後、**Actions** タブ → **Morning Market Brief** → **Run workflow** で即時実行できます。

---

## カスタマイズ

### 使用モデルの変更

デフォルトは `claude-haiku-4-5-20251001`（高速・低コスト）です。  
より高品質なレポートにしたい場合は GitHub Secrets に `MODEL` を追加します：

| シークレット名 | 値の例 |
|---|---|
| `MODEL` | `claude-sonnet-4-6` |

または `brief.yml` の `env:` ブロックを直接編集してください。

### 配信テーマの変更

`src/collect.py` の末尾「テーマ差し替えガイド」を参照してください。  
関数 1 つを差し替えるだけで、仮想通貨・マクロ経済・株式セクター等に切り替えられます。

### 配信時刻の変更

`.github/workflows/brief.yml` の `cron` 行を編集します。  
**cron は UTC 基準**であることに注意してください。

```yaml
# 例: JST 7:00 = UTC 22:00 の場合
- cron: "0 22 * * *"
```

---

## ファイル構成

```
morning-market-brief/
├── .github/workflows/brief.yml  # GitHub Actions 定義
├── src/
│   ├── collect.py               # 市況データ取得
│   ├── summarize.py             # Claude API で要約
│   └── send_mail.py             # Gmail 送信
├── main.py                      # エントリポイント（--dry-run 対応）
├── .env.example                 # 環境変数テンプレート
├── requirements.txt
└── LICENSE (MIT)
```

---

## ライセンス

MIT License — 自由に改変・再配布できます。

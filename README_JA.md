<div align="center">

<img src="docs/assets/logo.png" alt="VidGen Logo" width="160" style="border-radius: 20px; box-shadow: 0 4px 20px rgba(0,0,0,0.15);" />

# VidGen 🎨⚡

**本番環境対応のオープンソース AI ビデオ＆画像生成プラットフォーム**

[![Live Demo](https://img.shields.io/badge/ライブデモ-vidgenerator.ai-0070f3?style=for-the-badge&logo=google-chrome&logoColor=white)](https://vidgenerator.ai)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Nuxt 3](https://img.shields.io/badge/Nuxt-3.x-00DC82?style=for-the-badge&logo=nuxt.js&logoColor=white)](https://nuxt.com/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Async-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![PRs Welcome](https://img.shields.io/badge/PRs-Welcome-brightgreen.svg?style=for-the-badge)](.github/CONTRIBUTING.md)

[English](README.md) | [简体中文](README_CN.md) | [日本語](README_JA.md) | [한국어](README_KO.md) | [Español](README_ES.md) | [Português](README_PT.md)

</div>

<p align="center">
  <a href="https://vidgenerator.ai"><b>🚀 ライブデモ</b></a> •
  <a href="#-主な機能"><b>✨ 主な機能</b></a> •
  <a href="#️-技術スタック一覧"><b>🛠️ 技術スタック</b></a> •
  <a href="#-クイックスタート指南"><b>⚡ クイックスタート</b></a> •
  <a href="#-ディレクトリ構造"><b>📁 ディレクトリ構造</b></a>
</p>

---

> 🚀 **商用実績（Battle-Tested）**：VidGen は、商用運用サービス [vidgenerator.ai](https://vidgenerator.ai) のコアエンジンとして稼働しています。

## 🌟 プロジェクト概要

**VidGen** は、クリエイター、エンジニア、起業家向けに設計された高性能なオープンソース AI ビデオ＆画像生成プラットフォームです。洗練された Monorepo（単体リポジトリ多アプリケーション）アーキテクチャに基づき設計されており、Nuxt 3 による高パフォーマンスな SSR ユーザーポータル、多言語対応の Nuxt 3 管理画面、および Celery 非同期タスクキューを備えた Python FastAPI バックエンドを統合しています。

商用 AI 画像/ビデオ生成プラットフォームの新規立ち上げや、カスタム AI ワークフローの構築など、VidGen はクレジット決済・定期購入・コミュニティ共有・SEO 最適化・コンテンツモデレーションなど、商用サービスに必要な機能をすべて標準提供します。

---

## ✨ 主な機能

### 🎨 マルチモデル AI 生成エンジン
- **テキストからの画像生成 (Text2Img)**：FLUX.1、SDXL、Midjourney などの最新モデルを使用した超高解像度画像の生成。
- **画像からの画像生成 (Img2Img)**：元画像とプロンプト、類似度制御による画像再描画・スタイル変換。
- **テキストからの動画生成 (Text2Video)**：HunyuanVideo、Luma、Pika、Runway などの動的な動画生成。
- **画像からの動画生成 (Img2Video)**：静止画を一発で高フレームレートの動的な動画に変換（動きの大きさ微調整対応）。

### 🤖 マルチベンダーワークフロー＆非同期タスク
- **マルチベンダー API 適合**: SiliconFlow、Replicate、Google Gemini API、カスタム Provider 拡張メカニズムを内蔵。
- **ノード型ワークフローエンジン**: 複雑なマルチステップ AI ワークフローの視覚的構築と実行 (`backend/app/services/workflow_executor.py`)。
- **Celery 非同期タスクキュー**: 時間のかかる動画/大画像生成タスクを完全非同期化し、API スレッドのブロックを防止。
- **WebSocket リアルタイム状態通知**: Redis Pub/Sub と WebSocket 技術により、作品生成の進捗をリアルタイム配信。

### 💰 収益化・クレジット決済システム
- **グローバル決済統合**: **PayPal** および **Stripe** 決済ゲートウェイを標準統合。グローバル定期購入やクレジットパック購入に対応。
- **従量制クレジット消費**: モデルやパラメータ設定ごとに動的にクレジット消費量を設定可能。
- **割引・キャンペーンエンジン**: キャンペーンバナー、チャージ割引クーポン、プロモーションパッケージ設定をサポート。
- **毎日チェックイン報酬**: 連続チェックインによる階梯ボーナスと倍率加算システム。

### 🌐 プロンプトコミュニティ＆ソーシャル機能
- **探索ギャラリー**: コミュニティの優秀な作品、公開プロンプト、使用モデル、生成パラメータをウォーターフォール表示。
- **クリエイターマイページ**: カスタムハンドル名 (`@username`)、プロフィール、アイコン、個人作品集の展示。
- **ソーシャルインタラクション**: いいね、お気に入り、作品コメント、クリエイターフォロー機能。
- **SEO 深度最適化**: 動的 Meta タグ、自動 Sitemap 生成、特集ページ (`/topic/...`)、カテゴリページ (`/category/...`)、エフェクトページ (`/effects/...`)。

### 🔧 高機能な管理画面 (Admin Panel)
- **多言語 (i18n) サポート**: 英語、中国語、日本語、韓国語、スペイン語、ポルトガル語の 6 言語切替に対応。
- **バーチャルアカウント自動生成器**: `faker` ライブラリと Cloudflare R2 アイコン取得により、リアリティのあるバーチャルユーザーを大量一括生成。
- **コンテンツセーフティ・モデレーション**: NSFW 画像の自動判定、不適切なキーワードフィルター、ユーザー通報処理、一括凍結。
- **モデル＆価格管理**: AI モデルの稼働状態、基礎クレジット数、オプション加算、ワークフローテンプレートをノーコードでビジュアル設定。
- **運営ツール**: トップバナー・バナーカルーセル管理、ブログ記事エディタ、全般システム設定。

---

## 🛠️ 技術スタック一覧

| アーキテクチャ階層 | 技術選型 |
| :--- | :--- |
| **フロントエンド Web** | **Nuxt 3** (Vue 3, SSR/ISR), **Pinia**, **Tailwind CSS**, **Lucide Icons**, Axios, Socket.io |
| **管理画面 Admin** | **Nuxt 3** (Vue 3), **Tailwind CSS**, **Vue i18n** (6 言語対応), Axios |
| **バックエンド API** | **FastAPI** (Python 3.10+), **SQLAlchemy** (Async ORM), **Pydantic v2**, JWT |
| **タスクキュー＆監視** | **Celery**, **Flower** (キュー監視), **Redis** (Broker & キャッシュ) |
| **データベース** | **PostgreSQL** 14+ , **Alembic** マイグレーション管理 |
| **ストレージ＆ CDN** | **Cloudflare R2** / AWS S3 / Aliyun OSS (S3 互換オブジェクトストレージ) |
| **AI プロバイダー** | SiliconFlow, Replicate, Google Gemini, カスタム Adapter |
| **決済ゲートウェイ** | PayPal SDK, Stripe API |
| **コンテナオーケストレーション** | **Docker**, **Docker Compose** (一括全スタックコンテナ構築) |
| **運用・デプロイ** | 統一 **systemd** サービスマネージャー (`systemd/`), Nginx リバースプロキシ |

---

## 📁 ディレクトリ構造

```
vidgen/
├── web/                     # 🌐 フロントエンド Web アプリ (Nuxt 3, ポート 3000)
│   ├── pages/               # ページルーティング (探索、生成、マイページ、チャージ等)
│   ├── components/          # 再利用可能な Vue コンポーネント
│   ├── composables/         # カスタム Composable フック
│   ├── stores/              # Pinia 状態管理
│   └── nuxt.config.ts       # Nuxt 3 設定ファイル
│
├── admin/                   # 🔧 管理画面アプリ (Nuxt 3, ポート 3001)
│   ├── pages/               # 管理画面ルーティング (ユーザー管理、作品管理、審査、モデル等)
│   ├── composables/         # API & i18n フック (useAdminI18n.ts)
│   ├── locales/             # 6 言語対応辞書ファイル (en.ts, zh.ts, ja.ts, ko.ts 等)
│   └── nuxt.config.ts
│
├── backend/                 # 🐍 バックエンド API & 非同期エンジン (FastAPI, ポート 8000)
│   ├── app/
│   │   ├── main.py          # FastAPI エントリポイント＆ルーター登録
│   │   ├── celery_app.py    # Celery タスクキュー設定
│   │   ├── routes/          # API ルーティング (auth, works, generation, admin*.py)
│   │   ├── models/          # SQLAlchemy データベースモデル
│   │   ├── services/        # ストレージ、メール、Gemini、審査、決済等のコアサービス
│   │   ├── tasks/           # Celery 非同期タスク
│   │   └── utils/           # i18n、ログ、認証、Slug 生成等ツール
│   ├── migrations/          # Alembic DB マイグレーション脚本
│   ├── scripts/             # システム初期化＆メンテナンス CLI ツール
│   └── requirements.txt     # Python 依存関係リスト
│
├── systemd/                 # ⚙️ 統一サービス管理＆デプロイ脚本
│   ├── deploy.sh            # 開発自動デプロイ脚本
│   ├── manage-services.sh   # 対話型 systemd サービスマネージャー
│   └── *.service            # systemd サービス設定ファイル
│
└── docs/                    # 📚 技術開発・デプロイドキュメント
    ├── AA_PANEL_DEPLOYMENT_GUIDE.md
    ├── SYSTEMD_UNIFIED_GUIDE.md
    └── ...
```

---

## ⚡ クイックスタート指南

### 🐳 方法一：Docker Compose 起動（推奨）

単一のコマンドで全 VidGen サービス（Web、Admin、FastAPI Backend、Celery Worker、PostgreSQL、Redis）を一括構築・起動します：

```bash
# リポジトリのクローン
git clone https://github.com/ucmao/vidgen.git
cd vidgen

# 全 6 サービスコンテナを一括起動
docker compose up -d
```

- 🌐 **Web ポータル**: `http://localhost:3000`
- 🔧 **管理画面 Admin**: `http://localhost:3001` (初期管理者: `admin` / パスワード: `admin123`)
- 🐍 **API ドキュメント (Swagger UI)**: `http://localhost:8000/docs`

> 💡 **自動シードデータ（Seed Data）**：コンテナ起動時、`scripts/seed_all.py` が自動実行され、1 分以内に DB マイグレーション、管理者作成、AI モデル導入、チャージパッケージおよび SEO 設定が全自動初期化されます。

---

### 🛠️ 方法二：ローカル手動ビルド起動

#### 前提環境
- **Python**: 3.10 以上
- **Node.js**: 18.x 以上
- **PostgreSQL**: 14.x 以上
- **Redis**: 6.x 以上

---

### 1. バックエンドのセットアップ

```bash
# backend ディレクトリへ移動
cd backend

# Python 仮想環境の作成と有効化
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 依存パッケージのインストール
pip install -r requirements.txt

# 環境設定ファイルの作成
cp .env.example .env
# backend/.env を編集し、DATABASE_URL, REDIS_URL, R2 情報等を設定
```

#### データベース初期化＆シードデータ注入

```bash
# Alembic マイグレーション実行
alembic upgrade head

# CLI 初期化脚本の一括実行
python scripts/seed_all.py
```

#### FastAPI 開発サーバー起動

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
- **API ドキュメント**: `http://localhost:8000/docs`

---

### 2. Celery Worker の起動（非同期タスク処理）

```bash
cd backend
source venv/bin/activate

# 動画・画像生成タスク用 Celery ワーカーの起動
celery -A app.celery_app worker --loglevel=info -c 4
```

---

### 3. フロントエンド Web アプリの起動 (ポート 3000)

```bash
cd web

# 依存パッケージのインストール
npm install

# 環境設定ファイルの作成
cp .env.example .env

# Nuxt 3 開発サーバーの起動
npm run dev
```
- **Web ポータル**: `http://localhost:3000`

---

### 4. 管理画面 Admin の起動 (ポート 3001)

```bash
cd admin

# 依存パッケージのインストール
npm install

# 管理画面開発サーバーの起動
npm run dev
```
- **管理画面 Admin**: `http://localhost:3001`
- **初期ログインアカウント**: `python scripts/create_first_admin.py` により作成されたアカウント（デフォルト `admin` / `admin123`）

---

## 🚢 サービス管理＆本番デプロイ

VidGen には本番環境に対応した **systemd 統一サービスマネージャー** が内蔵されています（`systemd/`）：

```bash
# 対話型サービスマネージャーの実行
chmod +x systemd/manage-services.sh
./systemd/manage-services.sh
```

利用可能なコマンド：
- **`manage-services.sh status`**: Web, Admin, Backend API, Celery のリアルタイム状態確認。
- **`manage-services.sh start`**: 全サービスの一括起動。
- **`manage-services.sh restart`**: 全サービスの安全な再起動。
- **`deploy.sh`**: ワンクリック全自動本番デプロイ脚本。

詳細な Nginx や aaPanel へのデプロイ手順は [docs/05-deployment/production-deployment.md](docs/05-deployment/production-deployment.md) を参照してください。

---

## 🛠️ CLI メンテナンスツール

`backend/scripts/` フォルダには運用管理用の便利なツールが用意されています：

```bash
# ユーザーアカウントにクレジットを手動付与
python scripts/add_credits.py --email user@example.com --amount 1000

# システムに新しい AI モデルを一括インポート
python scripts/import_models.py

# 作品の URL Slug とタグの一括更新
python scripts/update_url_slugs_from_titles.py
```

---

## 📄 ライセンス

本プロジェクトは **MIT ライセンス** のもとでオープンソースとして公開されています。詳細は [LICENSE](LICENSE) ファイルを参照してください。

---

## 🤝 コントリビューション＆コミュニティ

Issue の報告、新機能提案、Pull Request を大歓迎します！  
気軽に Issue を立てたり PR を送信してください。

*VidGen がお役に立ちましたら、ぜひ GitHub で ⭐️ Star をお願いいたします！*

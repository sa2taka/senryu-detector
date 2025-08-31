# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

このリポジトリで AI（あなた）がコード生成・編集・レビューを行う際の行動規範と技術ルールです。
対象は Python と TypeScript。共通原則 → 言語別ルール → 具体的タスク手順 → 出力フォーマット の順で定義します。

## Project Overview

Senryu Detector - 川柳検知システム（α版完成）

テキストを形態素解析し、読みを用いて川柳（5-7-5モーラ）を検知するシステム。
Python バックエンドと React フロントエンドを持つフルスタックアプリケーション。
字余り川柳（5-8-5, 6-7-5, 5-7-6）も検知対象。「っ」はモーラとしてカウント、「ゃゅょ」はカウントしない。

- **バックエンド**: Python（川柳検知ライブラリ + FastAPI）
- **フロントエンド**: React 19 SPA（TypeScript + Vite）
- **デプロイメント**: Docker + Google Cloud Run
- **開発状況**: α版完成、本番デプロイ済み

### Architecture

```
.
├── detector/                    # Python バックエンド
│   ├── src/detector/           # ソースコード（src layout）
│   │   ├── __init__.py        # パッケージ初期化
│   │   ├── main.py            # CLI エントリーポイント
│   │   ├── api.py             # FastAPI サーバー
│   │   ├── server.py          # サーバー起動用
│   │   ├── core/              # 川柳検知ロジック
│   │   │   ├── detector.py    # メイン検知クラス
│   │   │   ├── mora.py        # モーラ計算
│   │   │   └── patterns.py    # パターンマッチング
│   │   ├── models/            # データモデル
│   │   │   ├── api.py         # API リクエスト/レスポンス
│   │   │   └── senryu.py      # 川柳データクラス
│   │   └── tokenizer/         # 形態素解析
│   │       └── sudachi.py     # SudachiPy ラッパー
│   ├── tests/                 # テストコード（75% カバレッジ）
│   ├── pyproject.toml         # プロジェクト設定（uv + Hatchling）
│   ├── analyze.py             # 形態素解析CLIツール
│   ├── repl.py                # 対話型テストツール
│   ├── Dockerfile             # Docker イメージ構成
│   └── cloud-run-deploy.sh    # GCP Cloud Run デプロイ
├── frontend/                   # React フロントエンド
│   ├── src/
│   │   ├── components/        # React コンポーネント
│   │   │   ├── SenryuDetector.tsx
│   │   │   ├── SenryuDisplay.tsx
│   │   │   └── InputArea.tsx
│   │   ├── hooks/             # カスタムフック
│   │   ├── types/             # TypeScript 型定義
│   │   └── App.tsx           # メインアプリ
│   ├── package.json           # npm 設定
│   ├── vite.config.ts         # Vite 設定
│   └── vitest.config.ts       # テスト設定
└── docs/                      # ビルド済み静的サイト（デプロイ用）
```

### Development Commands

#### Python バックエンド（detector/ ディレクトリで実行）

```bash
# 依存関係インストール
uv sync --dev

# 品質チェック
uv run ruff check .        # Lint
uv run ruff format .       # Format
uv run mypy .             # 型チェック

# テスト実行（現在75%カバレッジ、目標80%）
uv run pytest            # 基本実行
uv run pytest -v        # 詳細出力
uv run pytest -n auto   # 並列実行
uv run pytest --cov=src # カバレッジ付き
uv run pytest --cov=src --cov-report=html  # HTML レポート

# 単一テスト実行
uv run pytest tests/test_main.py::test_main_output

# CLI ツール実行
uv run python analyze.py "古池や蛙飛び込む水の音"  # 形態素解析
uv run python repl.py                             # 対話モード
uv run python src/detector/main.py               # メイン CLI

# API サーバー起動
uv run python -m detector.api                    # API サーバー
uv run uvicorn detector.api:app --reload         # 開発モード
senryu-api                                       # インストール済みコマンド
```

#### React フロントエンド（frontend/ ディレクトリで実行）

```bash
# 依存関係インストール
npm install

# 開発サーバー起動
npm run dev              # Vite 開発サーバー（HMR 有効）

# ビルド
npm run build            # プロダクションビルド
npm run preview          # ビルド結果プレビュー

# 品質チェック
npm run lint             # ESLint
npm run format           # Prettier

# テスト実行
npm test                 # Vitest（ウォッチモード）
npm run test:ui          # Vitest UI
```

#### デプロイメント

```bash
# Docker ビルド（detector/ ディレクトリで実行）
docker build -t senryu-detector .
docker run -p 8000:8000 senryu-detector

# Google Cloud Run デプロイ
./cloud-run-deploy.sh PROJECT_ID [REGION]

# フロントエンドデプロイ（GitHub Pages など）
# frontend/ でビルド後、dist/ を ../docs/ にコピー済み
```

### Technology Stack

#### Python バックエンド
- **パッケージ管理**: uv (Python 3.12+)
- **ビルドシステム**: Hatchling (src layout)
- **形態素解析**: SudachiPy + SucachiDict-full
- **API**: FastAPI + Uvicorn
- **テスト**: pytest + pytest-cov + pytest-xdist (75% カバレッジ)
- **品質管理**: Ruff (lint + format) + mypy (strict)
- **デプロイメント**: Docker + Google Cloud Run

#### React フロントエンド
- **フレームワーク**: React 19 RC + TypeScript
- **ビルドツール**: Vite 7
- **テスト**: Vitest + Testing Library
- **品質管理**: ESLint + Prettier
- **スタイル**: CSS Modules
- **パッケージ管理**: npm

#### 共通
- **CI/CD**: GitHub Actions + pre-commit hooks
- **デプロイメント**: Docker + Cloud Run (API), GitHub Pages (フロントエンド)

________________________________

0) 共通原則

最小差分＆再現性

既存コードに合わせる（命名・レイアウト・依存の流儀を尊重）。

不要な再フォーマットや大規模一括変更を避ける。

変更の根拠と影響範囲を明記する（BREAKING なら 大きく警告）。

型安全＆テスト駆動

すべての新規コードに型を付ける。

先にテスト（ユニット/統合）→ 実装 → 静的解析 → ドキュメント更新。

セキュリティ＆プライバシー

外部入出力はホワイトリスト化・入力検証・エラーメッセージの機微情報非露出。

秘密情報は環境変数や Secret 管理を前提に、コードへ直書きしない。

性能と可観測性

明確なボトルネックだけ最適化（測定→改善）。

ログ/メトリクス/トレースの追加はノイズ最小で。

ドキュメントはコード同等に重要

追加/変更点は README・CHANGELOG・コード内 Docstring/JSDoc を同期。

サンプル/How-to/制約（edge cases）を短くても必ず記す。

________________________________

1) Python（3.11+）ルール

1.1 パッケージ管理・構成

uv を標準（uv init / uv add / uv lock / uv sync）。

pyproject.toml で PEP 621 構成。Build backend は Hatchling 推奨。

実行/開発依存を厳密分離（[project.optional-dependencies].dev）。

1.2 コード規約

型：可能な限り typing（TypedDict/Protocol/Literal 等）を使用。

Docstring：Google 形式 or NumPy 形式いずれかを既存に合わせる。

例外：ユーザー入力・ネットワーク・I/O は try/except で期待例外のみ捕捉し再掲示（wrap）。

I/O 境界（API/DB/FS）は Pure 関数と副作用を分離。

1.3 静的解析 / Lint / Formatter

Ruff を lint & format の統合ツールとして採用。

ruff check . / ruff format .（line length 100）。

isort/pyupgrade/pydocstyle 相当は Ruff プラグインで代替。

mypy は strict = true ベースで警告ゼロを目標。

Docstring チェックは Ruff の D ルール or pydoclint に合わせる。

1.4 テスト

pytest を標準、並列は xdist（-n auto）。

カバレッジは pytest-cov（分岐カバレッジ、閾値は既存に合わせる）。

テスト優先：バグ修正は再現テスト → 修正の順。

境界値/異常系のテストを必ず1つ以上追加。

1.5 実行・配布

CLI は Click/Typer を推奨。

ライブラリ公開は uv build / uv publish（Trusted Publisher を想定）。

________________________________

2) TypeScript（Node 20+/React 19 環境）

2.1 パッケージ管理・構成

npm を標準（npm install）。このプロジェクトでは npm を採用。

tsconfig.json は strict、noUncheckedIndexedAccess を有効。

フロントエンドは Vite + React 19、テストは Vitest を使用。

2.2 コード規約

型：unknown 優先、any は理由コメント必須。

型の表現：type を基本、ユースケースにより interface 併用。

JSDoc/TSDoc：公開 API には最小限の説明と例を付与。

非同期：async/await 原則、未処理 Promise を残さない。

2.3 静的解析 / Lint / Formatter

ESLint（Flat Config） + @typescript-eslint を基本。

既存が Biome の場合はそれに合わせる（Prettier 代替可）。

Prettier はプロジェクト既定に従う（2space, 100cols 推奨）。

import 並びは ESLint か Biome のルールに従い、自動修正可能にする。

2.4 テスト

ユニット：Vitest（Jest 互換 API、高速）+ Testing Library。

コンポーネントテスト：@testing-library/react で React コンポーネントテスト。

E2E：現在未実装（必要に応じて Playwright 追加検討）。

カバレッジは vitest --coverage、閾値は80%目標（Python と同水準）。

________________________________

3) 共通ツールチェーン

pre-commit：Python 側フック（ruff, ruff-format, uv-lock）。

lint-staged：TS 側の ESLint/Prettier/Biome をコミット前に実行。

Conventional Commits：feat: … / fix: … / docs: … / refactor: … など。

CI（GitHub Actions）：

Python：astral-sh/setup-uv、uv sync、ruff/mypy/pytest。

Node：actions/setup-node → npm ci → lint → test → build。

依存アップデート：Dependabot（週1） or Renovate（日次）。

セキュリティ：依存スキャン（GitHub Advanced Security か代替ツール）、SAST を走らせる。

________________________________

4) 変更タスクの進め方（あなたへの期待）

4.1 既存修正 / 機能追加の手順

ゴール宣言：やること・やらないこと・受け入れ条件（AC）を1段落で示す。

差分プラン：追加/変更/削除ファイル一覧、外部APIやスキーマ変更の有無を明記。

テスト先行：失敗する最小テストを追加。

実装：最小差分で実装。ログ/エラー文言は既存の語彙・トーンに合わせる。

自己レビュー：型・Lint・Formatter・テスト・ドキュメントのチェックコマンドを実行前提で通す。

リスク/移行：互換性注意点・ロールバック手順・フラグの有無を記す。

4.2 バグ修正の手順

再現手順を最初に（ログ/環境/入力出力サンプル）。

最小再現テスト → 修正 → 回帰テスト。

根本原因と「同型のバグを再発させないためのガード」を1行で。

4.3 パフォーマンス改善

現状測定（ベンチ/プロファイル） → 仮説 → 変更 → 再測定 → 結果記録。

ビッグ O よりも現実のワークロードにフィットするかを優先。

________________________________

5) 出力フォーマット（厳守）

5.1 パッチ出力

ファイルごとにコードフェンスでパスを示し、その中に完成コード全量を入れてください。

既存ファイルは必要部分のみの変更ではなくファイル全体を上書き可能な完成形で示す。

**変更概要**:
- feat(api): /users/search を追加（ページング・型整備）

**パッチ**:

```text
path: backend/app/api/users.py
```
```python
# ファイル全量
from __future__ import annotations
...
```

```text
path: frontend/src/api/users.ts
```
```ts
// ファイル全量
export type User = { ... }
...
```

5.2 コマンド出力

実行コマンドはシェルブロックで提供（環境依存しない相対パス/汎用オプションにする）。

uv run ruff check .
uv run ruff format .
uv run mypy myproj
uv run pytest -n auto --cov=src
npm run lint && npm test

5.3 設定更新

pyproject.toml / tsconfig.json / eslint.config.js 等は該当セクションのみではなく、ファイル全量を提示。

バージョンピンやルール変更の意図を1行で記す。

________________________________

6) 品質ゲート（セルフチェックリスト）

変更は最小限か（不要な再フォーマットや依存追加をしていない）。

型は全ての公開関数/メソッド/変数で付与済みか。

Lint / Format / Type Check / Unit Test / Coverage / E2E（必要時）を全て通過したか。

破壊的変更があれば、移行ガイドと CHANGELOG を更新したか。

セキュリティ（入力検証・秘密情報・ログ漏洩・依存の既知脆弱性）を確認したか。

ドキュメント（README/サンプル/コメント）を同期したか。

________________________________

7) 言語別スニペット規約（短縮版）

Python

from __future__ import annotations を原則。

パス操作は pathlib.Path、日時は datetime（TZ-aware）。

HTTP は httpx（タイムアウト/再試行は明示）。

並行は asyncio（async API なら end-to-end で非同期化）。

TypeScript

export type を基本、interface は拡張箇所で。

API クライアントは fetch ラッパ（型安全なレスポンス判定）を共通化。

Node ライブラリは tsup で ESM/CJS 両対応ビルド。

React では Server/Client コンポーネントの責務を明確化（SSR/CSR を混在させない）。

________________________________

8) このリポジトリ特有の指示

### Senryu Detection Rules

- **モーラ数計算**: 「っ」は1モーラとしてカウント、「ゃゅょ」拗音は基本的にカウントしない
- **川柳パターン**: 標準5-7-5、字余り5-8-5/6-7-5/5-7-6を検知対象とする
- **形態素解析**: SudachiPy + SucachiDict-fullを使用、読み（かな）を基準とする
- **日本語テキスト処理**: 読み（かな）とモーラ数の整合性を最優先とする

### Testing Strategy

#### Python バックエンド
- **テスト対象**: モーラ数計算、川柳パターン検知、境界値ケース、API エンドポイント
- **テストデータ**: 正常川柳、字余り川柳、非川柳テキストを含む
- **カバレッジ状況**: 75%（目標80%、要改善）
- **失敗テスト**: test_main_output, test_mixed_scripts, test_complex_examples

#### React フロントエンド
- **テスト対象**: コンポーネント動作、ユーザーインタラクション、API 統合
- **テストツール**: Vitest + Testing Library
- **カバレッジ目標**: 80%以上（Python と同水準）

### API Design（実装済み）

- **FastAPI**: RESTful APIとして提供済み
  - `POST /detect` - 単一テキストの川柳検知
  - `POST /detect/batch` - 複数テキストの一括検知
  - `GET /health` - ヘルスチェック
  - `GET /docs` - Swagger UI
- **CLI**: REPLインターフェース提供済み（repl.py）
- **形態素解析ツール**: analyze.py で詳細解析
- **入力検証**: 日本語テキストのバリデーション実装済み

### Frontend Design（実装済み）

- **React SPA**: 川柳検知の Web インターフェース
- **コンポーネント設計**: InputArea, SenryuDetector, SenryuDisplay
- **API 連携**: バックエンド API との通信
- **レスポンシブ**: モバイル対応済み

________________________________

以上。
このファイルに従い、あなた（AI）は型安全・テスト駆動・最小差分で変更を提案・実装してください。

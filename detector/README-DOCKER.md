# Senryu Detector - Docker & Cloud Run Deployment Guide

## Docker化の構成

### アーキテクチャ
- **Multi-stage build**: ビルドステージと実行ステージを分離
- **Base Image**:
  - Build: `python:3.12-slim` (uv高速インストール用)
  - Runtime: `gcr.io/distroless/python3-debian12:nonroot` (最小セキュア実行環境)
- **Package Manager**: uv (高速依存関係管理)
- **Security**: non-rootユーザー実行、攻撃面最小化

### 作成されたファイル

```
detector/
├── Dockerfile              # Multi-stage Docker定義
├── .dockerignore           # 不要ファイル除外設定
├── cloudbuild.yaml         # Cloud Build CI/CD設定
├── cloud-run-deploy.sh     # 手動デプロイスクリプト
└── README-DOCKER.md        # このファイル
```

## ローカル Docker 実行

### 1. イメージビルド
```bash
cd detector/
docker build -t senryu-detector .
```

### 2. コンテナ起動
```bash
# デフォルトポート8080
docker run -p 8080:8080 senryu-detector

# カスタムポート指定
docker run -p 3000:3000 -e PORT=3000 senryu-detector
```

### 3. API テスト
```bash
# Health check
curl http://localhost:8080/health

# 川柳検知テスト
curl -X POST http://localhost:8080/detect \
  -H "Content-Type: application/json" \
  -d '{"text": "古池や蛙飛び込む水の音", "only_valid": true}'
```

## Cloud Run デプロイ

### 準備
1. Google Cloud Project作成・選択
2. 必要なAPIを有効化（自動実行されます）
   - Cloud Build API
   - Cloud Run API
   - Artifact Registry API

### 方法1: 手動デプロイスクリプト使用（推奨）

```bash
# PROJECT_IDを指定して実行
./cloud-run-deploy.sh YOUR_PROJECT_ID

# リージョン指定（デフォルト: asia-northeast1）
./cloud-run-deploy.sh YOUR_PROJECT_ID us-central1
```

### 方法2: Cloud Build使用（CI/CD）

```bash
# GitHub連携またはソースコード連携設定後
gcloud builds submit --config=cloudbuild.yaml
```

### Cloud Run設定詳細

| 項目 | 設定値 | 理由 |
|------|--------|------|
| Memory | 2Gi | SudachiDict読み込み用 |
| CPU | 2 | 形態素解析処理用 |
| Min instances | 0 | コールドスタート許容・コスト最適化 |
| Max instances | 100 | 大量リクエスト対応 |
| Concurrency | 80 | メモリ効率考慮 |
| Timeout | 300s | 大きなテキスト処理対応 |

## 本番環境考慮事項

### セキュリティ
- ✅ Distrolessイメージ使用（脆弱性最小化）
- ✅ Non-rootユーザー実行
- ✅ 必要最小限のファイルのみ含める
- ⚠️ CORS設定を本番環境用に制限推奨

### パフォーマンス
- ✅ uv使用による高速ビルド
- ✅ Multi-stage buildによるイメージサイズ最適化
- ✅ Docker layer caching活用
- ✅ SudachiDict事前ダウンロード

### 監視・ログ
- ✅ Cloud Logging統合
- ✅ ヘルスチェックエンドポイント提供
- ✅ 構造化ログ出力

### コスト最適化
- ✅ Min instances 0（使用時のみ課金）
- ✅ 適切なリソース設定
- ✅ 効率的な同期処理

## トラブルシューティング

### よくある問題

**1. ビルド時間が長い**
```bash
# Docker BuildKit有効化
export DOCKER_BUILDKIT=1
docker build -t senryu-detector .
```

**2. メモリ不足エラー**
```bash
# Cloud Runメモリ増加
gcloud run services update senryu-detector \
  --memory=4Gi --region=asia-northeast1
```

**3. コールドスタート時間短縮**
```bash
# Min instancesを1以上に設定
gcloud run services update senryu-detector \
  --min-instances=1 --region=asia-northeast1
```

### ログ確認
```bash
# Cloud Runログ表示
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=senryu-detector" \
  --limit=50 --format="table(timestamp,textPayload)"
```

### デバッグモード
```bash
# ローカルでコンテナ内シェルアクセス
docker run -it --entrypoint=/bin/sh senryu-detector

# Cloud Run環境変数追加
gcloud run services update senryu-detector \
  --set-env-vars="LOG_LEVEL=DEBUG" --region=asia-northeast1
```

## 追加リソース

- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Cloud Build Documentation](https://cloud.google.com/build/docs)
- [Artifact Registry Documentation](https://cloud.google.com/artifact-registry/docs)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)

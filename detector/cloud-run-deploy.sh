#!/bin/bash

# Senryu Detector Cloud Run デプロイスクリプト
# Usage: ./cloud-run-deploy.sh [PROJECT_ID] [REGION]

set -euo pipefail

# デフォルト値
DEFAULT_PROJECT_ID="${GOOGLE_CLOUD_PROJECT:-}"
DEFAULT_REGION="asia-northeast1"
SERVICE_NAME="senryu-detector"
REPOSITORY_NAME="senryu-detector"

# 引数パース
PROJECT_ID="${1:-$DEFAULT_PROJECT_ID}"
REGION="${2:-$DEFAULT_REGION}"

if [[ -z "$PROJECT_ID" ]]; then
  echo "Error: PROJECT_ID が設定されていません"
  echo "Usage: $0 <PROJECT_ID> [REGION]"
  echo "または GOOGLE_CLOUD_PROJECT 環境変数を設定してください"
  exit 1
fi

echo "🚀 Senryu Detector をCloud Runにデプロイします"
echo "   Project ID: $PROJECT_ID"
echo "   Region: $REGION"
echo "   Service: $SERVICE_NAME"
echo ""

# 必要なAPIの有効化確認
echo "📋 必要なAPIが有効化されているか確認中..."
gcloud services enable \
  cloudbuild.googleapis.com \
  run.googleapis.com \
  artifactregistry.googleapis.com \
  --project="$PROJECT_ID"

# Artifact Registryリポジトリの作成（存在しない場合のみ）
echo "📦 Artifact Registryリポジトリを確認/作成中..."
if ! gcloud artifacts repositories describe "$REPOSITORY_NAME" \
  --location="$REGION" \
  --project="$PROJECT_ID" \
  --quiet > /dev/null 2>&1; then

  echo "   リポジトリを作成中: $REPOSITORY_NAME"
  gcloud artifacts repositories create "$REPOSITORY_NAME" \
    --repository-format=docker \
    --location="$REGION" \
    --description="Senryu Detector Docker images" \
    --project="$PROJECT_ID"
else
  echo "   リポジトリは既に存在します: $REPOSITORY_NAME"
fi

# Dockerイメージのビルドとプッシュ
IMAGE_URI="$REGION-docker.pkg.dev/$PROJECT_ID/$REPOSITORY_NAME/$SERVICE_NAME"
BUILD_TAG=$(date +%Y%m%d-%H%M%S)
TAGGED_IMAGE="$IMAGE_URI:$BUILD_TAG"
LATEST_IMAGE="$IMAGE_URI:latest"

echo "🔨 Dockerイメージをビルド中..."
docker build -t "$TAGGED_IMAGE" -t "$LATEST_IMAGE" .

echo "📤 Artifact Registryにプッシュ中..."
docker push "$TAGGED_IMAGE"
docker push "$LATEST_IMAGE"

# Cloud Runサービスのデプロイ
echo "☁️ Cloud Runサービスをデプロイ中..."
gcloud run deploy "$SERVICE_NAME" \
  --image="$TAGGED_IMAGE" \
  --region="$REGION" \
  --platform=managed \
  --allow-unauthenticated \
  --memory=2Gi \
  --cpu=2 \
  --min-instances=0 \
  --max-instances=100 \
  --concurrency=80 \
  --timeout=300 \
  --port=8080 \
  --set-env-vars="PYTHONUNBUFFERED=1,PYTHONDONTWRITEBYTECODE=1" \
  --project="$PROJECT_ID" \
  --quiet

# デプロイ結果の取得
SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" \
  --region="$REGION" \
  --project="$PROJECT_ID" \
  --format="value(status.url)")

echo ""
echo "✅ デプロイ完了！"
echo "   Service URL: $SERVICE_URL"
echo "   Health Check: $SERVICE_URL/health"
echo "   API Docs: $SERVICE_URL/docs"
echo "   ReDoc: $SERVICE_URL/redoc"
echo ""
echo "🧪 テスト用サンプルリクエスト:"
echo "curl -X POST '$SERVICE_URL/detect' \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{\"text\": \"古池や蛙飛び込む水の音\", \"only_valid\": true}'"
echo ""
echo "📊 Cloud Runコンソール:"
echo "https://console.cloud.google.com/run/detail/$REGION/$SERVICE_NAME/metrics?project=$PROJECT_ID"

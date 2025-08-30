# Cloud Run デプロイ修正ドキュメント

## 発生したエラーと解決方法

### 1. プロジェクトIDエラー
**エラー内容:**
```
ERROR: (gcloud.services.enable) [sa2taka@gmail.com] does not have permission to access projects instance [myfirestoretest-408205]
```

**原因:** 間違ったプロジェクトIDを指定していた

**解決方法:** 正しいプロジェクトID `haiku-detector-470614` を使用

### 2. Dockerfile - README.md not found エラー
**エラー内容:**
```
ERROR: failed to compute cache key: failed to calculate checksum of ref: "/README.md": not found
```

**原因:** `.dockerignore` ファイルで `*.md` を除外していたため、README.mdがDockerビルドコンテキストに含まれていなかった

**解決方法:**
1. `.dockerignore` ファイルから `*.md` の除外を削除
2. DockerfileでREADME.mdをコピーするステップを維持

**修正前の .dockerignore:**
```
# Project specific
tests/
*.md  # これが問題の原因
cloudbuild.yaml
```

**修正後の .dockerignore:**
```
# Project specific
tests/
cloudbuild.yaml
```

### 3. Docker認証エラー
**エラー内容:**
```
denied: Unauthenticated request. Unauthenticated requests do not have permission "artifactregistry.repositories.uploadArtifacts"
```

**原因:** DockerがArtifact Registryへの認証設定がされていない

**解決方法:**
gcloud認証ヘルパーを設定する必要がある

```bash
# Artifact Registry用のDocker認証を設定
gcloud auth configure-docker asia-northeast1-docker.pkg.dev
```

## デプロイ手順の修正版

### 前提条件
1. Google Cloud SDKがインストールされていること
2. 適切なプロジェクトにアクセス権限があること
3. Docker認証が設定されていること

### 手順

1. **Docker認証の設定**
```bash
# gcloudでログイン
gcloud auth login

# プロジェクトを設定
gcloud config set project haiku-detector-470614

# Docker認証ヘルパーを設定
gcloud auth configure-docker asia-northeast1-docker.pkg.dev
```

2. **デプロイスクリプトの実行**
```bash
cd /home/sa2ta/Documents/projects/senryu-detector/detector
./cloud-run-deploy.sh haiku-detector-470614 asia-northeast1
```

## 修正したファイル一覧

1. **detector/.dockerignore**
   - `*.md` の除外を削除

2. **detector/Dockerfile**
   - README.mdのコピーを適切な位置に配置
   - pyproject.tomlがREADME.mdを参照しているため、ビルド時に必要

### 4. コンテナ起動エラー - PORT環境変数
**エラー内容:**
```
ERROR: (gcloud.run.deploy) Revision 'senryu-detector-00001-lx6' is not ready and cannot serve traffic.
The user-provided container failed to start and listen on the port defined provided by the PORT=8080 environment variable
```

**原因:** DockerfileのCMDで固定ポート8080を指定していたが、Cloud RunはPORT環境変数を使って動的にポートを設定する必要がある

**解決方法:**
DockerfileのCMDを修正して、api.pyのmain()関数を実行するように変更。main()関数は既にPORT環境変数を読み取るよう実装されている。

**修正前のDockerfile CMD:**
```dockerfile
CMD ["python", "-m", "uvicorn", "detector.api:app", "--host", "0.0.0.0", "--port", "8080"]
```

**修正後のDockerfile CMD:**
```dockerfile
CMD ["python", "-m", "detector.api"]
```

api.pyのmain()関数は以下のようにPORT環境変数を適切に処理:
```python
def main() -> None:
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(
        "detector.api:app",
        host="0.0.0.0",
        port=port,
        ...
    )
```

## 今後の改善点

1. **デプロイスクリプトの改善**
   - Docker認証チェックを追加
   - エラーハンドリングの強化

2. **ドキュメント化**
   - デプロイ手順をREADMEに追記
   - 前提条件を明確化

3. **CI/CD**
   - GitHub Actionsなどでの自動デプロイ設定を検討

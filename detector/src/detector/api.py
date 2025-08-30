"""川柳検知システムのFastAPI API。."""

from __future__ import annotations

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .core.detector import SenryuDetector
from .models.api import (
    DetectRequest,
    DetectResponse,
    ErrorResponse,
    HealthResponse,
)

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# グローバル検知器インスタンス
detector: SenryuDetector | None = None


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """アプリケーションのライフサイクル管理。."""
    global detector
    logger.info("川柳検知システムを初期化中...")
    try:
        detector = SenryuDetector()
        logger.info("初期化完了")
    except Exception as e:
        logger.error(f"初期化エラー: {e}")
        raise

    yield

    logger.info("川柳検知システムを終了中...")


# FastAPIアプリケーション初期化
app = FastAPI(
    title="川柳検知API - Senryu Detector API",
    description="""
    日本語テキストから川柳（5-7-5音律）を検知するAPI。

    ## 機能
    - 標準的な5-7-5パターンの検知
    - 字余り川柳（5-8-5、6-7-5、5-7-6）の検知
    - SudachiPy形態素解析による高精度な音律解析
    - バッチ処理対応

    ## 使用方法
    1. `/detect` エンドポイントにテキストをPOST
    2. 検知結果を受け取る
    """,
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 本番環境では適切に制限すること
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def general_exception_handler(request: object, exc: Exception) -> JSONResponse:
    """一般的な例外ハンドラ。."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="内部サーバーエラー",
            detail=str(exc),
        ).model_dump(),
    )


@app.get("/", response_model=dict[str, str])
async def root() -> dict[str, str]:
    """APIルート - 基本情報を返す。."""
    return {
        "message": "川柳検知API - Senryu Detector API",
        "version": "0.1.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/health",
    }


@app.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """ヘルスチェックエンドポイント。."""
    global detector

    if detector is None:
        raise HTTPException(
            status_code=503,
            detail="検知器が初期化されていません",
        )

    return HealthResponse(
        status="healthy",
        message="川柳検知システムは正常に動作しています",
        version="0.1.0",
    )


@app.post("/detect", response_model=DetectResponse)
async def detect_senryu(request: DetectRequest) -> DetectResponse:
    """テキストから川柳を検知。."""
    global detector

    if detector is None:
        raise HTTPException(
            status_code=503,
            detail="検知器が初期化されていません",
        )

    if not request.text.strip():
        raise HTTPException(
            status_code=400,
            detail="テキストが空です",
        )

    try:
        # 川柳検知実行
        results = detector.detect(request.text)

        # only_validオプションが有効な場合、有効な結果のみフィルタ
        if request.only_valid:
            results = [result for result in results if result.is_valid]

        # detailsオプションが無効な場合、phraseフィールドを削除
        if not request.details:
            for result in results:
                result.upper_phrase = None
                result.middle_phrase = None
                result.lower_phrase = None

        return DetectResponse(
            success=True,
            results=results,
            count=len(results),
        )

    except Exception as e:
        logger.error(f"Detection error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"検知処理中にエラーが発生しました: {str(e)}",
        ) from e


def main() -> None:
    """API サーバーを起動。."""
    import os

    import uvicorn

    # Cloud Runのポート環境変数を優先、デフォルトは8080
    port = int(os.getenv("PORT", "8080"))

    uvicorn.run(
        "detector.api:app",
        host="0.0.0.0",
        port=port,
        reload=False,  # 本番環境ではreloadを無効化
        log_level="info",
    )


if __name__ == "__main__":
    main()

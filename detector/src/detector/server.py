"""FastAPIサーバーのエントリーポイント."""

from __future__ import annotations

import os
import sys

import uvicorn


def main() -> None:
    """FastAPIサーバーを起動."""
    # Cloud Runのポート環境変数を優先、デフォルトは8080
    port = int(os.getenv("PORT", "8080"))

    # ログ出力
    print(f"Starting server on port {port}...", file=sys.stderr)

    uvicorn.run(
        "detector.api:app",
        host="0.0.0.0",
        port=port,
        reload=False,
        log_level="info",
        access_log=True,
    )


if __name__ == "__main__":
    main()

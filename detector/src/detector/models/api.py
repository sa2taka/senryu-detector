"""FastAPI用のリクエスト・レスポンスモデル。."""

from __future__ import annotations

from pydantic import BaseModel, Field

from .senryu import DetectionResult


class DetectRequest(BaseModel):
    """川柳検知APIのリクエストモデル。."""

    text: str = Field(
        description="分析する日本語テキスト",
        examples=["古池や蛙飛び込む水の音", "春風にぽっぽーという汽笛が聞こえる"],
    )
    only_valid: bool = Field(
        default=False,
        description="Trueの場合、有効な川柳のみを返す",
    )


class DetectResponse(BaseModel):
    """川柳検知APIのレスポンスモデル。."""

    success: bool = Field(description="処理が成功したかどうか")
    text: str = Field(description="分析されたテキスト")
    results: list[DetectionResult] = Field(description="検知結果のリスト")
    count: int = Field(description="検知された川柳の数")


class HealthResponse(BaseModel):
    """ヘルスチェックAPIのレスポンスモデル。."""

    status: str = Field(description="システムステータス", examples=["healthy"])
    message: str = Field(description="ステータスメッセージ")
    version: str = Field(description="システムバージョン")


class ErrorResponse(BaseModel):
    """エラーレスポンスモデル。."""

    success: bool = Field(default=False, description="処理が失敗したことを示す")
    error: str = Field(description="エラーメッセージ")
    detail: str | None = Field(default=None, description="詳細なエラー情報")

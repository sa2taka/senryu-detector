"""川柳検知のためのデータモデル。."""

from __future__ import annotations

from .api import (
    DetectRequest,
    DetectResponse,
    ErrorResponse,
    HealthResponse,
)
from .senryu import DetectionResult, SenryuPattern, SenryuPhrase, Token

__all__ = [
    # Core models
    "DetectionResult",
    "SenryuPattern",
    "SenryuPhrase",
    "Token",
    # API models
    "DetectRequest",
    "DetectResponse",
    "HealthResponse",
    "ErrorResponse",
]

"""日本の詩歌のための川柳検知器。."""

from __future__ import annotations

from .core.detector import SenryuDetector
from .models.senryu import DetectionResult, SenryuPattern, SenryuPhrase, Token

__version__ = "0.1.0"

__all__ = [
    "SenryuDetector",
    "DetectionResult",
    "SenryuPattern",
    "SenryuPhrase",
    "Token",
]

"""川柳検知のためのデータモデル。."""

from __future__ import annotations

from .senryu import DetectionResult, SenryuPattern, SenryuPhrase, Token

__all__ = ["DetectionResult", "SenryuPattern", "SenryuPhrase", "Token"]

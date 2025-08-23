"""川柳検知のコアロジック。."""

from __future__ import annotations

from .detector import SenryuDetector
from .mora import count_mora, is_long_vowel, is_special_mora, is_youon
from .patterns import SENRYU_PATTERNS, is_valid_senryu_pattern

__all__ = [
    "SenryuDetector",
    "count_mora",
    "is_long_vowel",
    "is_special_mora",
    "is_youon",
    "SENRYU_PATTERNS",
    "is_valid_senryu_pattern",
]

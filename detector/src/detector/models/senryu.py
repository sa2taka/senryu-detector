"""川柳構造と検知結果のデータモデル。."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class SenryuPattern(Enum):
    """サポートされる川柳パターン。."""

    STANDARD = "5-7-5"  # 標準川柳
    JIAMARI_1 = "5-8-5"  # 字余り川柳（中句8音）
    JIAMARI_2 = "6-7-5"  # 字余り川柳（上句6音）
    JIAMARI_3 = "5-7-6"  # 字余り川柳（下句6音）


class Token(BaseModel):
    """形態素解析トークン。."""

    surface: str = Field(description="Surface form of the token")
    reading: str = Field(description="Reading in katakana")
    mora_count: int = Field(description="Number of mora in this token", ge=0)
    pos: str = Field(description="Part of speech")


class SenryuPhrase(BaseModel):
    """川柳内のフレーズ（上句/中句/下句）。."""

    tokens: list[Token] = Field(description="Tokens comprising this phrase")
    mora_count: int = Field(description="Total mora count of this phrase", ge=0)
    text: str = Field(description="Original text of this phrase")
    reading: str = Field(description="Reading of this phrase in hiragana")

    @property
    def surface_text(self) -> str:
        """トークンから表層テキストを取得。."""
        return "".join(token.surface for token in self.tokens)


class DetectionResult(BaseModel):
    """川柳検知の結果。."""

    pattern: SenryuPattern = Field(description="Detected senryu pattern")
    upper_phrase: SenryuPhrase = Field(description="Upper phrase (上句)")
    middle_phrase: SenryuPhrase = Field(description="Middle phrase (中句)")
    lower_phrase: SenryuPhrase = Field(description="Lower phrase (下句)")
    start_position: int = Field(description="Start position in original text", ge=0)
    end_position: int = Field(description="End position in original text", ge=0)
    original_text: str = Field(description="Original text segment")
    is_valid: bool = Field(description="Whether this is a valid senryu", default=True)

    @property
    def mora_pattern(self) -> tuple[int, int, int]:
        """モーラパターンをタプルで取得。."""
        return (
            self.upper_phrase.mora_count,
            self.middle_phrase.mora_count,
            self.lower_phrase.mora_count,
        )

    @property
    def full_reading(self) -> str:
        """川柳の完全な読みを取得。."""
        return (
            f"{self.upper_phrase.reading} {self.middle_phrase.reading} {self.lower_phrase.reading}"
        )

    @property
    def is_standard_pattern(self) -> bool:
        """標準の5-7-5パターンかどうかをチェック。."""
        return self.pattern == SenryuPattern.STANDARD

    def __str__(self) -> str:
        """検知結果の文字列表現。."""
        pattern_str = "-".join(map(str, self.mora_pattern))
        status = "✅" if self.is_valid else "❌"
        return f"{status} [{pattern_str}] {self.original_text}"

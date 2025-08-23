"""Tests for senryu data models."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from detector.models.senryu import (
    DetectionResult,
    SenryuPattern,
    SenryuPhrase,
    Token,
)


class TestToken:
    """Test Token model."""

    def test_valid_token(self) -> None:
        """Test valid token creation."""
        token = Token(
            surface="春",
            reading="はる",
            mora_count=2,
            pos="名詞",
        )

        assert token.surface == "春"
        assert token.reading == "はる"
        assert token.mora_count == 2
        assert token.pos == "名詞"

    def test_zero_mora_count(self) -> None:
        """Test token with zero mora count."""
        token = Token(
            surface="の",
            reading="の",
            mora_count=0,
            pos="助詞",
        )

        assert token.mora_count == 0

    def test_negative_mora_count_invalid(self) -> None:
        """Test negative mora count is invalid."""
        with pytest.raises(ValidationError):
            Token(
                surface="test",
                reading="test",
                mora_count=-1,
                pos="test",
            )

    def test_empty_surface_invalid(self) -> None:
        """Test empty surface is invalid."""
        with pytest.raises(ValidationError):
            Token(
                surface="",
                reading="test",
                mora_count=1,
                pos="test",
            )

    def test_empty_reading_invalid(self) -> None:
        """Test empty reading is invalid."""
        with pytest.raises(ValidationError):
            Token(
                surface="test",
                reading="",
                mora_count=1,
                pos="test",
            )

    def test_empty_pos_invalid(self) -> None:
        """Test empty pos is invalid."""
        with pytest.raises(ValidationError):
            Token(
                surface="test",
                reading="test",
                mora_count=1,
                pos="",
            )


class TestSenryuPhrase:
    """Test SenryuPhrase model."""

    def test_valid_phrase(self) -> None:
        """Test valid phrase creation."""
        tokens = [
            Token(surface="古", reading="ふる", mora_count=2, pos="形容詞"),
            Token(surface="池", reading="いけ", mora_count=2, pos="名詞"),
            Token(surface="や", reading="や", mora_count=1, pos="助詞"),
        ]

        phrase = SenryuPhrase(
            tokens=tokens,
            mora_count=5,
            text="古池や",
            reading="ふるいけや",
        )

        assert len(phrase.tokens) == 3
        assert phrase.mora_count == 5
        assert phrase.text == "古池や"
        assert phrase.reading == "ふるいけや"

    def test_empty_tokens_invalid(self) -> None:
        """Test empty tokens list is invalid."""
        with pytest.raises(ValidationError):
            SenryuPhrase(
                tokens=[],
                mora_count=5,
                text="test",
                reading="test",
            )

    def test_negative_mora_count_invalid(self) -> None:
        """Test negative mora count is invalid."""
        tokens = [Token(surface="test", reading="test", mora_count=1, pos="test")]

        with pytest.raises(ValidationError):
            SenryuPhrase(
                tokens=tokens,
                mora_count=-1,
                text="test",
                reading="test",
            )


class TestDetectionResult:
    """Test DetectionResult model."""

    def test_valid_result(self) -> None:
        """Test valid detection result creation."""
        tokens = [Token(surface="古", reading="ふる", mora_count=2, pos="形容詞")]
        phrase = SenryuPhrase(
            tokens=tokens,
            mora_count=5,
            text="古池や",
            reading="ふるいけや",
        )

        result = DetectionResult(
            pattern=SenryuPattern.STANDARD,
            upper_phrase=phrase,
            middle_phrase=phrase,  # Simplified for test
            lower_phrase=phrase,
            is_valid=True,
            start_position=0,
            end_position=15,
            original_text="古池や蛙飛び込む水の音",
        )

        assert result.pattern == SenryuPattern.STANDARD
        assert result.is_valid is True
        assert result.start_position == 0
        assert result.end_position == 15

    def test_mora_pattern_property(self) -> None:
        """Test mora_pattern property."""
        upper = SenryuPhrase(
            tokens=[Token(surface="上", reading="かみ", mora_count=2, pos="名詞")],
            mora_count=5,
            text="上句",
            reading="かみく",
        )
        middle = SenryuPhrase(
            tokens=[Token(surface="中", reading="なか", mora_count=2, pos="名詞")],
            mora_count=7,
            text="中句",
            reading="なかく",
        )
        lower = SenryuPhrase(
            tokens=[Token(surface="下", reading="しも", mora_count=2, pos="名詞")],
            mora_count=5,
            text="下句",
            reading="しもく",
        )

        result = DetectionResult(
            pattern=SenryuPattern.STANDARD,
            upper_phrase=upper,
            middle_phrase=middle,
            lower_phrase=lower,
            is_valid=True,
            start_position=0,
            end_position=12,
            original_text="上句中句下句",
        )

        assert result.mora_pattern == (5, 7, 5)

    def test_full_reading_property(self) -> None:
        """Test full_reading property."""
        upper = SenryuPhrase(
            tokens=[Token(surface="上", reading="かみ", mora_count=2, pos="名詞")],
            mora_count=5,
            text="上句",
            reading="かみく",
        )
        middle = SenryuPhrase(
            tokens=[Token(surface="中", reading="なか", mora_count=2, pos="名詞")],
            mora_count=7,
            text="中句",
            reading="なかく",
        )
        lower = SenryuPhrase(
            tokens=[Token(surface="下", reading="しも", mora_count=2, pos="名詞")],
            mora_count=5,
            text="下句",
            reading="しもく",
        )

        result = DetectionResult(
            pattern=SenryuPattern.STANDARD,
            upper_phrase=upper,
            middle_phrase=middle,
            lower_phrase=lower,
            is_valid=True,
            start_position=0,
            end_position=12,
            original_text="上句中句下句",
        )

        assert result.full_reading == "かみくなかくしもく"

    def test_invalid_positions(self) -> None:
        """Test invalid position values."""
        tokens = [Token(surface="test", reading="test", mora_count=1, pos="test")]
        phrase = SenryuPhrase(
            tokens=tokens,
            mora_count=5,
            text="test",
            reading="test",
        )

        # Negative start position
        with pytest.raises(ValidationError):
            DetectionResult(
                pattern=SenryuPattern.STANDARD,
                upper_phrase=phrase,
                middle_phrase=phrase,
                lower_phrase=phrase,
                is_valid=True,
                start_position=-1,
                end_position=5,
                original_text="test",
            )

        # Start position > end position
        with pytest.raises(ValidationError):
            DetectionResult(
                pattern=SenryuPattern.STANDARD,
                upper_phrase=phrase,
                middle_phrase=phrase,
                lower_phrase=phrase,
                is_valid=True,
                start_position=10,
                end_position=5,
                original_text="test",
            )

    def test_is_valid_validation(self) -> None:
        """Test is_valid field validation."""
        tokens = [Token(surface="test", reading="test", mora_count=1, pos="test")]
        phrase = SenryuPhrase(
            tokens=tokens,
            mora_count=5,
            text="test",
            reading="test",
        )

        # Valid is_valid
        result = DetectionResult(
            pattern=SenryuPattern.STANDARD,
            upper_phrase=phrase,
            middle_phrase=phrase,
            lower_phrase=phrase,
            is_valid=False,
            start_position=0,
            end_position=5,
            original_text="test",
        )

        assert result.is_valid is False

    def test_string_representation(self) -> None:
        """Test string representation."""
        tokens = [Token(surface="古", reading="ふる", mora_count=2, pos="形容詞")]
        phrase = SenryuPhrase(
            tokens=tokens,
            mora_count=5,
            text="古池や",
            reading="ふるいけや",
        )

        # Valid result
        valid_result = DetectionResult(
            pattern=SenryuPattern.STANDARD,
            upper_phrase=phrase,
            middle_phrase=phrase,
            lower_phrase=phrase,
            is_valid=True,
            start_position=0,
            end_position=15,
            original_text="古池や蛙飛び込む水の音",
        )

        str_repr = str(valid_result)
        assert "✅" in str_repr
        assert "5-7-5" in str_repr

        # Invalid result
        invalid_result = DetectionResult(
            pattern=SenryuPattern.STANDARD,
            upper_phrase=phrase,
            middle_phrase=phrase,
            lower_phrase=phrase,
            is_valid=False,
            start_position=0,
            end_position=15,
            original_text="古池や蛙飛び込む水の音",
        )

        str_repr = str(invalid_result)
        assert "❌" in str_repr


class TestSenryuPattern:
    """Test SenryuPattern enum."""

    def test_pattern_values(self) -> None:
        """Test pattern enum values."""
        assert SenryuPattern.STANDARD.value == "5-7-5"
        assert SenryuPattern.JIAMARI_1.value == "5-8-5"
        assert SenryuPattern.JIAMARI_2.value == "6-7-5"
        assert SenryuPattern.JIAMARI_3.value == "5-7-6"

    def test_pattern_completeness(self) -> None:
        """Test that all expected patterns are defined."""
        patterns = list(SenryuPattern)
        assert len(patterns) == 4

        pattern_values = {p.value for p in patterns}
        expected = {"5-7-5", "5-8-5", "6-7-5", "5-7-6"}
        assert pattern_values == expected

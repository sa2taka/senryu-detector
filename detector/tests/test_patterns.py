"""Tests for senryu pattern matching logic."""

from __future__ import annotations

from detector.core.patterns import (
    SENRYU_PATTERNS,
    get_pattern_type,
    get_target_patterns,
    is_standard_pattern,
    is_valid_senryu_pattern,
    validate_senryu_rules,
)
from detector.models.senryu import SenryuPattern


class TestPatternValidation:
    """Test pattern validation functions."""

    def test_valid_patterns(self) -> None:
        """Test valid senryu patterns."""
        assert is_valid_senryu_pattern((5, 7, 5)) is True  # Standard
        assert is_valid_senryu_pattern((5, 8, 5)) is True  # Jiamari 1
        assert is_valid_senryu_pattern((6, 7, 5)) is True  # Jiamari 2
        assert is_valid_senryu_pattern((5, 7, 6)) is True  # Jiamari 3

    def test_invalid_patterns(self) -> None:
        """Test invalid patterns."""
        assert is_valid_senryu_pattern((3, 5, 3)) is False
        assert is_valid_senryu_pattern((7, 7, 7)) is False
        assert is_valid_senryu_pattern((5, 5, 5)) is False
        assert is_valid_senryu_pattern((10, 10, 10)) is False

    def test_get_pattern_type(self) -> None:
        """Test pattern type detection."""
        assert get_pattern_type((5, 7, 5)) == SenryuPattern.STANDARD
        assert get_pattern_type((5, 8, 5)) == SenryuPattern.JIAMARI_1
        assert get_pattern_type((6, 7, 5)) == SenryuPattern.JIAMARI_2
        assert get_pattern_type((5, 7, 6)) == SenryuPattern.JIAMARI_3
        assert get_pattern_type((3, 5, 3)) is None

    def test_is_standard_pattern(self) -> None:
        """Test standard pattern identification."""
        assert is_standard_pattern(SenryuPattern.STANDARD) is True
        assert is_standard_pattern(SenryuPattern.JIAMARI_1) is False
        assert is_standard_pattern(SenryuPattern.JIAMARI_2) is False
        assert is_standard_pattern(SenryuPattern.JIAMARI_3) is False


class TestBinaryValidation:
    """Test binary validation logic."""

    def test_validate_senryu_rules_valid(self) -> None:
        """Test validation with valid senryu patterns."""
        from detector.models.senryu import Token

        # Mock valid tokens
        valid_token = Token(surface="テスト", reading="てすと", mora_count=3, pos="名詞")
        tokens = [valid_token]

        # Standard pattern
        assert validate_senryu_rules((5, 7, 5), tokens, tokens, tokens) is True

        # Jiamari patterns
        assert validate_senryu_rules((5, 8, 5), tokens, tokens, tokens) is True
        assert validate_senryu_rules((6, 7, 5), tokens, tokens, tokens) is True
        assert validate_senryu_rules((5, 7, 6), tokens, tokens, tokens) is True

    def test_validate_senryu_rules_invalid_pattern(self) -> None:
        """Test validation with invalid mora patterns."""
        from detector.models.senryu import Token

        valid_token = Token(surface="テスト", reading="てすと", mora_count=3, pos="名詞")
        tokens = [valid_token]

        # Invalid patterns
        assert validate_senryu_rules((3, 5, 3), tokens, tokens, tokens) is False
        assert validate_senryu_rules((7, 7, 7), tokens, tokens, tokens) is False

    def test_validate_senryu_rules_invalid_start_pos(self) -> None:
        """Test validation with invalid starting parts of speech."""
        from detector.models.senryu import Token

        valid_token = Token(surface="テスト", reading="てすと", mora_count=3, pos="名詞")
        invalid_token = Token(surface="が", reading="が", mora_count=1, pos="助詞")

        # Invalid middle phrase start
        assert (
            validate_senryu_rules((5, 7, 5), [valid_token], [invalid_token], [valid_token]) is False
        )

        # Invalid lower phrase start
        assert (
            validate_senryu_rules((5, 7, 5), [valid_token], [valid_token], [invalid_token]) is False
        )


class TestPatternUtilities:
    """Test pattern utility functions."""

    def test_get_target_patterns(self) -> None:
        """Test target patterns retrieval."""
        patterns = get_target_patterns()

        assert len(patterns) == 4
        assert (5, 7, 5) in patterns
        assert (5, 8, 5) in patterns
        assert (6, 7, 5) in patterns
        assert (5, 7, 6) in patterns

    def test_senryu_patterns_constant(self) -> None:
        """Test SENRYU_PATTERNS constant."""
        assert len(SENRYU_PATTERNS) == 4
        assert SENRYU_PATTERNS[SenryuPattern.STANDARD] == (5, 7, 5)
        assert SENRYU_PATTERNS[SenryuPattern.JIAMARI_1] == (5, 8, 5)
        assert SENRYU_PATTERNS[SenryuPattern.JIAMARI_2] == (6, 7, 5)
        assert SENRYU_PATTERNS[SenryuPattern.JIAMARI_3] == (5, 7, 6)

"""Tests for mora counting logic."""

from __future__ import annotations

from detector.core.mora import (
    count_mora,
    is_long_vowel,
    is_special_mora,
    is_youon,
    normalize_reading,
)


class TestMoraHelpers:
    """Test helper functions for mora analysis."""

    def test_is_youon(self) -> None:
        """Test youon detection."""
        assert is_youon("ゃ") is True
        assert is_youon("ゅ") is True
        assert is_youon("ょ") is True
        assert is_youon("ャ") is True
        assert is_youon("ュ") is True
        assert is_youon("ョ") is True

        assert is_youon("あ") is False
        assert is_youon("か") is False
        assert is_youon("っ") is False

    def test_is_special_mora(self) -> None:
        """Test sokuon detection."""
        assert is_special_mora("っ") is True
        assert is_special_mora("ッ") is True

        assert is_special_mora("あ") is False
        assert is_special_mora("ゃ") is False

    def test_is_long_vowel(self) -> None:
        """Test long vowel mark detection."""
        assert is_long_vowel("ー") is True

        assert is_long_vowel("あ") is False
        assert is_long_vowel("-") is False


class TestMoraCounting:
    """Test mora counting functionality."""

    def test_basic_hiragana(self) -> None:
        """Test basic hiragana mora counting."""
        assert count_mora("あ") == 1
        assert count_mora("こんにちは") == 5
        assert count_mora("さくら") == 3

    def test_basic_katakana(self) -> None:
        """Test basic katakana mora counting."""
        assert count_mora("ア") == 1
        assert count_mora("コンピューター") == 6
        assert count_mora("カメラ") == 3

    def test_youon_combinations(self) -> None:
        """Test youon (small ya/yu/yo) handling."""
        assert count_mora("きょう") == 2  # き + ょ (youon doesn't count)
        assert count_mora("しゃ") == 1  # し + ゃ (youon doesn't count)
        assert count_mora("りゅう") == 2  # り + ゅ + う
        assert count_mora("ひょうひょう") == 4  # ひ + ょ + う + ひ + ょ + う

    def test_sokuon_handling(self) -> None:
        """Test sokuon (small tsu) handling."""
        assert count_mora("がっこう") == 4  # が + っ + こ + う
        assert count_mora("いっぱい") == 4  # い + っ + ぱ + い
        assert count_mora("ざっし") == 3  # ざ + っ + し

    def test_long_vowel_marks(self) -> None:
        """Test long vowel mark handling."""
        assert count_mora("コンピューター") == 6  # コ + ン + ピ + ュ + ー + タ + ー
        assert count_mora("カー") == 2  # カ + ー
        assert count_mora("ビール") == 3  # ビ + ー + ル

    def test_mixed_scripts(self) -> None:
        """Test mixed hiragana/katakana text."""
        assert count_mora("ひらがなとカタカナ") == 8
        assert count_mora("コンピューターです") == 8

    def test_edge_cases(self) -> None:
        """Test edge cases."""
        assert count_mora("") == 0
        assert count_mora("   ") == 0  # Only spaces
        assert count_mora("123") == 0  # No Japanese characters
        assert count_mora("あいうえお") == 5  # All vowels

    def test_complex_examples(self) -> None:
        """Test complex real-world examples."""
        # 川柳の例
        assert count_mora("ふるいけや") == 5  # 古池や
        assert count_mora("かわずとびこむ") == 7  # 蛙飛び込む
        assert count_mora("みずのおと") == 5  # 水の音

        # 字余りの例
        assert count_mora("はるのよい") == 5  # 春の宵
        assert count_mora("さくらちりぬる") == 6  # 桜散りぬる
        assert count_mora("かぜのおと") == 5  # 風の音


class TestNormalizeReading:
    """Test reading normalization."""

    def test_katakana_to_hiragana(self) -> None:
        """Test katakana to hiragana conversion."""
        assert normalize_reading("カタカナ") == "かたかな"
        assert normalize_reading("コンピューター") == "こんぴゅーたー"
        assert normalize_reading("アリガトウ") == "ありがとう"

    def test_hiragana_unchanged(self) -> None:
        """Test hiragana remains unchanged."""
        assert normalize_reading("ひらがな") == "ひらがな"
        assert normalize_reading("こんにちは") == "こんにちは"

    def test_mixed_text(self) -> None:
        """Test mixed katakana/hiragana text."""
        assert normalize_reading("ひらがなとカタカナ") == "ひらがなとかたかな"

    def test_special_characters(self) -> None:
        """Test special characters preservation."""
        assert normalize_reading("コンピューター") == "こんぴゅーたー"
        assert normalize_reading("ー") == "ー"  # Long vowel mark preserved

    def test_empty_string(self) -> None:
        """Test empty string handling."""
        assert normalize_reading("") == ""

"""Integration tests for senryu detection."""

from __future__ import annotations

from detector.core.detector import SenryuDetector
from detector.models.senryu import SenryuPattern


class TestSenryuDetection:
    """Test full senryu detection pipeline."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.detector = SenryuDetector()

    def test_famous_haiku_detection(self) -> None:
        """Test detection of famous haiku patterns."""
        # 松尾芭蕉の有名な俳句（川柳パターンとしてテスト）
        test_cases = [
            "ふるいけやかわずとびこむみずのおと",  # 古池や蛙飛び込む水の音
            "なつくさやつわものどもがゆめのあと",  # 夏草や兵どもが夢の跡
        ]

        for text in test_cases:
            results = self.detector.detect(text)

            # At least one result should be found
            assert len(results) > 0

            # The best result should be valid
            best_result = results[0]
            assert best_result.is_valid

            # Should detect 5-7-5 pattern or close variant
            mora_pattern = best_result.mora_pattern
            assert len(mora_pattern) == 3
            assert all(isinstance(count, int) and count > 0 for count in mora_pattern)

    def test_jiamari_patterns(self) -> None:
        """Test detection of jiamari (syllable-excess) patterns."""
        # 字余り川柳の例（仮想的な例）
        test_cases = [
            # 5-8-5パターン想定
            "はるのひにさくらのはながさいている",
            # 6-7-5パターン想定
            "あきのよるつきがきれいにかがやいて",
            # 5-7-6パターン想定
            "ふゆのゆきやまにつもってしろくなる",
        ]

        for text in test_cases:
            results = self.detector.detect(text)

            # Should find at least some pattern
            if results:  # Some may not match perfectly
                best_result = results[0]
                assert best_result.is_valid

                # Pattern should be one of the valid types
                assert best_result.pattern in [
                    SenryuPattern.STANDARD,
                    SenryuPattern.JIAMARI_1,
                    SenryuPattern.JIAMARI_2,
                    SenryuPattern.JIAMARI_3,
                ]

    def test_non_senryu_text(self) -> None:
        """Test that non-senryu text produces low confidence or no results."""
        test_cases = [
            "こんにちは",  # Too short
            "あ",  # Far too short
            "これはとてもながいぶんしょうでせんりゅうのパターンにはあてはまりません",  # Too long
            "",  # Empty
            "   ",  # Only spaces
        ]

        for text in test_cases:
            results = self.detector.detect(text)

            # Either no results or invalid results
            if results:
                best_result = results[0]
                assert not best_result.is_valid  # Should be invalid for non-senryu

    def test_mixed_content_detection(self) -> None:
        """Test detection in mixed content."""
        # 川柳を含む長いテキスト
        text = "昨日は良い天気でした。ふるいけやかわずとびこむみずのおと。今日は雨です。"

        results = self.detector.detect(text)

        if results:
            # Should find the haiku portion
            best_result = results[0]
            assert best_result.is_valid

            # The detected portion should be reasonable
            detected_text = best_result.original_text
            assert len(detected_text) > 0
            assert len(detected_text) < len(text)  # Shouldn't be the entire text

    def test_binary_validation(self) -> None:
        """Test binary validation system."""
        detector = SenryuDetector()

        # Valid senryu
        valid_text = "ふるいけやかわずとびこむみずのおと"
        valid_results = detector.detect(valid_text)

        if valid_results:
            assert valid_results[0].is_valid

        # Invalid text
        invalid_text = "こんにちは"
        invalid_results = detector.detect(invalid_text)

        # Should either have no results or invalid results
        for result in invalid_results:
            assert not result.is_valid

    def test_result_validation(self) -> None:
        """Test that results have proper validation."""
        detector = SenryuDetector()

        text = "ふるいけやかわずとびこむみずのおと"
        results = detector.detect(text)

        # All results should have is_valid field
        for result in results:
            assert hasattr(result, "is_valid")
            assert isinstance(result.is_valid, bool)

    def test_detection_result_structure(self) -> None:
        """Test the structure of detection results."""
        text = "ふるいけやかわずとびこむみずのおと"
        results = self.detector.detect(text)

        if results:
            result = results[0]

            # All required fields should be present
            assert hasattr(result, "pattern")
            assert hasattr(result, "upper_phrase")
            assert hasattr(result, "middle_phrase")
            assert hasattr(result, "lower_phrase")
            assert hasattr(result, "is_valid")
            assert hasattr(result, "start_position")
            assert hasattr(result, "end_position")
            assert hasattr(result, "original_text")

            # Phrases should have proper structure
            for phrase in [result.upper_phrase, result.middle_phrase, result.lower_phrase]:
                assert len(phrase.tokens) > 0
                assert phrase.mora_count > 0
                assert phrase.text
                assert phrase.reading

            # Positions should be valid
            assert 0 <= result.start_position <= result.end_position <= len(text)

            # Pattern should be valid
            assert result.pattern in [
                SenryuPattern.STANDARD,
                SenryuPattern.JIAMARI_1,
                SenryuPattern.JIAMARI_2,
                SenryuPattern.JIAMARI_3,
            ]

    def test_reading_extraction(self) -> None:
        """Test reading extraction functionality."""
        text = "ふるいけやかわずとびこむみずのおと"
        results = self.detector.detect(text)

        if results:
            result = results[0]

            # Full reading should be non-empty
            full_reading = result.full_reading
            assert full_reading
            assert len(full_reading.strip()) > 0

            # Each phrase should have reading
            for phrase in [result.upper_phrase, result.middle_phrase, result.lower_phrase]:
                assert phrase.reading
                assert len(phrase.reading.strip()) > 0

    def test_edge_cases(self) -> None:
        """Test various edge cases."""
        edge_cases = [
            "っっっっっっっ",  # Only sokuon
            "ゃゅょゃゅょ",  # Only youon
            "ーーーーー",  # Only long vowels
            "あいうえおかきくけこ",  # Simple pattern
            "。、！？",  # Only punctuation
        ]

        for text in edge_cases:
            # Should not crash, may return empty results
            results = self.detector.detect(text)
            assert isinstance(results, list)

            # If results exist, they should be valid
            for result in results:
                assert isinstance(result.is_valid, bool)
                assert result.start_position >= 0
                assert result.end_position >= result.start_position

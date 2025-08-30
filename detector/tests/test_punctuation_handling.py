"""Tests for punctuation and symbol handling in senryu detection."""

from __future__ import annotations

from detector.core.detector import SenryuDetector
from detector.tokenizer.sudachi import SudachiTokenizer


class TestPunctuationHandling:
    """Test punctuation handling in senryu detection."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.detector = SenryuDetector()
        self.tokenizer = SudachiTokenizer()

    def test_sentence_boundary_exclusion(self) -> None:
        """Test that senryu crossing sentence boundaries are not detected."""
        # 句点をまたいだテキストは川柳として検知されないべき
        text = "ネコ。犬は困ったもの、ではあるね"
        results = self.detector.detect(text)

        # 句点をまたいだ川柳は検知されない
        assert len(results) == 0, "句点をまたいだテキストが川柳として検知された"

    def test_exclamation_mark_exclusion(self) -> None:
        """Test that senryu crossing exclamation marks are not detected."""
        text = "春が来た！花が咲いて、美しいね"
        results = self.detector.detect(text)

        # 感嘆符をまたいだ川柳は検知されない
        valid_results = [r for r in results if r.is_valid]
        assert len(valid_results) == 0, "感嘆符をまたいだテキストが川柳として検知された"

    def test_question_mark_exclusion(self) -> None:
        """Test that senryu crossing question marks are not detected."""
        text = "何だろう？これは不思議、な出来事だ"
        results = self.detector.detect(text)

        # 疑問符をまたいだ川柳は検知されない
        valid_results = [r for r in results if r.is_valid]
        assert len(valid_results) == 0, "疑問符をまたいだテキストが川柳として検知された"

    def test_symbol_reading_handling(self) -> None:
        """Test that symbols have empty readings and zero mora count."""
        # 句点を含むテキストをトークナイズ
        text = "春が来た。"
        tokens = self.tokenizer.tokenize(text)

        # 句点トークンを見つける
        period_token = None
        for token in tokens:
            if token.surface == "。":
                period_token = token
                break

        assert period_token is not None, "句点トークンが見つからない"
        assert period_token.reading == "", f"句点の読みが空文字列でない: {period_token.reading}"
        assert period_token.mora_count == 0, f"句点のモーラ数が0でない: {period_token.mora_count}"
        assert period_token.pos == "補助記号", f"句点の品詞が補助記号でない: {period_token.pos}"

    def test_comma_reading_handling(self) -> None:
        """Test that commas have appropriate handling."""
        text = "春が来て、花が咲いた"
        tokens = self.tokenizer.tokenize(text)

        # 読点トークンを見つける
        comma_token = None
        for token in tokens:
            if token.surface == "、":
                comma_token = token
                break

        if comma_token is not None:
            # 読点が補助記号として認識された場合
            if comma_token.pos == "補助記号":
                assert (
                    comma_token.reading == ""
                ), f"読点の読みが空文字列でない: {comma_token.reading}"
                assert (
                    comma_token.mora_count == 0
                ), f"読点のモーラ数が0でない: {comma_token.mora_count}"

    def test_valid_senryu_without_punctuation(self) -> None:
        """Test that valid senryu without punctuation are still detected."""
        # 句点なしの有効な川柳
        text = "古池や蛙飛び込む水の音"
        results = self.detector.detect(text)

        valid_results = [r for r in results if r.is_valid]
        assert len(valid_results) > 0, "有効な川柳が検知されなかった"

        # 最初の結果をチェック
        result = valid_results[0]
        assert result.mora_pattern == (5, 7, 5), f"予期しないモーラパターン: {result.mora_pattern}"

    def test_senryu_with_trailing_punctuation(self) -> None:
        """Test senryu with punctuation at the end."""
        # 末尾に句点がある川柳
        text = "古池や蛙飛び込む水の音。"
        results = self.detector.detect(text)

        valid_results = [r for r in results if r.is_valid]
        # 句点より前の部分で川柳が検知される可能性がある
        if valid_results:
            result = valid_results[0]
            # 句点を含まない原文テキストであることを確認
            assert "。" not in result.original_text, "川柳の原文テキストに句点が含まれている"

    def test_multiple_sentences_no_cross_detection(self) -> None:
        """Test that senryu are not detected across multiple sentences."""
        text = "春が来た。花が咲いて。鳥も歌う。"
        results = self.detector.detect(text)

        # 各文が短すぎて川柳にならないため、検知されない
        valid_results = [r for r in results if r.is_valid]

        # もし検知された場合は、句点をまたいでいないことを確認
        for result in valid_results:
            assert (
                "。" not in result.original_text
            ), f"検知された川柳に句点が含まれている: {result.original_text}"

    def test_symbol_varieties(self) -> None:
        """Test handling of various symbols."""
        symbols = ["。", "、", "！", "？", "!", "?", "：", "；"]

        for symbol in symbols:
            text = f"テスト{symbol}文字列"
            tokens = self.tokenizer.tokenize(text)

            symbol_token = None
            for token in tokens:
                if token.surface == symbol:
                    symbol_token = token
                    break

            if symbol_token is not None and symbol_token.pos == "補助記号":
                assert (
                    symbol_token.reading == ""
                ), f"記号'{symbol}'の読みが空文字列でない: {symbol_token.reading}"
                assert (
                    symbol_token.mora_count == 0
                ), f"記号'{symbol}'のモーラ数が0でない: {symbol_token.mora_count}"

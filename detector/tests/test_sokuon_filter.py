"""Tests for the sokuon ending filter."""

from __future__ import annotations

from detector.core.filters.sokuon import SokuonEndingFilter
from detector.core.splitters.base import SplitResult
from detector.models.senryu import Token


class TestSokuonEndingFilter:
    """促音終了フィルターのテスト。."""

    def setup_method(self) -> None:
        """テストセットアップ。."""
        self.filter = SokuonEndingFilter()

    def test_allows_normal_phrases(self) -> None:
        """通常の句（促音で終わらない）を許可することをテスト。."""
        # 上句：「古池や」（こいけや）
        upper_tokens = [
            Token(surface="古池", reading="コイケ", pos="名詞", mora_count=3),
            Token(surface="や", reading="ヤ", pos="助詞", mora_count=1),
        ]
        # 中句：「蛙飛び込む」（かわずとびこむ）
        middle_tokens = [
            Token(surface="蛙", reading="カワズ", pos="名詞", mora_count=3),
            Token(surface="飛び込む", reading="トビコム", pos="動詞", mora_count=4),
        ]
        # 下句：「水の音」（みずのおと）
        lower_tokens = [
            Token(surface="水", reading="ミズ", pos="名詞", mora_count=2),
            Token(surface="の", reading="ノ", pos="助詞", mora_count=1),
            Token(surface="音", reading="オト", pos="名詞", mora_count=2),
        ]

        split_result = SplitResult(
            upper_tokens=upper_tokens,
            middle_tokens=middle_tokens,
            lower_tokens=lower_tokens,
            score=10.0,
        )

        tokens = upper_tokens + middle_tokens + lower_tokens

        result = self.filter.apply(tokens, split_result=split_result)
        assert result is True

    def test_rejects_phrase_ending_with_sokuon(self) -> None:
        """促音で終わる句を拒否することをテスト。."""
        # 上句：「やっ」で終わる不自然な句
        upper_tokens = [
            Token(surface="やっ", reading="ヤッ", pos="感動詞", mora_count=2),
        ]
        # 中句：「それはだめだっ」で終わる句
        middle_tokens = [
            Token(surface="それは", reading="ソレワ", pos="連体詞", mora_count=3),
            Token(surface="だめ", reading="ダメ", pos="形容動詞", mora_count=2),
            Token(surface="だっ", reading="ダッ", pos="助動詞", mora_count=2),
        ]
        # 下句：通常の句
        lower_tokens = [
            Token(surface="思った", reading="オモッタ", pos="動詞", mora_count=4),
            Token(surface="よ", reading="ヨ", pos="助詞", mora_count=1),
        ]

        split_result = SplitResult(
            upper_tokens=upper_tokens,
            middle_tokens=middle_tokens,
            lower_tokens=lower_tokens,
            score=5.0,
        )

        tokens = upper_tokens + middle_tokens + lower_tokens

        result = self.filter.apply(tokens, split_result=split_result)
        assert result is False

    def test_allows_sokuon_followed_by_symbol(self) -> None:
        """促音の後に記号が続く場合は許可することをテスト。."""
        # 上句：「あっ。」のように感嘆符で終わる句
        upper_tokens = [
            Token(surface="あっ", reading="アッ", pos="感動詞", mora_count=2),
            Token(surface="。", reading="。", pos="補助記号", mora_count=0),
        ]
        # 中句：通常の句
        middle_tokens = [
            Token(surface="びっくり", reading="ビックリ", pos="副詞", mora_count=4),
            Token(surface="した", reading="シタ", pos="動詞", mora_count=2),
        ]
        # 下句：「やったっ！」のように感嘆符で終わる句
        lower_tokens = [
            Token(surface="やった", reading="ヤッタ", pos="動詞", mora_count=3),
            Token(surface="っ", reading="ッ", pos="記号", mora_count=1),
            Token(surface="！", reading="！", pos="補助記号", mora_count=0),
        ]

        split_result = SplitResult(
            upper_tokens=upper_tokens,
            middle_tokens=middle_tokens,
            lower_tokens=lower_tokens,
            score=8.0,
        )

        tokens = upper_tokens + middle_tokens + lower_tokens

        result = self.filter.apply(tokens, split_result=split_result)
        assert result is True

    def test_handles_empty_split_result(self) -> None:
        """split_resultが空の場合の処理をテスト。."""
        tokens = [Token(surface="テスト", reading="テスト", pos="名詞", mora_count=3)]

        result = self.filter.apply(tokens)
        assert result is True

    def test_handles_empty_phrases(self) -> None:
        """空の句がある場合の処理をテスト。."""
        upper_tokens: list[Token] = []
        middle_tokens = [
            Token(surface="真ん中", reading="マンナカ", pos="名詞", mora_count=4),
        ]
        lower_tokens: list[Token] = []

        split_result = SplitResult(
            upper_tokens=upper_tokens,
            middle_tokens=middle_tokens,
            lower_tokens=lower_tokens,
            score=3.0,
        )

        tokens = middle_tokens

        result = self.filter.apply(tokens, split_result=split_result)
        assert result is True

    def test_phrase_ends_with_sokuon_detection(self) -> None:
        """_phrase_ends_with_sokuon メソッドの動作をテスト。."""
        # 促音で終わる句
        sokuon_tokens = [
            Token(surface="言っ", reading="イッ", pos="動詞", mora_count=2),
        ]
        assert self.filter._phrase_ends_with_sokuon(sokuon_tokens) is True

        # 促音で終わらない句
        normal_tokens = [
            Token(surface="言った", reading="イッタ", pos="動詞", mora_count=3),
        ]
        assert self.filter._phrase_ends_with_sokuon(normal_tokens) is False

        # 空の句
        empty_tokens: list[Token] = []
        assert self.filter._phrase_ends_with_sokuon(empty_tokens) is False

    def test_has_symbol_after_sokuon_detection(self) -> None:
        """_has_symbol_after_sokuon メソッドの動作をテスト。."""
        # 記号を含むトークン
        symbol_token = Token(surface="！", reading="！", pos="補助記号", mora_count=0)
        symbol_tokens = [symbol_token]
        assert self.filter._has_symbol_after_sokuon(symbol_tokens) is True

        # 記号品詞のトークン
        punctuation_token = Token(surface="。", reading="。", pos="句読点", mora_count=0)
        punct_tokens = [punctuation_token]
        assert self.filter._has_symbol_after_sokuon(punct_tokens) is True

        # 通常のトークン
        normal_token = Token(surface="っ", reading="ッ", pos="動詞", mora_count=1)
        normal_tokens = [normal_token]
        assert self.filter._has_symbol_after_sokuon(normal_tokens) is False

    def test_integration_with_various_sokuon_patterns(self) -> None:
        """様々な促音パターンでの統合テスト。."""
        test_cases = [
            # (description, should_pass, upper, middle, lower)
            (
                "全て促音で終わる",
                False,
                [Token(surface="あっ", reading="アッ", pos="感動詞", mora_count=2)],
                [Token(surface="それっ", reading="ソレッ", pos="代名詞", mora_count=3)],
                [Token(surface="だっ", reading="ダッ", pos="助動詞", mora_count=2)],
            ),
            (
                "一つだけ促音で終わる",
                False,
                [Token(surface="古池", reading="コイケ", pos="名詞", mora_count=3)],
                [Token(surface="蛙", reading="カワズ", pos="名詞", mora_count=3)],
                [Token(surface="ぴょんっ", reading="ピョンッ", pos="副詞", mora_count=4)],
            ),
            (
                "促音＋記号で終わる",
                True,
                [
                    Token(surface="あっ", reading="アッ", pos="感動詞", mora_count=2),
                    Token(surface="！", reading="！", pos="補助記号", mora_count=0),
                ],
                [Token(surface="素晴らしい", reading="スバラシイ", pos="形容詞", mora_count=5)],
                [Token(surface="一日", reading="イチニチ", pos="名詞", mora_count=4)],
            ),
        ]

        for description, should_pass, upper, middle, lower in test_cases:
            split_result = SplitResult(
                upper_tokens=upper, middle_tokens=middle, lower_tokens=lower, score=5.0
            )

            tokens = upper + middle + lower
            result = self.filter.apply(tokens, split_result=split_result)

            assert result is should_pass, f"Test failed for: {description}"

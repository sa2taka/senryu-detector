"""川柳検知のメインエンジン（SLAP原則準拠）。."""

from __future__ import annotations

import re
from collections.abc import Iterator
from typing import Any

from ..models.senryu import DetectionResult, SenryuPattern, SenryuPhrase, Token
from ..tokenizer.sudachi import SudachiTokenizer
from .filters import (
    FilterChain,
    JapaneseCharacterFilter,
    MinimumTokenCountFilter,
    MoraCountFilter,
    PunctuationBoundaryFilter,
    SokuonEndingFilter,
    UnknownWordFilter,
)
from .patterns import (
    get_pattern_type,
    get_target_patterns,
    validate_senryu_rules,
)
from .splitters import AdaptivePOSSplitter


class SenryuDetector:
    """日本語テキストから川柳を検知するメインエンジン（SLAP準拠）。.

    高レベルのワークフロー管理に特化し、詳細な処理は専門モジュールに委譲。
    """

    def __init__(self) -> None:
        """川柳検知器を初期化。."""
        self.tokenizer = SudachiTokenizer(mode="C")
        self._init_filters()
        self._init_splitters()

    def _init_filters(self) -> None:
        """フィルタチェーンを初期化。."""
        self.filter_chain = FilterChain(
            [
                JapaneseCharacterFilter(),
                MinimumTokenCountFilter(min_count=3),
                PunctuationBoundaryFilter(),
                UnknownWordFilter(strict=True),
                MoraCountFilter(min_mora=12, max_mora=20, tolerance=4),
                SokuonEndingFilter(),
            ]
        )

    def _init_splitters(self) -> None:
        """句分割器を初期化。."""
        self.splitter = AdaptivePOSSplitter()

    def detect(self, text: str) -> list[DetectionResult]:
        """指定されたテキストから川柳を検知（高レベルワークフロー）。.

        Args:
            text: 分析する日本語テキスト

        Returns:
            検知された川柳のリスト
        """
        if not text.strip():
            return []

        # 1. テキスト前処理
        normalized_text = self._preprocess_text(text)
        if not normalized_text:
            return []

        # 2. 形態素解析
        tokens = self._tokenize_text(normalized_text)
        if not tokens:
            return []

        # 3. 川柳候補の生成と検証
        candidates = self._generate_and_validate_candidates(tokens, normalized_text)

        # 4. 結果の最適化と重複除去
        return self._optimize_results(candidates)

    def _preprocess_text(self, text: str) -> str | None:
        """テキストの前処理。.

        Args:
            text: 生テキスト

        Returns:
            正規化されたテキスト、処理不可能な場合はNone
        """
        # 日本語文字チェック
        if not self._contains_japanese(text):
            return None

        # テキスト正規化
        return self._normalize_text(text)

    def _tokenize_text(self, text: str) -> list[Token] | None:
        """テキストの形態素解析。.

        Args:
            text: 正規化済みテキスト

        Returns:
            トークンリスト、処理失敗時はNone
        """
        tokens = self.tokenizer.tokenize(text)
        return tokens if len(tokens) >= 3 else None

    def _generate_and_validate_candidates(
        self, tokens: list[Token], original_text: str
    ) -> list[DetectionResult]:
        """川柳候補の生成と検証。.

        Args:
            tokens: トークンリスト
            original_text: 元テキスト

        Returns:
            検証済み候補のリスト
        """
        # 候補生成とフィルタリング
        raw_candidates = self._find_senryu_candidates(tokens, original_text)
        filtered_candidates = list(self.filter_chain.filter_candidates(raw_candidates))

        # 各候補を検証
        validated_candidates = []
        for candidate_tokens in filtered_candidates:
            results = self._validate_candidate(candidate_tokens, original_text)
            validated_candidates.extend(results)

        return [result for result in validated_candidates if result.is_valid]

    def _optimize_results(self, candidates: list[DetectionResult]) -> list[DetectionResult]:
        """結果の最適化と重複除去。.

        Args:
            candidates: 検証済み候補

        Returns:
            最適化された結果
        """
        if not candidates:
            return []

        # 重複除去
        deduplicated = self._remove_duplicates(candidates)

        # 結果をスコア順にソート（メタデータにスコア情報がある場合）
        return sorted(deduplicated, key=lambda x: x.start_position)

    def _find_senryu_candidates(
        self, tokens: list[Token], original_text: str
    ) -> Iterator[list[Token]]:
        """スライディングウィンドウで川柳候補を探索。.

        Args:
            tokens: 形態素解析トークン
            original_text: 元テキスト

        Yields:
            候補トークンリスト
        """
        for start_idx in range(len(tokens)):
            for end_idx in range(start_idx + 3, min(len(tokens) + 1, start_idx + 20)):
                yield tokens[start_idx:end_idx]

    def _validate_candidate(self, tokens: list[Token], original_text: str) -> list[DetectionResult]:
        """候補トークンリストを川柳として検証。.

        Args:
            tokens: 候補トークンリスト
            original_text: 元テキスト

        Returns:
            検証結果のリスト
        """
        results = []
        target_patterns = get_target_patterns()

        for pattern in target_patterns:
            result = self._try_pattern_match(tokens, pattern, original_text)
            if result:
                results.append(result)

        return results

    def _try_pattern_match(
        self,
        tokens: list[Token],
        target_pattern: tuple[int, int, int],
        original_text: str,
    ) -> DetectionResult | None:
        """特定パターンでのマッチング試行。.

        Args:
            tokens: トークンリスト
            target_pattern: 目標モーラパターン
            original_text: 元テキスト

        Returns:
            マッチ結果、失敗時はNone
        """
        # 句分割を試行
        split_result = self.splitter.split(tokens, target_pattern)
        if not split_result:
            return None

        # フレーズオブジェクトを作成
        upper_phrase = self._create_phrase(split_result.upper_tokens)
        middle_phrase = self._create_phrase(split_result.middle_tokens)
        lower_phrase = self._create_phrase(split_result.lower_tokens)

        # パターンタイプを取得
        actual_pattern = split_result.mora_pattern
        pattern_type = get_pattern_type(actual_pattern)

        if not pattern_type:
            pattern_type = self._get_closest_pattern_type(actual_pattern)
            if not pattern_type:
                return None

        # 川柳ルールの厳密な検証
        is_valid = validate_senryu_rules(
            actual_pattern,
            split_result.upper_tokens,
            split_result.middle_tokens,
            split_result.lower_tokens,
        )

        # テキスト位置を計算
        start_pos, end_pos = self._calculate_text_positions(tokens, original_text)
        segment_text = original_text[start_pos:end_pos]

        return DetectionResult(
            pattern=pattern_type,
            upper_phrase=upper_phrase,
            middle_phrase=middle_phrase,
            lower_phrase=lower_phrase,
            start_position=start_pos,
            end_position=end_pos,
            original_text=segment_text,
            is_valid=is_valid,
        )

    def _create_phrase(self, tokens: list[Token]) -> SenryuPhrase:
        """トークンからSenryuPhraseを作成。.

        Args:
            tokens: フレーズ用のトークンリスト

        Returns:
            SenryuPhraseオブジェクト
        """
        text = "".join(token.surface for token in tokens)
        reading = "".join(token.reading for token in tokens)
        mora_count = sum(token.mora_count for token in tokens)

        return SenryuPhrase(
            tokens=tokens,
            mora_count=mora_count,
            text=text,
            reading=reading,
        )

    def _contains_japanese(self, text: str) -> bool:
        """テキストが日本語文字を含むかチェック。.

        Args:
            text: チェックするテキスト

        Returns:
            日本語文字を含む場合True
        """
        for char in text:
            if (
                "\u3040" <= char <= "\u309f"  # ひらがな
                or "\u30a0" <= char <= "\u30ff"  # カタカナ
                or "\u4e00" <= char <= "\u9fff"  # CJK統合漢字
                or "\u3400" <= char <= "\u4dbf"  # CJK拡張A
            ):
                return True
        return False

    def _normalize_text(self, text: str) -> str:
        """テキストの正規化。.

        Args:
            text: 入力生テキスト

        Returns:
            正規化されたテキスト
        """
        # 改行を句点に変換
        normalized = re.sub(r"\n", "。", text)
        # 複数の句点を1つに統合
        normalized = re.sub(r"。+", "。", normalized)
        # 複数の空白を1つに統合
        normalized = re.sub(r"\s+", " ", normalized)
        # 前後の空白を除去
        return normalized.strip()

    def _get_closest_pattern_type(self, pattern: tuple[int, int, int]) -> SenryuPattern | None:
        """最も近いパターンタイプを取得。.

        Args:
            pattern: モーラパターン

        Returns:
            最も近いSenryuPattern
        """
        target_patterns = get_target_patterns()
        best_distance = float("inf")
        best_pattern_type = None

        for target_pattern in target_patterns:
            distance = sum(abs(p - t) for p, t in zip(pattern, target_pattern, strict=False))
            if distance < best_distance:
                best_distance = distance
                best_pattern_type = get_pattern_type(target_pattern)

        return best_pattern_type

    def _calculate_text_positions(self, tokens: list[Token], original_text: str) -> tuple[int, int]:
        """元テキスト内の位置を計算。.

        Args:
            tokens: トークンリスト
            original_text: 元テキスト

        Returns:
            (start_pos, end_pos)のタプル
        """
        segment_text = "".join(token.surface for token in tokens)
        start_pos = original_text.find(segment_text)
        if start_pos == -1:
            start_pos = 0
        end_pos = start_pos + len(segment_text)
        return start_pos, min(end_pos, len(original_text))

    def _remove_duplicates(self, results: list[DetectionResult]) -> list[DetectionResult]:
        """重複除去。.

        Args:
            results: 川柳検知結果

        Returns:
            重複除去された結果
        """
        if not results:
            return []

        # 開始位置でグループ化
        position_groups: dict[int, list[DetectionResult]] = {}
        for result in results:
            start_pos = result.start_position
            if start_pos not in position_groups:
                position_groups[start_pos] = []
            position_groups[start_pos].append(result)

        # 各グループから最適な結果を選択
        selected_results = []
        for group in position_groups.values():
            if len(group) == 1:
                selected_results.append(group[0])
            else:
                best_result = self._select_best_result(group)
                selected_results.append(best_result)

        return sorted(selected_results, key=lambda x: x.start_position)

    def _select_best_result(self, candidates: list[DetectionResult]) -> DetectionResult:
        """候補から最適な結果を選択。.

        Args:
            candidates: 同じ開始位置の候補

        Returns:
            最適な結果
        """
        # 5-7-5パターンを優先
        standard_patterns = [c for c in candidates if c.pattern == SenryuPattern.STANDARD]
        if standard_patterns:
            return max(standard_patterns, key=lambda x: len(x.original_text))

        # 字余りパターンの中で最長のテキストを選択
        jiamari_patterns = [
            c
            for c in candidates
            if c.pattern
            in [SenryuPattern.JIAMARI_1, SenryuPattern.JIAMARI_2, SenryuPattern.JIAMARI_3]
        ]

        if jiamari_patterns:
            return max(jiamari_patterns, key=lambda x: len(x.original_text))

        # その他の場合は最長のテキストを選択
        return max(candidates, key=lambda x: len(x.original_text))

    # カスタマイズ用メソッド
    def add_filter(self, filter_instance: Any) -> None:
        """フィルタを追加。.

        Args:
            filter_instance: 追加するフィルタインスタンス
        """
        self.filter_chain.add_filter(filter_instance)

    def remove_filter(self, filter_type: Any) -> bool:
        """フィルタを削除。.

        Args:
            filter_type: 削除するフィルタの型

        Returns:
            削除に成功した場合True
        """
        return self.filter_chain.remove_filter(filter_type)

    def set_splitter(self, splitter: Any) -> None:
        """句分割器を設定。.

        Args:
            splitter: 新しい句分割器
        """
        self.splitter = splitter

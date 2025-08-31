"""品詞考慮句分割器の実装。."""

from __future__ import annotations

from typing import Any

from .base import BaseSplitter, SplitResult, TokenList
from .scorer import BoundaryScorer, CompositeScorer, MoraScorer, SemanticScorer


class POSAwareSplitter(BaseSplitter):
    """品詞情報を考慮した句分割器。.

    単語の品詞情報を活用して、より自然な句境界で分割を行う。
    """

    def __init__(self, mora_weight: float = 1.0, pos_weight: float = 0.8) -> None:
        """品詞考慮分割器を初期化。.

        Args:
            mora_weight: モーラスコアの重み
            pos_weight: 品詞スコアの重み
        """
        self.mora_weight = mora_weight
        self.pos_weight = pos_weight
        self.scorer = CompositeScorer(
            [
                (MoraScorer(penalty_weight=1.0), mora_weight),
                (BoundaryScorer(), pos_weight),
            ]
        )

    def split(
        self,
        tokens: TokenList,
        target_pattern: tuple[int, int, int],
    ) -> SplitResult | None:
        """品詞情報を考慮して分割。.

        Args:
            tokens: 分割対象のトークンリスト
            target_pattern: 目標モーラパターン

        Returns:
            最適な分割結果、適切な分割がない場合はNone
        """
        if not self.can_split(tokens):
            return None

        best_split = None
        best_score = float("-inf")

        for i in range(1, len(tokens)):
            for j in range(i + 1, len(tokens)):
                upper_tokens = tokens[:i]
                middle_tokens = tokens[i:j]
                lower_tokens = tokens[j:]

                # 空の句は除外
                if not upper_tokens or not middle_tokens or not lower_tokens:
                    continue

                # 句開始の妥当性チェック
                if not self._is_valid_phrase_start(middle_tokens[0]):
                    continue
                if not self._is_valid_phrase_start(lower_tokens[0]):
                    continue

                # スコア計算
                score = self.scorer.calculate_score(
                    upper_tokens, middle_tokens, lower_tokens, target_pattern
                )

                if score > best_score:
                    best_score = score
                    best_split = SplitResult(
                        upper_tokens=upper_tokens,
                        middle_tokens=middle_tokens,
                        lower_tokens=lower_tokens,
                        score=score,
                        metadata={
                            "splitter": "pos_aware",
                            "mora_weight": self.mora_weight,
                            "pos_weight": self.pos_weight,
                        },
                    )

        # 最低スコア閾値をクリア
        if best_split and best_split.score > -10.0:
            return best_split

        return None

    def _is_valid_phrase_start(self, token: Any) -> bool:
        """句の開始として適切な品詞かどうかを判定。.

        Args:
            token: 句の最初のトークン

        Returns:
            適切な開始品詞の場合True
        """
        # 句の開始として明らかに不適切な品詞のみを除外
        invalid_starts = {
            "接続助詞",  # ので、から、けれど等
            "接尾辞",  # ども、ら、たち等
            "補助記号",  # 句読点等
        }

        return token.pos not in invalid_starts


class SemanticAwareSplitter(BaseSplitter):
    """意味的まとまりを考慮した句分割器。.

    品詞の組み合わせや文の構造を考慮してより自然な分割を行う。
    """

    def __init__(
        self,
        mora_weight: float = 1.0,
        boundary_weight: float = 0.5,
        semantic_weight: float = 0.8,
    ) -> None:
        """意味考慮分割器を初期化。.

        Args:
            mora_weight: モーラスコアの重み
            boundary_weight: 境界スコアの重み
            semantic_weight: 意味スコアの重み
        """
        self.scorer = CompositeScorer(
            [
                (MoraScorer(penalty_weight=1.0), mora_weight),
                (BoundaryScorer(), boundary_weight),
                (SemanticScorer(), semantic_weight),
            ]
        )

    def split(
        self,
        tokens: TokenList,
        target_pattern: tuple[int, int, int],
    ) -> SplitResult | None:
        """意味的まとまりを考慮して分割。.

        Args:
            tokens: 分割対象のトークンリスト
            target_pattern: 目標モーラパターン

        Returns:
            最適な分割結果
        """
        if not self.can_split(tokens):
            return None

        best_split = None
        best_score = float("-inf")

        for i in range(1, len(tokens)):
            for j in range(i + 1, len(tokens)):
                upper_tokens = tokens[:i]
                middle_tokens = tokens[i:j]
                lower_tokens = tokens[j:]

                # 空の句は除外
                if not upper_tokens or not middle_tokens or not lower_tokens:
                    continue

                # 意味的妥当性の事前チェック
                if not self._is_semantically_valid(upper_tokens, middle_tokens, lower_tokens):
                    continue

                # スコア計算
                score = self.scorer.calculate_score(
                    upper_tokens, middle_tokens, lower_tokens, target_pattern
                )

                if score > best_score:
                    best_score = score
                    best_split = SplitResult(
                        upper_tokens=upper_tokens,
                        middle_tokens=middle_tokens,
                        lower_tokens=lower_tokens,
                        score=score,
                        metadata={"splitter": "semantic_aware"},
                    )

        return best_split

    def _is_semantically_valid(
        self,
        upper_tokens: TokenList,
        middle_tokens: TokenList,
        lower_tokens: TokenList,
    ) -> bool:
        """意味的に妥当な分割かチェック。.

        Args:
            upper_tokens: 上句のトークン
            middle_tokens: 中句のトークン
            lower_tokens: 下句のトークン

        Returns:
            意味的に妥当な場合True
        """
        # すべての句が助詞・助動詞で始まる場合は除外
        problem_starts = {"助詞", "助動詞"}

        if (
            middle_tokens
            and middle_tokens[0].pos in problem_starts
            and lower_tokens
            and lower_tokens[0].pos in problem_starts
        ):
            return False

        # 極端に短い句（1トークンのみ）が複数ある場合は除外
        short_phrases = sum(
            1 for phrase in [upper_tokens, middle_tokens, lower_tokens] if len(phrase) == 1
        )
        if short_phrases >= 2:
            return False

        return True


class AdaptivePOSSplitter(BaseSplitter):
    """適応的品詞分割器。.

    複数の品詞考慮戦略を組み合わせて最適な分割を選択する。
    """

    def __init__(self) -> None:
        """適応的品詞分割器を初期化。."""
        self.splitters = [
            POSAwareSplitter(mora_weight=1.2, pos_weight=0.8),
            SemanticAwareSplitter(mora_weight=1.0, boundary_weight=0.6, semantic_weight=1.0),
            # より保守的な設定
            POSAwareSplitter(mora_weight=2.0, pos_weight=0.5),
        ]

    def split(
        self,
        tokens: TokenList,
        target_pattern: tuple[int, int, int],
    ) -> SplitResult | None:
        """複数戦略で分割を試行し、最高スコアを選択。.

        Args:
            tokens: 分割対象のトークンリスト
            target_pattern: 目標モーラパターン

        Returns:
            最適な分割結果
        """
        best_result = None
        best_score = float("-inf")

        for splitter in self.splitters:
            result = splitter.split(tokens, target_pattern)
            if result and result.score > best_score:
                best_score = result.score
                best_result = result

        if best_result:
            # メタデータを含む新しい結果を作成
            updated_metadata = best_result.metadata or {}
            updated_metadata["splitter"] = "adaptive_pos"

            from .base import SplitResult

            best_result = SplitResult(
                upper_tokens=best_result.upper_tokens,
                middle_tokens=best_result.middle_tokens,
                lower_tokens=best_result.lower_tokens,
                score=best_result.score,
                metadata=updated_metadata,
            )

        return best_result

"""モーラベース句分割器の実装。."""

from __future__ import annotations

from .base import BaseSplitter, SplitResult, TokenList
from .scorer import CompositeScorer, MoraScorer


class MoraBasedSplitter(BaseSplitter):
    """モーラ数に基づく句分割器。.

    単語境界を尊重しながら、目標モーラパターンに最も近い分割を探す。
    """

    def __init__(self, tolerance: int = 4) -> None:
        """モーラベース分割器を初期化。.

        Args:
            tolerance: 総モーラ数の許容誤差
        """
        self.tolerance = tolerance
        self.scorer = CompositeScorer([(MoraScorer(penalty_weight=1.0), 1.0)])

    def split(
        self,
        tokens: TokenList,
        target_pattern: tuple[int, int, int],
    ) -> SplitResult | None:
        """モーラ数ベースでトークンを分割。.

        Args:
            tokens: 分割対象のトークンリスト
            target_pattern: 目標モーラパターン

        Returns:
            最適な分割結果、適切な分割がない場合はNone
        """
        if not self.can_split(tokens):
            return None

        # 総モーラ数の事前チェック
        total_mora = sum(token.mora_count for token in tokens)
        target_total = sum(target_pattern)

        if abs(total_mora - target_total) > self.tolerance:
            return None

        # 累積モーラ数配列を作成
        self._calculate_cumulative_mora(tokens)

        best_split = None
        best_score = float("-inf")

        # 単語境界でのみ分割を試行
        for i in range(1, len(tokens)):
            for j in range(i + 1, len(tokens)):
                upper_tokens = tokens[:i]
                middle_tokens = tokens[i:j]
                lower_tokens = tokens[j:]

                # 空の句は除外
                if not upper_tokens or not middle_tokens or not lower_tokens:
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
                        metadata={"splitter": "mora_based", "tolerance": self.tolerance},
                    )

        # スコア閾値チェック
        if best_split and best_split.score >= -self.tolerance:
            return best_split

        return None

    def _calculate_cumulative_mora(self, tokens: TokenList) -> list[int]:
        """累積モーラ数配列を計算。.

        Args:
            tokens: トークンリスト

        Returns:
            累積モーラ数のリスト
        """
        cumulative = [0]
        for token in tokens:
            cumulative.append(cumulative[-1] + token.mora_count)
        return cumulative

    def can_split(self, tokens: TokenList) -> bool:
        """分割可能かどうかをチェック。.

        Args:
            tokens: チェック対象のトークンリスト

        Returns:
            分割可能な場合True
        """
        if len(tokens) < 3:
            return False

        # モーラ数0のトークンが多すぎる場合は分割困難
        zero_mora_count = sum(1 for token in tokens if token.mora_count == 0)
        if zero_mora_count > len(tokens) // 2:
            return False

        return True


class FlexibleMoraBasedSplitter(MoraBasedSplitter):
    """より柔軟なモーラベース句分割器。.

    モーラ数の許容範囲を段階的に広げて分割を試行する。
    """

    def __init__(self, base_tolerance: int = 2, max_tolerance: int = 5) -> None:
        """柔軟モーラベース分割器を初期化。.

        Args:
            base_tolerance: 基本許容誤差
            max_tolerance: 最大許容誤差
        """
        super().__init__(tolerance=base_tolerance)
        self.base_tolerance = base_tolerance
        self.max_tolerance = max_tolerance

    def split(
        self,
        tokens: TokenList,
        target_pattern: tuple[int, int, int],
    ) -> SplitResult | None:
        """段階的に許容範囲を広げて分割を試行。.

        Args:
            tokens: 分割対象のトークンリスト
            target_pattern: 目標モーラパターン

        Returns:
            最適な分割結果
        """
        # 段階的に許容範囲を広げて試行
        for tolerance in range(self.base_tolerance, self.max_tolerance + 1):
            self.tolerance = tolerance
            result = super().split(tokens, target_pattern)
            if result:
                # メタデータを含む新しい結果を作成
                updated_metadata = result.metadata or {}
                updated_metadata["actual_tolerance"] = tolerance

                from .base import SplitResult

                return SplitResult(
                    upper_tokens=result.upper_tokens,
                    middle_tokens=result.middle_tokens,
                    lower_tokens=result.lower_tokens,
                    score=result.score,
                    metadata=updated_metadata,
                )

        return None

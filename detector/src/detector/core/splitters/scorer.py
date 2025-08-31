"""句分割のスコアリング機能。."""

from __future__ import annotations

from abc import ABC, abstractmethod

from ...models.senryu import Token

type TokenList = list[Token]


class BaseScorer(ABC):
    """スコアリング機能の基底クラス。."""

    @abstractmethod
    def calculate_score(
        self,
        upper_tokens: TokenList,
        middle_tokens: TokenList,
        lower_tokens: TokenList,
        target_pattern: tuple[int, int, int],
    ) -> float:
        """分割に対するスコアを計算。.

        Args:
            upper_tokens: 上句のトークン
            middle_tokens: 中句のトークン
            lower_tokens: 下句のトークン
            target_pattern: 目標モーラパターン

        Returns:
            スコア値（高いほど良い分割）
        """


class MoraScorer(BaseScorer):
    """モーラ数に基づくスコアリング。."""

    def __init__(self, penalty_weight: float = 1.0) -> None:
        """モーラスコアラーを初期化。.

        Args:
            penalty_weight: ペナルティの重み
        """
        self.penalty_weight = penalty_weight

    def calculate_score(
        self,
        upper_tokens: TokenList,
        middle_tokens: TokenList,
        lower_tokens: TokenList,
        target_pattern: tuple[int, int, int],
    ) -> float:
        """モーラ数の差異に基づくスコア計算。.

        Args:
            upper_tokens: 上句のトークン
            middle_tokens: 中句のトークン
            lower_tokens: 下句のトークン
            target_pattern: 目標モーラパターン

        Returns:
            モーラスコア（差異が小さいほど高い）
        """
        upper_target, middle_target, lower_target = target_pattern

        upper_mora = sum(token.mora_count for token in upper_tokens)
        middle_mora = sum(token.mora_count for token in middle_tokens)
        lower_mora = sum(token.mora_count for token in lower_tokens)

        # 目標パターンとの差異を計算（小さいほど良い）
        mora_penalty = (
            abs(upper_mora - upper_target)
            + abs(middle_mora - middle_target)
            + abs(lower_mora - lower_target)
        )

        return -mora_penalty * self.penalty_weight


class BoundaryScorer(BaseScorer):
    """品詞境界に基づくスコアリング。."""

    def __init__(self) -> None:
        """境界スコアラーを初期化。."""
        self.pos_bonuses = {
            "助詞": 1.0,
            "助動詞": 0.7,
        }
        self.transition_bonuses = {
            ("名詞", "動詞"): 0.5,
            ("名詞", "形容詞"): 0.5,
        }

    def calculate_score(
        self,
        upper_tokens: TokenList,
        middle_tokens: TokenList,
        lower_tokens: TokenList,
        target_pattern: tuple[int, int, int],
    ) -> float:
        """品詞境界に基づくスコア計算。.

        Args:
            upper_tokens: 上句のトークン
            middle_tokens: 中句のトークン
            lower_tokens: 下句のトークン
            target_pattern: 目標モーラパターン

        Returns:
            境界スコア
        """
        score = 0.0

        # 句の終端での品詞ボーナス
        if upper_tokens and upper_tokens[-1].pos in self.pos_bonuses:
            score += self.pos_bonuses[upper_tokens[-1].pos]
        if middle_tokens and middle_tokens[-1].pos in self.pos_bonuses:
            score += self.pos_bonuses[middle_tokens[-1].pos]

        # 句の境界での品詞遷移ボーナス
        if upper_tokens and middle_tokens:
            transition = (upper_tokens[-1].pos, middle_tokens[0].pos)
            if transition in self.transition_bonuses:
                score += self.transition_bonuses[transition]

        if middle_tokens and lower_tokens:
            transition = (middle_tokens[-1].pos, lower_tokens[0].pos)
            if transition in self.transition_bonuses:
                score += self.transition_bonuses[transition]

        return score


class SemanticScorer(BaseScorer):
    """意味的まとまりに基づくスコアリング。."""

    def __init__(self) -> None:
        """意味的スコアラーを初期化。."""
        self.start_penalties = {
            "助詞": -1.5,
            "助動詞": -1.5,
        }
        self.start_bonuses = {
            "名詞": 0.3,
            "動詞": 0.3,
            "形容詞": 0.3,
            "副詞": 0.3,
        }
        self.end_bonuses = {
            "助詞": 0.8,
            "感動詞": 0.8,
            "動詞": 0.6,
            "助動詞": 0.6,
            "名詞": 0.5,
        }

    def calculate_score(
        self,
        upper_tokens: TokenList,
        middle_tokens: TokenList,
        lower_tokens: TokenList,
        target_pattern: tuple[int, int, int],
    ) -> float:
        """意味的まとまりに基づくスコア計算。.

        Args:
            upper_tokens: 上句のトークン
            middle_tokens: 中句のトークン
            lower_tokens: 下句のトークン
            target_pattern: 目標モーラパターン

        Returns:
            意味的スコア
        """
        score = 0.0

        # 句の開始品詞のペナルティ/ボーナス
        for phrase_tokens in [middle_tokens, lower_tokens]:
            if phrase_tokens:
                start_pos = phrase_tokens[0].pos
                if start_pos in self.start_penalties:
                    score += self.start_penalties[start_pos]
                elif start_pos in self.start_bonuses:
                    score += self.start_bonuses[start_pos]

        # 句の終了品詞のボーナス
        for phrase_tokens in [upper_tokens, middle_tokens, lower_tokens]:
            if phrase_tokens:
                end_pos = phrase_tokens[-1].pos
                if end_pos in self.end_bonuses:
                    score += self.end_bonuses[end_pos]

        # 修飾関係のボーナス
        all_phrases = [upper_tokens, middle_tokens, lower_tokens]
        for phrase_tokens in all_phrases:
            score += self._calculate_internal_structure_bonus(phrase_tokens)

        return score

    def _calculate_internal_structure_bonus(self, tokens: TokenList) -> float:
        """句内の構造に基づくボーナス計算。.

        Args:
            tokens: 句のトークンリスト

        Returns:
            構造ボーナス
        """
        bonus = 0.0

        for i in range(len(tokens) - 1):
            current_pos = tokens[i].pos
            next_pos = tokens[i + 1].pos

            # 名詞+助詞の組み合わせ
            if current_pos == "名詞" and next_pos == "助詞":
                bonus += 0.2

            # 形容詞/形容動詞 + 名詞の組み合わせ
            if current_pos in ["形容詞", "形容動詞"] and next_pos == "名詞":
                bonus += 0.3

        return bonus


class CompositeScorer(BaseScorer):
    """複数のスコアラーを組み合わせるコンポジットスコアラー。."""

    def __init__(self, scorers: list[tuple[BaseScorer, float]]) -> None:
        """コンポジットスコアラーを初期化。.

        Args:
            scorers: (スコアラー, 重み)のタプルのリスト
        """
        self.scorers = scorers

    def calculate_score(
        self,
        upper_tokens: TokenList,
        middle_tokens: TokenList,
        lower_tokens: TokenList,
        target_pattern: tuple[int, int, int],
    ) -> float:
        """すべてのスコアラーの重み付き合計を計算。.

        Args:
            upper_tokens: 上句のトークン
            middle_tokens: 中句のトークン
            lower_tokens: 下句のトークン
            target_pattern: 目標モーラパターン

        Returns:
            合成スコア
        """
        total_score = 0.0

        for scorer, weight in self.scorers:
            score = scorer.calculate_score(
                upper_tokens, middle_tokens, lower_tokens, target_pattern
            )
            total_score += score * weight

        return total_score

    def add_scorer(self, scorer: BaseScorer, weight: float) -> None:
        """スコアラーを追加。.

        Args:
            scorer: 追加するスコアラー
            weight: 重み
        """
        self.scorers.append((scorer, weight))

    def remove_scorer(self, scorer_type: type[BaseScorer]) -> bool:
        """指定タイプのスコアラーを削除。.

        Args:
            scorer_type: 削除するスコアラーの型

        Returns:
            削除に成功した場合True
        """
        for i, (scorer, _) in enumerate(self.scorers):
            if isinstance(scorer, scorer_type):
                del self.scorers[i]
                return True
        return False

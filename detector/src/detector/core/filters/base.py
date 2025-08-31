"""フィルタリング層のベースクラス。."""

from __future__ import annotations

from abc import ABC, abstractmethod

from ...models.senryu import Token

# 型エイリアス
type TokenList = list[Token]
type CandidateTokens = list[Token]


class BaseFilter(ABC):
    """すべてのフィルタの基底クラス。."""

    @abstractmethod
    def apply(self, tokens: TokenList, **kwargs: object) -> bool:
        """フィルタを適用し、トークンリストが条件を満たすかどうかを判定。.

        Args:
            tokens: フィルタリング対象のトークンリスト
            **kwargs: フィルタ固有の追加引数

        Returns:
            トークンリストが条件を満たす場合True、除外すべき場合False
        """

    def __and__(self, other: BaseFilter) -> CompositeFilter:
        """論理AND操作でフィルタを組み合わせ。."""
        return CompositeFilter([self, other], mode="and")

    def __or__(self, other: BaseFilter) -> CompositeFilter:
        """論理OR操作でフィルタを組み合わせ。."""
        return CompositeFilter([self, other], mode="or")


class CandidateFilter(BaseFilter):
    """候補トークンリスト用のフィルタベースクラス。.

    川柳候補として検討するトークンリストをフィルタリングする。
    """


class CompositeFilter(BaseFilter):
    """複数のフィルタを組み合わせるコンポジットフィルタ。."""

    def __init__(self, filters: list[BaseFilter], mode: str = "and") -> None:
        """コンポジットフィルタを初期化。.

        Args:
            filters: 組み合わせるフィルタのリスト
            mode: 組み合わせ方式 ("and" または "or")
        """
        if mode not in ("and", "or"):
            raise ValueError("mode must be 'and' or 'or'")
        self.filters = filters
        self.mode = mode

    def apply(self, tokens: TokenList, **kwargs: object) -> bool:
        """すべてのフィルタを指定された方式で適用。.

        Args:
            tokens: フィルタリング対象のトークンリスト
            **kwargs: フィルタ固有の追加引数

        Returns:
            組み合わせ結果
        """
        if not self.filters:
            return True

        if self.mode == "and":
            return all(filter_.apply(tokens, **kwargs) for filter_ in self.filters)
        else:  # or
            return any(filter_.apply(tokens, **kwargs) for filter_ in self.filters)

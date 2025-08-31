"""フィルタチェーンの実装。."""

from __future__ import annotations

from collections.abc import Iterator

from .base import BaseFilter, TokenList


class FilterChain:
    """フィルタを順番に適用するチェーンクラス。.

    複数のフィルタを組み合わせて、川柳候補をフィルタリングする。
    """

    def __init__(self, filters: list[BaseFilter] | None = None) -> None:
        """フィルタチェーンを初期化。.

        Args:
            filters: 適用するフィルタのリスト
        """
        self.filters = filters or []

    def add_filter(self, filter_: BaseFilter) -> None:
        """フィルタを追加。.

        Args:
            filter_: 追加するフィルタ
        """
        self.filters.append(filter_)

    def remove_filter(self, filter_type: type[BaseFilter]) -> bool:
        """指定されたタイプのフィルタを削除。.

        Args:
            filter_type: 削除するフィルタの型

        Returns:
            フィルタが見つかって削除された場合True
        """
        for i, filter_ in enumerate(self.filters):
            if isinstance(filter_, filter_type):
                del self.filters[i]
                return True
        return False

    def apply(self, token_lists: list[TokenList]) -> list[TokenList]:
        """すべてのトークンリストにフィルタチェーンを適用。.

        Args:
            token_lists: フィルタリング対象のトークンリストのリスト

        Returns:
            フィルタを通過したトークンリストのリスト
        """
        filtered_lists = []
        for tokens in token_lists:
            if self._should_pass(tokens):
                filtered_lists.append(tokens)
        return filtered_lists

    def filter_candidates(self, candidates_iter: Iterator[TokenList]) -> Iterator[TokenList]:
        """候補の反復子をフィルタリング（メモリ効率版）。.

        Args:
            candidates_iter: 候補トークンリストの反復子

        Yields:
            フィルタを通過したトークンリスト
        """
        for tokens in candidates_iter:
            if self._should_pass(tokens):
                yield tokens

    def _should_pass(self, tokens: TokenList) -> bool:
        """トークンリストがすべてのフィルタを通過するかチェック。.

        Args:
            tokens: チェックするトークンリスト

        Returns:
            すべてのフィルタを通過する場合True
        """
        for filter_ in self.filters:
            if not filter_.apply(tokens):
                return False
        return True

    def __len__(self) -> int:
        """フィルタチェーンの長さを返す。."""
        return len(self.filters)

    def __bool__(self) -> bool:
        """フィルタが存在するかどうかを返す。."""
        return bool(self.filters)

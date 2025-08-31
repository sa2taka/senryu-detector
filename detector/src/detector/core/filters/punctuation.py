"""句読点境界フィルタの実装。."""

from __future__ import annotations

from .base import CandidateFilter, TokenList


class PunctuationBoundaryFilter(CandidateFilter):
    """句読点などの文境界記号を含むトークンリストを除外するフィルタ。.

    川柳は通常単一の文として構成されるため、句点や感嘆符などの
    文境界記号をまたいだ候補は除外する。
    """

    def __init__(self, boundary_marks: set[str] | None = None) -> None:
        """句読点境界フィルタを初期化。.

        Args:
            boundary_marks: 境界記号として扱う文字のセット
        """
        self.boundary_marks = boundary_marks or {"。", "！", "？", "!", "?"}

    def apply(self, tokens: TokenList, **kwargs: object) -> bool:
        """トークンリストに文境界記号が含まれていないかチェック。.

        Args:
            tokens: チェックするトークンリスト
            **kwargs: 未使用

        Returns:
            文境界記号が含まれていない場合True
        """
        for token in tokens:
            if token.surface in self.boundary_marks:
                return False
        return True

    def add_boundary_mark(self, mark: str) -> None:
        """境界記号を追加。.

        Args:
            mark: 追加する境界記号
        """
        self.boundary_marks.add(mark)

    def remove_boundary_mark(self, mark: str) -> bool:
        """境界記号を削除。.

        Args:
            mark: 削除する境界記号

        Returns:
            削除に成功した場合True
        """
        if mark in self.boundary_marks:
            self.boundary_marks.remove(mark)
            return True
        return False


class SymbolFilter(CandidateFilter):
    """特定の記号を含むトークンリストをフィルタリング。.

    補助記号や特殊文字を含む候補を処理するためのフィルタ。
    """

    def __init__(
        self,
        allowed_symbols: set[str] | None = None,
        exclude_pos: set[str] | None = None,
    ) -> None:
        """記号フィルタを初期化。.

        Args:
            allowed_symbols: 許可する記号のセット
            exclude_pos: 除外する品詞のセット
        """
        self.allowed_symbols = allowed_symbols or set()
        self.exclude_pos = exclude_pos or {"補助記号", "空白"}

    def apply(self, tokens: TokenList, **kwargs: object) -> bool:
        """記号に関するフィルタリングルールを適用。.

        Args:
            tokens: チェックするトークンリスト
            **kwargs: 未使用

        Returns:
            フィルタを通過する場合True
        """
        for token in tokens:
            # 除外品詞のトークンがある場合
            if token.pos in self.exclude_pos:
                # 許可記号でない場合は除外
                if token.surface not in self.allowed_symbols:
                    return False
        return True

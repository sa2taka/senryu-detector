"""日本語文字フィルタの実装。."""

from __future__ import annotations

from .base import CandidateFilter, TokenList


class JapaneseCharacterFilter(CandidateFilter):
    """日本語文字を含むトークンリストのみを通すフィルタ。.

    川柳検知の対象として、日本語文字（ひらがな、カタカナ、漢字）を
    含むトークンリストのみを許可する。
    """

    def apply(self, tokens: TokenList, **kwargs: object) -> bool:
        """トークンリストが日本語文字を含むかチェック。.

        Args:
            tokens: チェックするトークンリスト
            **kwargs: 未使用

        Returns:
            日本語文字を含む場合True
        """
        if not tokens:
            return False

        # 全トークンの表層形を結合して日本語文字をチェック
        combined_text = "".join(token.surface for token in tokens)
        return self._contains_japanese(combined_text)

    def _contains_japanese(self, text: str) -> bool:
        """テキストが日本語文字を含むかどうかをチェック。.

        Args:
            text: チェックするテキスト

        Returns:
            日本語文字を含む場合True
        """
        for char in text:
            # ひらがな、カタカナ、CJK統合漢字を含む場合は日本語とみなす
            if (
                "\u3040" <= char <= "\u309f"  # ひらがな
                or "\u30a0" <= char <= "\u30ff"  # カタカナ
                or "\u4e00" <= char <= "\u9fff"  # CJK統合漢字
                or "\u3400" <= char <= "\u4dbf"  # CJK拡張A
            ):
                return True
        return False


class MinimumTokenCountFilter(CandidateFilter):
    """最小トークン数フィルタ。.

    指定された最小トークン数を満たすリストのみを通す。
    """

    def __init__(self, min_count: int = 3) -> None:
        """最小トークン数フィルタを初期化。.

        Args:
            min_count: 最小トークン数（デフォルト: 3）
        """
        self.min_count = min_count

    def apply(self, tokens: TokenList, **kwargs: object) -> bool:
        """トークンリストが最小トークン数を満たすかチェック。.

        Args:
            tokens: チェックするトークンリスト
            **kwargs: 未使用

        Returns:
            最小トークン数を満たす場合True
        """
        return len(tokens) >= self.min_count

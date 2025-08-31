"""未知語フィルタの実装。."""

from __future__ import annotations

from typing import Any

from .base import CandidateFilter, TokenList


class UnknownWordFilter(CandidateFilter):
    """未知語を含むトークンリストを除外するフィルタ。.

    形態素解析で適切に処理されなかった未知語を含む候補を除外し、
    検知精度を向上させる。
    """

    def __init__(
        self,
        strict: bool = True,
        allowed_pos: set[str] | None = None,
    ) -> None:
        """未知語フィルタを初期化。.

        Args:
            strict: 厳密モード（デフォルト: True）
            allowed_pos: 未知語として扱わない品詞のセット
        """
        self.strict = strict
        self.allowed_pos = allowed_pos or {"補助記号", "空白"}

    def apply(self, tokens: TokenList, **kwargs: object) -> bool:
        """トークンリストに未知語が含まれていないかチェック。.

        Args:
            tokens: チェックするトークンリスト
            **kwargs: 未使用

        Returns:
            未知語が含まれていない場合True
        """
        for token in tokens:
            if self._is_unknown_word(token):
                return False
        return True

    def _is_unknown_word(self, token: Any) -> bool:
        """トークンが未知語かどうかを判定。.

        Args:
            token: チェックするトークン

        Returns:
            未知語の場合True
        """
        # 許可品詞の場合は未知語扱いしない
        if token.pos in self.allowed_pos:
            return False

        # モーラ数が0で、読みが表層形と同じ場合は未知語とみなす
        if token.mora_count == 0 and token.reading == token.surface:
            return True

        # 読みが英数字のままの場合も未知語とみなす
        if token.reading and self._contains_ascii_alphanumeric(token.reading):
            return True

        return False

    def _contains_ascii_alphanumeric(self, text: str) -> bool:
        """テキストにASCII英数字が含まれているかチェック。.

        Args:
            text: チェックするテキスト

        Returns:
            ASCII英数字が含まれている場合True
        """
        return any(c.isalnum() and ord(c) < 128 for c in text)


class MoraCountFilter(CandidateFilter):
    """モーラ数に基づくフィルタ。.

    総モーラ数が川柳として適切な範囲にあるトークンリストのみを通す。
    """

    def __init__(
        self,
        min_mora: int = 14,  # 5-7-5 - 3 = 14
        max_mora: int = 20,  # 5-8-5 + 3 = 21
        tolerance: int = 3,
    ) -> None:
        """モーラ数フィルタを初期化。.

        Args:
            min_mora: 最小モーラ数
            max_mora: 最大モーラ数
            tolerance: 許容誤差
        """
        self.min_mora = min_mora - tolerance
        self.max_mora = max_mora + tolerance

    def apply(self, tokens: TokenList, **kwargs: object) -> bool:
        """トークンリストの総モーラ数が範囲内かチェック。.

        Args:
            tokens: チェックするトークンリスト
            **kwargs: 未使用

        Returns:
            総モーラ数が範囲内の場合True
        """
        total_mora = sum(token.mora_count for token in tokens)
        return self.min_mora <= total_mora <= self.max_mora

"""促音（っ）終了に関するフィルター。."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ...models.senryu import Token
from .base import CandidateFilter

if TYPE_CHECKING:
    from ..splitters.base import SplitResult

type TokenList = list[Token]


class SokuonEndingFilter(CandidateFilter):
    """句が「っ」で終わることを防ぐフィルター。.

    川柳の各句（上句・中句・下句）が促音「っ」で終わらないようにチェックする。
    ただし、「っ」の後に記号（。！？など）が続く場合は問題ないと判断する。
    """

    def __init__(self) -> None:
        """促音終了フィルターを初期化。."""
        # 句末に来ても問題ない記号類
        self.allowed_endings = {
            "。",
            "！",
            "？",
            "!",
            "?",
            ".",
            "…",
            "・",
            "」",
            "』",
            "）",
            "〉",
            "》",
            "、",
            ",",
            "；",
            ";",
            "：",
        }

    def apply(self, tokens: TokenList, **kwargs: object) -> bool:
        """フィルターを適用。.

        Args:
            tokens: フィルター対象のトークンリスト
            **kwargs: 追加パラメータ（split_result等）

        Returns:
            フィルターを通過する場合True
        """
        # 分割結果があることを確認
        split_result: SplitResult | None = kwargs.get("split_result")  # type: ignore[assignment]
        if not split_result:
            return True

        # 各句の最後が「っ」で終わっていないかチェック
        phrases = [split_result.upper_tokens, split_result.middle_tokens, split_result.lower_tokens]

        for phrase_tokens in phrases:
            if not phrase_tokens:
                continue

            if self._phrase_ends_with_sokuon(phrase_tokens):
                return False

        return True

    def _phrase_ends_with_sokuon(self, phrase_tokens: TokenList) -> bool:
        """句が促音で終わっているかチェック。.

        Args:
            phrase_tokens: 句のトークンリスト

        Returns:
            促音で終わっている場合True
        """
        if not phrase_tokens:
            return False

        # 句の最後のトークンを取得
        last_token = phrase_tokens[-1]

        # 表層形が「っ」で終わる場合
        if last_token.surface.endswith("っ"):
            # 次に記号が続く場合は許可（全体のトークンリストから判定）
            return not self._has_symbol_after_sokuon(phrase_tokens)

        return False

    def _has_symbol_after_sokuon(self, phrase_tokens: TokenList) -> bool:
        """「っ」の後に記号が続いているかチェック。.

        Args:
            phrase_tokens: 句のトークンリスト

        Returns:
            記号が続いている場合True
        """
        last_token = phrase_tokens[-1]

        # トークンが「っ」以外の文字も含む場合（例：「です。」「った！」）
        if len(last_token.surface) > 1 and last_token.surface.endswith("っ"):
            return False

        # 表層形全体が「っ」の場合、読みや品詞から判定
        # 記号的なトークンの場合は許可
        if any(symbol in last_token.surface for symbol in self.allowed_endings):
            return True

        # 補助記号の品詞の場合は許可
        if last_token.pos in ["補助記号", "記号", "句読点"]:
            return True

        return False

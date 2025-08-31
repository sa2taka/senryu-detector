"""句分割層のベースクラス。."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from ...models.senryu import Token

type TokenList = list[Token]
type SplitTuple = tuple[TokenList, TokenList, TokenList]


@dataclass(frozen=True)
class SplitResult:
    """句分割の結果を表すデータクラス。."""

    upper_tokens: TokenList
    middle_tokens: TokenList
    lower_tokens: TokenList
    score: float
    metadata: dict[str, object] | None = None

    @property
    def mora_pattern(self) -> tuple[int, int, int]:
        """モーラパターンを取得。."""
        return (
            sum(token.mora_count for token in self.upper_tokens),
            sum(token.mora_count for token in self.middle_tokens),
            sum(token.mora_count for token in self.lower_tokens),
        )

    @property
    def total_mora(self) -> int:
        """総モーラ数を取得。."""
        return sum(self.mora_pattern)

    def to_tuple(self) -> SplitTuple:
        """タプル形式で分割結果を返す。."""
        return (self.upper_tokens, self.middle_tokens, self.lower_tokens)


class BaseSplitter(ABC):
    """句分割器の基底クラス。.

    トークンリストを川柳の3句（上句・中句・下句）に分割する。
    """

    @abstractmethod
    def split(
        self,
        tokens: TokenList,
        target_pattern: tuple[int, int, int],
    ) -> SplitResult | None:
        """トークンリストを3つの句に分割。.

        Args:
            tokens: 分割対象のトークンリスト
            target_pattern: 目標モーラパターン

        Returns:
            最適な分割結果、適切な分割がない場合はNone
        """

    def can_split(self, tokens: TokenList) -> bool:
        """分割可能かどうかを事前チェック。.

        Args:
            tokens: チェック対象のトークンリスト

        Returns:
            分割可能な場合True
        """
        return len(tokens) >= 3  # 最低限のトークン数


class CompositeSplitter(BaseSplitter):
    """複数の分割器を組み合わせるコンポジット分割器。."""

    def __init__(self, splitters: list[BaseSplitter]) -> None:
        """コンポジット分割器を初期化。.

        Args:
            splitters: 使用する分割器のリスト
        """
        self.splitters = splitters

    def split(
        self,
        tokens: TokenList,
        target_pattern: tuple[int, int, int],
    ) -> SplitResult | None:
        """すべての分割器を試行し、最高スコアの結果を返す。.

        Args:
            tokens: 分割対象のトークンリスト
            target_pattern: 目標モーラパターン

        Returns:
            最適な分割結果
        """
        best_result = None
        best_score = float("-inf")

        for splitter in self.splitters:
            if not splitter.can_split(tokens):
                continue

            result = splitter.split(tokens, target_pattern)
            if result and result.score > best_score:
                best_score = result.score
                best_result = result

        return best_result

    def add_splitter(self, splitter: BaseSplitter) -> None:
        """分割器を追加。.

        Args:
            splitter: 追加する分割器
        """
        self.splitters.append(splitter)

    def remove_splitter(self, splitter_type: type[BaseSplitter]) -> bool:
        """指定タイプの分割器を削除。.

        Args:
            splitter_type: 削除する分割器の型

        Returns:
            削除に成功した場合True
        """
        for i, splitter in enumerate(self.splitters):
            if isinstance(splitter, splitter_type):
                del self.splitters[i]
                return True
        return False

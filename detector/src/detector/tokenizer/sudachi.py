"""形態素解析のSudachiPyラッパー。."""

from __future__ import annotations

import sudachipy

from ..core.mora import count_mora, normalize_reading
from ..models.senryu import Token


class SudachiTokenizer:
    """SudachiPy形態素解析器のラッパークラス。."""

    def __init__(self, mode: str = "C") -> None:
        """トークナイザーを初期化。.

        Args:
            mode: Sudachi分割モード。'A'(最短), 'B'(中間), 'C'(最長)
        """
        self._tokenizer: sudachipy.Tokenizer | None = None
        self._mode = self._get_split_mode(mode)

    def _get_split_mode(self, mode: str) -> sudachipy.SplitMode:
        """モード文字列をSplitMode列挙型に変換。."""
        mode_map = {
            "A": sudachipy.SplitMode.A,
            "B": sudachipy.SplitMode.B,
            "C": sudachipy.SplitMode.C,
        }

        if mode not in mode_map:
            raise ValueError(f"Invalid mode: {mode}. Must be one of 'A', 'B', 'C'")

        return mode_map[mode]

    @property
    def tokenizer(self) -> sudachipy.Tokenizer:
        """トークナイザーインスタンスを取得または作成。."""
        if self._tokenizer is None:
            try:
                # sudachidict-fullを使用してDictionaryを作成
                dictionary = sudachipy.Dictionary(dict_type="full")
                self._tokenizer = dictionary.create()
            except Exception:
                try:
                    # フォールバック: デフォルト辞書を使用（通常はfullが使われる）
                    dictionary = sudachipy.Dictionary()
                    self._tokenizer = dictionary.create()
                except Exception as e:
                    raise RuntimeError(f"SudachiPyの初期化に失敗しました: {e}") from e
        return self._tokenizer

    def tokenize(self, text: str) -> list[Token]:
        """テキストを形態素解析トークンに分割。.

        Args:
            text: 分割する日本語テキスト

        Returns:
            表層形、読み、モーラ数、品詞情報を含むTokenオブジェクトのリスト
        """
        if not text.strip():
            return []

        tokens = []
        morphemes = self.tokenizer.tokenize(text, self._mode)

        for morpheme in morphemes:
            surface = morpheme.surface()
            # 読み情報を取得（フィールド7が読み）
            reading_features = morpheme.reading_form()

            # カタカナの読みをひらがなに正規化
            normalized_reading = normalize_reading(reading_features)

            # モーラ数を計算
            mora_count = count_mora(normalized_reading)

            # 品詞情報を取得
            pos_tags = morpheme.part_of_speech()
            pos = pos_tags[0] if pos_tags else "Unknown"

            # 記号（補助記号、空白）の場合は読みを空文字列、モーラ数を0にする
            if pos in ["補助記号", "空白"]:
                normalized_reading = ""
                mora_count = 0

            tokens.append(
                Token(
                    surface=surface,
                    reading=normalized_reading,
                    mora_count=mora_count,
                    pos=pos,
                )
            )

        return tokens

    def get_reading(self, text: str) -> str:
        """テキスト全体の読みを取得。.

        Args:
            text: 日本語テキスト

        Returns:
            ひらがなでの読み
        """
        tokens = self.tokenize(text)
        return "".join(token.reading for token in tokens)

    def get_mora_count(self, text: str) -> int:
        """テキストの総モーラ数を取得。.

        Args:
            text: 日本語テキスト

        Returns:
            総モーラ数
        """
        tokens = self.tokenize(text)
        return sum(token.mora_count for token in tokens)

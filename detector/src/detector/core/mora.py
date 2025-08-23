"""日本語テキストのモーラ数えロジック。."""

from __future__ import annotations

import re
from typing import Final

# 拗音（ゃゅょ等）- モーラとしてカウントしない
YOUON_PATTERN: Final[re.Pattern[str]] = re.compile(r"[ゃゅょャュョ]")

# 促音（っ）- モーラとしてカウントする
SOKUON_PATTERN: Final[re.Pattern[str]] = re.compile(r"[っッ]")

# 長音記号（ー）- モーラとしてカウントする
LONG_VOWEL_PATTERN: Final[re.Pattern[str]] = re.compile(r"ー")

# ひらがな・カタカナの基本文字
HIRAGANA_PATTERN: Final[re.Pattern[str]] = re.compile(r"[あ-ん]")
KATAKANA_PATTERN: Final[re.Pattern[str]] = re.compile(r"[ア-ン]")


def is_youon(char: str) -> bool:
    """文字がゃゅょのような拗音かどうかをチェック。.

    Args:
        char: チェックする文字

    Returns:
        拗音の場合はTrue、そうでなければFalse
    """
    return bool(YOUON_PATTERN.match(char))


def is_special_mora(char: str) -> bool:
    """文字が特殊モーラ（促音っ）かどうかをチェック。.

    Args:
        char: チェックする文字

    Returns:
        促音の場合はTrue、そうでなければFalse
    """
    return bool(SOKUON_PATTERN.match(char))


def is_long_vowel(char: str) -> bool:
    """文字が長音記号（ー）かどうかをチェック。.

    Args:
        char: チェックする文字

    Returns:
        長音記号の場合はTrue、そうでなければFalse
    """
    return bool(LONG_VOWEL_PATTERN.match(char))


def is_japanese_mora_char(char: str) -> bool:
    """文字がモーラとしてカウントできるかどうかをチェック。.

    Args:
        char: チェックする文字

    Returns:
        モーラとしてカウントできる場合はTrue
    """
    return bool(HIRAGANA_PATTERN.match(char) or KATAKANA_PATTERN.match(char) or is_long_vowel(char))


def count_mora(text: str) -> int:
    """日本語テキストのモーラ数をカウント。.

    ルール:
    - ひらがな/カタカナの基本文字は、1モーラとしてカウント
    - 拗音（ゃゅょ）はモーラとしてカウントしない
    - 促音（っ）は1モーラとしてカウント
    - 長音記号（ー）は1モーラとしてカウント

    Args:
        text: モーラ数を数える日本語テキスト

    Returns:
        テキスト内のモーラ数

    例:
        >>> count_mora("こんにちは")
        5
        >>> count_mora("きょう")  # きょ = き + ょ、しかしょはカウントしない
        2
        >>> count_mora("がっこう")  # が + っ + こ + う
        4
        >>> count_mora("コンピューター")  # コ + ン + ピ + ー + タ + ー
        6
    """
    if not text:
        return 0

    mora_count = 0
    i = 0

    while i < len(text):
        char = text[i]

        if is_japanese_mora_char(char):
            if is_youon(char):
                # 拗音は前の文字と組み合わせて1モーラ
                # ただし、前の文字がない場合や日本語文字でない場合は0モーラ
                if i == 0 or not is_japanese_mora_char(text[i - 1]) or is_youon(text[i - 1]):
                    # 独立した拗音は0モーラ（異常ケース）
                    pass
                else:
                    # 前の文字と組み合わせ済みなので、追加のカウントは不要
                    pass
            else:
                # 基本的な文字は1モーラ
                mora_count += 1

                # 次の文字が拗音の場合、組み合わせても1モーラのまま
                if i + 1 < len(text) and is_youon(text[i + 1]):
                    i += 1  # 拗音をスキップ

        i += 1

    return mora_count


def normalize_reading(reading: str) -> str:
    """一貫した処理のために読みをひらがなに正規化。.

    Args:
        reading: カタカナまたはひらがなの読み

    Returns:
        ひらがなに正規化された読み
    """
    if not reading:
        return ""

    # カタカナをひらがなに変換
    normalized = ""
    for char in reading:
        if "ア" <= char <= "ン":
            # カタカナをひらがなに変換
            hiragana_char = chr(ord(char) - ord("ア") + ord("あ"))
            normalized += hiragana_char
        else:
            normalized += char

    return normalized

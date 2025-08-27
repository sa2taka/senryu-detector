"""川柳パターン定義とマッチングロジック。."""

from __future__ import annotations

from typing import Final

from ..models.senryu import SenryuPattern, Token

# 有効な川柳パターンの定義
SENRYU_PATTERNS: Final[dict[SenryuPattern, tuple[int, int, int]]] = {
    SenryuPattern.STANDARD: (5, 7, 5),  # 標準川柳
    SenryuPattern.JIAMARI_1: (5, 8, 5),  # 字余り川柳（中句8音）
    SenryuPattern.JIAMARI_2: (6, 7, 5),  # 字余り川柳（上句6音）
    SenryuPattern.JIAMARI_3: (5, 7, 6),  # 字余り川柳（下句6音）
}


def is_valid_senryu_pattern(mora_pattern: tuple[int, int, int]) -> bool:
    """モーラパターンが有効な川柳パターンとマッチするかどうかをチェック。.

    Args:
        mora_pattern: (上句、中句、下句)のモーラ数タプル

    Returns:
        有効な川柳パターンとマッチする場合はTrue
    """
    return mora_pattern in SENRYU_PATTERNS.values()


def get_pattern_type(mora_pattern: tuple[int, int, int]) -> SenryuPattern | None:
    """指定されたモーラ数の川柳パターンタイプを取得。.

    Args:
        mora_pattern: (上句、中句、下句)のモーラ数タプル

    Returns:
        有効な場合はSenryuPattern、そうでなければNone
    """
    for pattern, pattern_mora in SENRYU_PATTERNS.items():
        if mora_pattern == pattern_mora:
            return pattern
    return None


def validate_senryu_rules(
    mora_pattern: tuple[int, int, int],
    upper_tokens: list[Token],
    middle_tokens: list[Token],
    lower_tokens: list[Token],
) -> bool:
    """川柳の厳密なルールに基づく二値判定。.

    Args:
        mora_pattern: (上句、中句、下句)のモーラ数タプル
        upper_tokens: 上句のトークンリスト
        middle_tokens: 中句のトークンリスト
        lower_tokens: 下句のトークンリスト

    Returns:
        川柳として有効な場合True、そうでなければFalse
    """
    # 1. モーラパターンの厳密チェック
    if not is_valid_senryu_pattern(mora_pattern):
        return False

    # 2. 句開始の品詞ルール（すべての句をチェック）
    if not _is_valid_phrase_start_strict(upper_tokens[0]):
        return False
    if not _is_valid_phrase_start_strict(middle_tokens[0]):
        return False
    if not _is_valid_phrase_start_strict(lower_tokens[0]):
        return False

    # 3. 最低限のトークン数チェック
    if len(upper_tokens) == 0 or len(middle_tokens) == 0 or len(lower_tokens) == 0:
        return False

    return True


def _is_valid_phrase_start_strict(token: Token) -> bool:
    """句開始として厳密に有効な品詞かチェック。.

    Args:
        token: 検査対象のトークン

    Returns:
        有効な開始品詞の場合True
    """
    # 明らかに不適切な品詞のみ禁止
    invalid_starts = {
        "助詞",  # が、を、に、で等の格助詞
        "助動詞",  # だ、である等
        "接続助詞",  # ので、から等
        "補助記号",  # 句読点等
        "接続詞",  # しかし、そして等
    }

    return token.pos not in invalid_starts


def get_target_patterns() -> list[tuple[int, int, int]]:
    """検知対象のすべてのモーラパターンリストを取得。.

    Returns:
        タプルとしての有効なモーラパターンリスト
    """
    return list(SENRYU_PATTERNS.values())


def is_standard_pattern(pattern: SenryuPattern) -> bool:
    """パターンが標準の5-7-5パターンかどうかをチェック。.

    Args:
        pattern: チェックする川柳パターン

    Returns:
        標準パターンの場合はTrue、そうでなければFalse
    """
    return pattern == SenryuPattern.STANDARD

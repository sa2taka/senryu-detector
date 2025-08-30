"""川柳検知のメインエンジン。."""

from __future__ import annotations

import re
from collections.abc import Iterator

from ..models.senryu import DetectionResult, SenryuPattern, SenryuPhrase, Token
from ..tokenizer.sudachi import SudachiTokenizer
from .patterns import (
    get_pattern_type,
    get_target_patterns,
    validate_senryu_rules,
)


class SenryuDetector:
    """日本語テキストから川柳を検知するメインエンジン。."""

    def __init__(self) -> None:
        """川柳検知器を初期化。."""
        self.tokenizer = SudachiTokenizer(mode="C")  # フレーズ境界の検出により適した最長分割を使用

    def detect(self, text: str) -> list[DetectionResult]:
        """指定されたテキストから川柳を検知。.

        Args:
            text: 分析する日本語テキスト

        Returns:
            検知された川柳のリスト
        """
        if not text.strip():
            return []

        # 日本語文字を含まない場合は早期リターン
        if not self._contains_japanese(text):
            return []

        # テキストを正規化
        normalized_text = self._normalize_text(text)

        # 形態素解析
        tokens = self.tokenizer.tokenize(normalized_text)

        if len(tokens) < 3:  # 最低限のトークン数チェック
            return []

        # 候補を検出
        candidates = list(self._find_senryu_candidates(tokens, normalized_text))

        # 有効な川柳のみを抽出し、重複を除去
        valid_candidates = [result for result in candidates if result.is_valid]

        # 開始位置が重複する川柳から最適なものを選択
        return self._remove_duplicates(valid_candidates)

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

    def _normalize_text(self, text: str) -> str:
        """一貫した処理のためのテキスト正規化。.

        Args:
            text: 入力生テキスト

        Returns:
            正規化されたテキスト
        """
        # 改行を句点に変換（区切り文字として扱う）
        normalized = re.sub(r"\n", "。", text)

        # 複数の句点を1つに統合
        normalized = re.sub(r"。+", "。", normalized)

        # 複数の空白を1つに統合
        normalized = re.sub(r"\s+", " ", normalized)

        # 前後の空白を除去
        return normalized.strip()

    def _find_senryu_candidates(
        self,
        tokens: list[Token],
        original_text: str,
    ) -> Iterator[DetectionResult]:
        """スライディングウィンドウ手法で川柳候補を探索。.

        Args:
            tokens: 形態素解析トークンリスト
            original_text: 位置追跡用の元テキスト

        Yields:
            川柳検知結果
        """
        target_patterns = get_target_patterns()

        # スライディングウィンドウでトークンの組み合わせを試行
        for start_idx in range(len(tokens)):
            for end_idx in range(
                start_idx + 3, min(len(tokens) + 1, start_idx + 20)
            ):  # 最大20トークン
                candidate_tokens = tokens[start_idx:end_idx]

                # 句点（。）をまたいだ候補を除外
                if self._contains_sentence_boundary(candidate_tokens):
                    continue

                # 未知語を含む候補を除外
                if self._contains_unknown_words(candidate_tokens):
                    continue

                # 各パターンに対してフレーズ分割を試行
                for pattern in target_patterns:
                    result = self._try_pattern_match(
                        candidate_tokens,
                        pattern,
                        original_text,
                        start_idx,
                    )

                    if result is not None:
                        yield result

    def _try_pattern_match(
        self,
        tokens: list[Token],
        target_pattern: tuple[int, int, int],
        original_text: str,
        start_token_idx: int,
    ) -> DetectionResult | None:
        """特定の川柳パターンに対してトークンをマッチング。.

        Args:
            tokens: マッチングするトークンリスト
            target_pattern: 目標モーラパターン（上句、中句、下句）
            original_text: 位置追跡用の元テキスト
            start_token_idx: 元テキスト内の開始トークンインデックス

        Returns:
            パターンがマッチした場合は検知結果、そうでなければNone
        """
        upper_target, middle_target, lower_target = target_pattern
        total_mora = sum(token.mora_count for token in tokens)
        expected_total = sum(target_pattern)

        # 総モーラ数が大きく異なる場合はスキップ
        if abs(total_mora - expected_total) > 3:
            return None

        # 最適なフレーズ分割を探索
        best_split = self._find_best_phrase_split(tokens, target_pattern)

        if best_split is None:
            return None

        upper_tokens, middle_tokens, lower_tokens = best_split

        # フレーズオブジェクトを作成
        upper_phrase = self._create_phrase(upper_tokens)
        middle_phrase = self._create_phrase(middle_tokens)
        lower_phrase = self._create_phrase(lower_tokens)

        # パターンタイプを取得
        actual_pattern = (
            upper_phrase.mora_count,
            middle_phrase.mora_count,
            lower_phrase.mora_count,
        )

        pattern_type = get_pattern_type(actual_pattern)

        if pattern_type is None:
            # 完全一致しない場合も、近いパターンなら許可
            if not self._is_close_pattern(actual_pattern, target_pattern):
                return None
            # 最も近いパターンタイプを探す
            pattern_type = self._get_closest_pattern_type(actual_pattern)

            # それでもNoneなら返さない
            if pattern_type is None:
                return None

        # 川柳ルールの厳密な検証
        is_valid = validate_senryu_rules(
            actual_pattern,
            upper_tokens,
            middle_tokens,
            lower_tokens,
        )

        # テキスト位置を計算
        start_pos, end_pos = self._calculate_text_positions(
            tokens,
            original_text,
        )

        segment_text = original_text[start_pos:end_pos]

        return DetectionResult(
            pattern=pattern_type,
            upper_phrase=upper_phrase,
            middle_phrase=middle_phrase,
            lower_phrase=lower_phrase,
            start_position=start_pos,
            end_position=end_pos,
            original_text=segment_text,
            is_valid=is_valid,
        )

    def _find_best_phrase_split(
        self,
        tokens: list[Token],
        target_pattern: tuple[int, int, int],
    ) -> tuple[list[Token], list[Token], list[Token]] | None:
        """単語境界を尊重してトークンを3つのフレーズに分割する最適な方法を探索。.

        Args:
            tokens: 分割するトークンリスト
            target_pattern: 各フレーズの目標モーラ数

        Returns:
            最適な分割（上句、中句、下句）トークンリスト、または適切な分割がない場合はNone
        """
        if len(tokens) < 3:  # 最低3つのトークンが必要
            return None

        upper_target, middle_target, lower_target = target_pattern

        # 累積モーラ数配列を作成（単語境界でのみ分割可能）
        cumulative_mora = [0]
        for token in tokens:
            cumulative_mora.append(cumulative_mora[-1] + token.mora_count)

        total_mora = cumulative_mora[-1]
        target_total = sum(target_pattern)

        # 総モーラ数が大きく異なる場合はスキップ
        if abs(total_mora - target_total) > 4:
            return None

        best_split = None
        best_score = float("inf")

        # 単語境界でのみ分割を試行
        for i in range(1, len(tokens)):  # 上句終了位置
            for j in range(i + 1, len(tokens)):  # 中句終了位置
                upper_tokens = tokens[:i]
                middle_tokens = tokens[i:j]
                lower_tokens = tokens[j:]

                # 意味論的境界チェック：句が不適切な品詞で始まっていないか確認
                # 中句と下句の開始品詞をチェック（上句は最初なのでチェック不要）
                if not self._is_valid_phrase_start(middle_tokens[0]):
                    continue
                if not self._is_valid_phrase_start(lower_tokens[0]):
                    continue

                # 各句のモーラ数計算
                upper_mora = cumulative_mora[i]
                middle_mora = cumulative_mora[j] - cumulative_mora[i]
                lower_mora = cumulative_mora[-1] - cumulative_mora[j]

                # 基本スコア: 目標パターンとの差異
                mora_score = (
                    abs(upper_mora - upper_target)
                    + abs(middle_mora - middle_target)
                    + abs(lower_mora - lower_target)
                )

                # 品詞情報を考慮したボーナス計算
                pos_bonus = self._calculate_boundary_bonus(tokens, i, j)

                # 意味的まとまりのボーナス
                semantic_bonus = self._calculate_semantic_bonus(
                    upper_tokens, middle_tokens, lower_tokens
                )

                # 最終スコア（ボーナスは減点として機能）
                final_score = mora_score - pos_bonus - semantic_bonus

                # より良いスコアの場合は更新
                if final_score < best_score:
                    best_score = final_score
                    best_split = (upper_tokens, middle_tokens, lower_tokens)

        # スコアが許容範囲内の場合のみ返す
        if best_split is not None and best_score <= 3:  # 調整された閾値
            return best_split

        return None

    def _calculate_boundary_bonus(
        self, tokens: list[Token], first_boundary: int, second_boundary: int
    ) -> float:
        """品詞情報に基づく境界位置のボーナススコアを計算。.

        Args:
            tokens: 全トークンリスト
            first_boundary: 上句と中句の境界位置
            second_boundary: 中句と下句の境界位置

        Returns:
            ボーナススコア（高いほど良い境界）
        """
        bonus = 0.0

        # 助詞での区切りに大きなボーナス
        if (
            first_boundary > 0
            and first_boundary <= len(tokens)
            and tokens[first_boundary - 1].pos == "助詞"
        ):
            bonus += 1.0
        if (
            second_boundary > 0
            and second_boundary <= len(tokens)
            and tokens[second_boundary - 1].pos == "助詞"
        ):
            bonus += 1.0

        # 助動詞での区切りにもボーナス
        if (
            first_boundary > 0
            and first_boundary <= len(tokens)
            and tokens[first_boundary - 1].pos == "助動詞"
        ):
            bonus += 0.7
        if (
            second_boundary > 0
            and second_boundary <= len(tokens)
            and tokens[second_boundary - 1].pos == "助動詞"
        ):
            bonus += 0.7

        # 名詞から動詞への境界にボーナス
        if (
            first_boundary > 0
            and first_boundary < len(tokens)
            and tokens[first_boundary - 1].pos == "名詞"
            and tokens[first_boundary].pos in ["動詞", "形容詞"]
        ):
            bonus += 0.5

        if (
            second_boundary > 0
            and second_boundary < len(tokens)
            and tokens[second_boundary - 1].pos == "名詞"
            and tokens[second_boundary].pos in ["動詞", "形容詞"]
        ):
            bonus += 0.5

        return bonus

    def _contains_sentence_boundary(self, tokens: list[Token]) -> bool:
        """トークンリストに句点などの文境界記号が含まれているかチェック。.

        Args:
            tokens: チェックするトークンリスト

        Returns:
            文境界記号が含まれている場合True
        """
        for token in tokens:
            # 句点（。）や感嘆符（！）、疑問符（？）を含む場合は除外
            if token.surface in ["。", "！", "？", "!", "?"]:
                return True
        return False

    def _contains_unknown_words(self, tokens: list[Token]) -> bool:
        """トークンリストに未知語が含まれているかチェック。.

        Args:
            tokens: チェックするトークンリスト

        Returns:
            未知語が含まれている場合True
        """
        for token in tokens:
            # モーラ数が0で、かつ読みが表層形と同じ場合は未知語とみなす
            if token.mora_count == 0 and token.reading == token.surface:
                # ただし、記号や空白は除外
                if token.pos not in ["補助記号", "空白"]:
                    return True

            # 読みが英数字のままの場合も未知語とみなす
            if token.reading and any(c.isalnum() and ord(c) < 128 for c in token.reading):
                return True

        return False

    def _is_valid_phrase_start(self, token: Token) -> bool:
        """句の開始として適切な品詞かどうかを判定。.

        Args:
            token: 句の最初のトークン

        Returns:
            適切な開始品詞の場合True
        """
        # 句の開始として明らかに不適切な品詞のみを除外
        invalid_starts = {
            "接続助詞",  # ので、から、けれど等（接続的な意味）
            "接尾辞",  # ども、ら、たち等（語尾）
            "補助記号",  # 句読点等
        }

        # 助詞・助動詞で始まる場合は大幅減点するが、完全除外はしない
        return token.pos not in invalid_starts

    def _calculate_semantic_bonus(
        self, upper_tokens: list[Token], middle_tokens: list[Token], lower_tokens: list[Token]
    ) -> float:
        """意味的なまとまりに基づくボーナススコアを計算。.

        Args:
            upper_tokens: 上句のトークン
            middle_tokens: 中句のトークン
            lower_tokens: 下句のトークン

        Returns:
            意味的まとまりのボーナススコア
        """
        bonus = 0.0

        # 句の開始に対するペナルティ/ボーナス

        # すべての句が助詞・助動詞で始まる場合は減点
        if upper_tokens and upper_tokens[0].pos in ["助詞", "助動詞"]:
            bonus -= 1.5  # 大幅減点
        if middle_tokens and middle_tokens[0].pos in ["助詞", "助動詞"]:
            bonus -= 1.5  # 大幅減点
        if lower_tokens and lower_tokens[0].pos in ["助詞", "助動詞"]:
            bonus -= 1.5  # 大幅減点

        # 良い開始品詞にボーナス
        good_starts = ["名詞", "動詞", "形容詞", "副詞"]
        if middle_tokens and middle_tokens[0].pos in good_starts:
            bonus += 0.5
        if lower_tokens and lower_tokens[0].pos in good_starts:
            bonus += 0.5

        # 各句が適切な構造を持っているかチェック

        # 1. 上句：助詞で終わる句にボーナス（「古池や」「夏草や」等）
        if upper_tokens and upper_tokens[-1].pos in ["助詞", "感動詞"]:
            bonus += 0.8

        # 2. 中句：動詞で終わる句にボーナス（「飛び込む」「散りぬる」等）
        if middle_tokens and middle_tokens[-1].pos in ["動詞", "助動詞"]:
            bonus += 0.6

        # 3. 下句：名詞で終わる句にボーナス（「水の音」「風の音」等）
        if lower_tokens and lower_tokens[-1].pos == "名詞":
            bonus += 0.5

        # 4. 各句の内部構造チェック
        # 名詞+助詞の組み合わせにボーナス
        for phrase_tokens in [upper_tokens, middle_tokens, lower_tokens]:
            for i in range(len(phrase_tokens) - 1):
                if phrase_tokens[i].pos == "名詞" and phrase_tokens[i + 1].pos == "助詞":
                    bonus += 0.2

        # 5. 修飾関係のボーナス
        # 形容詞/形容動詞 + 名詞の組み合わせ
        for phrase_tokens in [upper_tokens, middle_tokens, lower_tokens]:
            for i in range(len(phrase_tokens) - 1):
                if (
                    phrase_tokens[i].pos in ["形容詞", "形容動詞"]
                    and phrase_tokens[i + 1].pos == "名詞"
                ):
                    bonus += 0.3

        return bonus

    def _create_phrase(self, tokens: list[Token]) -> SenryuPhrase:
        """トークンからSenryuPhraseを作成。.

        Args:
            tokens: フレーズ用のトークンリスト

        Returns:
            SenryuPhraseオブジェクト
        """
        text = "".join(token.surface for token in tokens)
        reading = "".join(token.reading for token in tokens)
        mora_count = sum(token.mora_count for token in tokens)

        return SenryuPhrase(
            tokens=tokens,
            mora_count=mora_count,
            text=text,
            reading=reading,
        )

    def _is_close_pattern(
        self,
        actual: tuple[int, int, int],
        target: tuple[int, int, int],
    ) -> bool:
        """実際のパターンが目標パターンに十分近いかをチェック。.

        Args:
            actual: 実際のモーラパターン
            target: 目標モーラパターン

        Returns:
            パターンが十分近い場合はTrue
        """
        return sum(abs(a - t) for a, t in zip(actual, target, strict=False)) <= 2

    def _get_closest_pattern_type(self, pattern: tuple[int, int, int]) -> SenryuPattern | None:
        """指定されたモーラ数に最も近い有効なパターンタイプを取得。.

        Args:
            pattern: マッチさせるモーラパターン

        Returns:
            最も近いSenryuPattern
        """
        target_patterns = get_target_patterns()
        best_distance = float("inf")
        best_pattern_type = None

        for target_pattern in target_patterns:
            distance = sum(abs(p - t) for p, t in zip(pattern, target_pattern, strict=False))
            if distance < best_distance:
                best_distance = distance
                best_pattern_type = get_pattern_type(target_pattern)

        return best_pattern_type

    def _calculate_text_positions(
        self,
        tokens: list[Token],
        original_text: str,
    ) -> tuple[int, int]:
        """元テキスト内の開始位置と終了位置を計算。.

        Args:
            tokens: トークンリスト
            original_text: 元テキスト

        Returns:
            (start_pos, end_pos)のタプル
        """
        # 簡易的な実装：トークンの表層形から位置を推定
        segment_text = "".join(token.surface for token in tokens)

        start_pos = original_text.find(segment_text)
        if start_pos == -1:
            start_pos = 0

        end_pos = start_pos + len(segment_text)

        return start_pos, min(end_pos, len(original_text))

    def _remove_duplicates(self, results: list[DetectionResult]) -> list[DetectionResult]:
        """開始位置が同じ川柳から最適なものを選択して重複を除去。.

        Args:
            results: 川柳検知結果のリスト

        Returns:
            重複除去された川柳検知結果のリスト
        """
        if not results:
            return []

        # 開始位置でグループ化
        position_groups: dict[int, list[DetectionResult]] = {}
        for result in results:
            start_pos = result.start_position
            if start_pos not in position_groups:
                position_groups[start_pos] = []
            position_groups[start_pos].append(result)

        # 各グループから最適な結果を選択
        selected_results = []
        for group in position_groups.values():
            if len(group) == 1:
                selected_results.append(group[0])
            else:
                best_result = self._select_best_result(group)
                selected_results.append(best_result)

        # 開始位置でソート
        selected_results.sort(key=lambda x: x.start_position)
        return selected_results

    def _select_best_result(self, candidates: list[DetectionResult]) -> DetectionResult:
        """候補の中から最適な川柳を選択。.

        Args:
            candidates: 同じ開始位置を持つ川柳候補のリスト

        Returns:
            最適な川柳検知結果
        """
        # 5-7-5パターンを優先
        from ..models.senryu import SenryuPattern

        standard_patterns = [c for c in candidates if c.pattern == SenryuPattern.STANDARD]
        if standard_patterns:
            # 5-7-5の中で最長のテキストを選択
            return max(standard_patterns, key=lambda x: len(x.original_text))

        # 字余りパターンの中で最長のテキストを選択
        jiamari_patterns = [
            c
            for c in candidates
            if c.pattern
            in [SenryuPattern.JIAMARI_1, SenryuPattern.JIAMARI_2, SenryuPattern.JIAMARI_3]
        ]

        if jiamari_patterns:
            return max(jiamari_patterns, key=lambda x: len(x.original_text))

        # その他の場合は最長のテキストを選択
        return max(candidates, key=lambda x: len(x.original_text))

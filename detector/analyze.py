#!/usr/bin/env python3
"""形態素解析結果表示ツール。."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# プロジェクトのsrcディレクトリをパスに追加
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

try:
    from detector.core.mora import count_mora, normalize_reading
    from detector.tokenizer.sudachi import SudachiTokenizer
except ImportError as e:
    print(f"インポートエラー: {e}")
    print("src/detector/以下のモジュールが見つからない可能性があります。")
    sys.exit(1)


def analyze_text(text: str, verbose: bool = False) -> None:
    """テキストの形態素解析結果を表示する。."""
    print(f"📝 入力テキスト: {text}")
    print("=" * 80)

    # 既存のSudachiTokenizerを使用して、詳細情報も取得
    tokenizer = SudachiTokenizer(mode="C")

    try:
        # 詳細な形態素解析のためにSudachiPyを直接使用
        sudachi_tokenizer = tokenizer.tokenizer
        morphemes = sudachi_tokenizer.tokenize(text, tokenizer._mode)

        if not morphemes:
            print("❌ 形態素が見つかりませんでした")
            return

        print(f"🔍 形態素解析結果 ({len(morphemes)}形態素)")
        print("-" * 80)

        total_mora = 0

        for i, morpheme in enumerate(morphemes, 1):
            # 基本情報
            surface = morpheme.surface()
            reading_form = morpheme.reading_form()
            normalized_form = morpheme.normalized_form()
            dictionary_form = morpheme.dictionary_form()

            # 詳細な品詞情報を取得
            pos_tags = morpheme.part_of_speech()

            # 読みを正規化してモーラ数計算
            normalized_reading = normalize_reading(reading_form)
            mora_count = count_mora(normalized_reading)
            total_mora += mora_count

            print(f"{i:2d}. 表記: {surface:<12} 読み: {reading_form:<15}")
            print(f"    正規化形: {normalized_form:<10} 辞書形: {dictionary_form:<15}")

            # 品詞の詳細情報
            pos_labels = ["大分類", "中分類", "小分類", "細分類", "活用型", "活用形"]
            print("    品詞情報:")
            for _j, (label, pos_tag) in enumerate(zip(pos_labels, pos_tags[:6], strict=False)):
                if pos_tag and pos_tag != "*":
                    print(f"      {label}: {pos_tag}")

            print(f"    モーラ数: {mora_count}")

            if verbose:
                # より詳細な情報を表示
                if len(pos_tags) > 6:
                    extra_tags = [tag for tag in pos_tags[6:] if tag != "*"]
                    if extra_tags:
                        print(f"    追加品詞情報: {', '.join(extra_tags)}")

                # 全品詞情報のリスト表示
                print(f"    全品詞タグ: {pos_tags}")

                # 語彙素情報（利用可能なメソッドのみ）
                try:
                    word_id = morpheme.word_id()
                    print(f"    語彙素ID: {word_id}")
                except AttributeError:
                    print("    語彙素ID: (取得不可)")

                # その他の利用可能な情報
                try:
                    begin = morpheme.begin()
                    end = morpheme.end()
                    print(f"    位置: {begin}-{end}")
                except AttributeError:
                    pass

            print()

        print(f"📊 総モーラ数: {total_mora}")

        # 川柳パターンとの比較
        patterns = [
            ("標準川柳", [5, 7, 5]),
            ("字余り5-8-5", [5, 8, 5]),
            ("字余り6-7-5", [6, 7, 5]),
            ("字余り5-7-6", [5, 7, 6]),
        ]

        print("\n🎋 川柳パターン適合性:")
        print("-" * 40)
        for name, pattern in patterns:
            expected = sum(pattern)
            match = "✅" if total_mora == expected else "❌"
            print(f"{match} {name}: {pattern} (合計{expected}モーラ)")

    except Exception as e:
        print(f"❌ 解析エラー: {e}")
        import traceback

        if verbose:
            traceback.print_exc()
        sys.exit(1)


def main() -> None:
    """メイン関数。."""
    parser = argparse.ArgumentParser(
        description="文字列の形態素解析結果と品詞情報を表示します",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  python analyze.py "古池や蛙飛び込む水の音"
  python analyze.py "プログラミングは楽しい作業だ"
        """,
    )

    parser.add_argument("text", help="解析するテキスト")

    parser.add_argument("-v", "--verbose", action="store_true", help="詳細情報を表示")

    args = parser.parse_args()

    if not args.text.strip():
        print("❌ 空のテキストは解析できません")
        sys.exit(1)

    analyze_text(args.text, verbose=args.verbose)


if __name__ == "__main__":
    main()

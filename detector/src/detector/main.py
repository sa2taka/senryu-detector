"""検知器のメインエントリーポイント。."""

from __future__ import annotations

import sys

from .core.detector import SenryuDetector


def main(text: str | None = None) -> None:
    """川柳検知器を実行。.

    Args:
        text: 分析するテキスト。Noneの場合は標準入力から読み取るか例文を提供。
    """
    detector = SenryuDetector()

    if text is None:
        if len(sys.argv) > 1:
            # コマンドライン引数を使用
            text = " ".join(sys.argv[1:])
        else:
            # 対話モードまたは例文表示
            print("川柳検知システム - Senryu Detector")
            print("=" * 40)

            # 有名な例文でのデモ
            examples = [
                "古池や蛙飛び込む水の音",
                "夏草や兵どもが夢の跡",
                "菊の花咲きたりけり石の上",
            ]

            print("\n例文での検知結果:")
            for i, example in enumerate(examples, 1):
                print(f"\n{i}. {example}")
                results = detector.detect(example)

                if results:
                    for j, result in enumerate(results, 1):
                        print(f"   結果{j}: {result}")
                        print(f"   パターン: {result.pattern.value}")
                        print(f"   有効: {'✅' if result.is_valid else '❌'}")
                        print(f"   読み: {result.full_reading}")
                        print(
                            f"   上句: {result.upper_phrase.reading} "
                            f"({result.upper_phrase.mora_count}モーラ)"
                        )
                        print(
                            f"   中句: {result.middle_phrase.reading} "
                            f"({result.middle_phrase.mora_count}モーラ)"
                        )
                        print(
                            f"   下句: {result.lower_phrase.reading} "
                            f"({result.lower_phrase.mora_count}モーラ)"
                        )
                else:
                    print("   検知結果なし")

            print("\n" + "=" * 40)
            print("使用方法:")
            print('  コマンドライン: python -m detector.main "検知したいテキスト"')
            print("  プログラム内:   from detector import SenryuDetector")
            print("                 detector = SenryuDetector()")
            print('                 results = detector.detect("テキスト")')
            return

    # 提供されたテキストを分析
    print(f"分析テキスト: {text}")
    print("-" * 40)

    results = detector.detect(text)

    if results:
        print(f"検知された川柳パターン: {len(results)}件")

        for i, result in enumerate(results, 1):
            print(f"\n結果 {i}:")
            print(f"  テキスト: {result.original_text}")
            print(f"  パターン: {result.pattern.value}")
            print(f"  有効: {'✅' if result.is_valid else '❌'}")
            print(f"  読み: {result.full_reading}")
            print(f"  上句: {result.upper_phrase.reading} ({result.upper_phrase.mora_count}モーラ)")
            print(
                f"  中句: {result.middle_phrase.reading} ({result.middle_phrase.mora_count}モーラ)"
            )
            print(f"  下句: {result.lower_phrase.reading} ({result.lower_phrase.mora_count}モーラ)")
            print(f"  位置: {result.start_position}-{result.end_position}")
    else:
        print("川柳パターンは検知されませんでした。")


if __name__ == "__main__":
    main()

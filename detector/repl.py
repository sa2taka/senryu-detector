#!/usr/bin/env python3
"""川柳検知器のクイックテスト用スクリプト。."""

from __future__ import annotations

import sys
from pathlib import Path

# プロジェクトのsrcディレクトリをパスに追加
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

try:
    from detector import SenryuDetector
except ImportError as e:
    print(f"インポートエラー: {e}")
    print("src/detector/__init__.pyが見つからない可能性があります。")
    sys.exit(1)


def repl() -> None:
    """対話型テスト。."""
    print("🎋 川柳検知器 対話テスト")
    print("テキストを入力してください（'q'で終了）")
    print("=" * 40)

    detector = SenryuDetector()

    while True:
        try:
            text = input("\n> ").strip()

            if text.lower() in ["q", "quit", "exit"]:
                print("終了します。")
                break

            if not text:
                continue

            results = detector.detect(text)

            if results:
                print(f"✅ {len(results)}件検知:")
                for i, result in enumerate(results, 1):
                    print(
                        f"  {i}. [{result.pattern.value}] {'有効' if result.is_valid else '無効'}"
                    )
                    print(f"     {result.original_text} ({result.full_reading})")

        except KeyboardInterrupt:
            print("\n終了します。")
            break
        except Exception as e:
            print(f"エラー: {e}")


if __name__ == "__main__":
    repl()

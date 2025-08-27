#!/usr/bin/env python3
"""川柳検知APIの使用例。."""

import requests


def example_usage() -> None:
    """API使用例を実行。."""
    # APIサーバーのURL（実際に起動したサーバーを想定）
    BASE_URL = "http://localhost:8000"

    print("🎋 川柳検知API 使用例")
    print("=" * 50)
    print("注意: この例を実行するには、まずAPIサーバーを起動してください:")
    print("  uv run python -m detector.api")
    print("  または: senryu-api")
    print()

    # サーバーが起動しているかチェック
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=2)
        print("✅ APIサーバーに接続成功")
    except requests.exceptions.RequestException:
        print("❌ APIサーバーに接続できません。先にサーバーを起動してください。")
        return

    print()

    # 1. 単一テキストの検知
    print("1. 単一テキストの川柳検知")
    text = "古池や蛙飛び込む水の音"

    response = requests.post(f"{BASE_URL}/detect", json={"text": text, "only_valid": True})

    if response.status_code == 200:
        data = response.json()
        print(f"テキスト: {text}")
        print(f"検知数: {data['count']}")

        for i, result in enumerate(data["results"], 1):
            print(f"  結果{i}:")
            print(f"    パターン: {result['pattern']}")
            print(f"    読み: {result['full_reading']}")
            print(f"    有効: {'✅' if result['is_valid'] else '❌'}")
    else:
        print(f"エラー: {response.json()}")

    print()

    # 2. 一括検知
    print("2. 複数テキストの一括検知")
    texts = [
        "古池や蛙飛び込む水の音",
        "夏草や兵どもが夢の跡",
        "春風にぽっぽーという汽笛が聞こえる",
        "満員電車で本を読んでる",
    ]

    response = requests.post(f"{BASE_URL}/detect/batch", json={"texts": texts, "only_valid": False})

    if response.status_code == 200:
        data = response.json()
        print(f"総検知数: {data['total_count']}")

        for i, result in enumerate(data["results"], 1):
            print(f"  テキスト{i}: '{result['text']}'")
            print(f"    検知数: {result['count']}")

            for j, detection in enumerate(result["results"], 1):
                status = "有効" if detection["is_valid"] else "無効"
                print(f"      結果{j}: {detection['pattern']} - {status}")
    else:
        print(f"エラー: {response.json()}")

    print()

    # 3. 例文取得
    print("3. 川柳例文の取得")
    response = requests.get(f"{BASE_URL}/examples")

    if response.status_code == 200:
        data = response.json()
        print("利用可能な例文:")

        for example, description in zip(data["examples"], data["descriptions"], strict=False):
            print(f"  • {example}")
            print(f"    {description}")

    print()
    print("=" * 50)
    print("✅ APIの詳細なドキュメントは以下で確認できます:")
    print(f"  Swagger UI: {BASE_URL}/docs")
    print(f"  ReDoc: {BASE_URL}/redoc")


if __name__ == "__main__":
    example_usage()

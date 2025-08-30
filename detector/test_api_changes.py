"""API変更のテストスクリプト."""

import httpx

# ローカルAPIのURL
BASE_URL = "http://localhost:8000"


def test_detect_endpoint() -> None:
    """検知エンドポイントのテスト."""
    # テストデータ（改行を含む）
    test_text = """春風に
ポッポーという
汽笛聞く

古池や
蛙飛び込む
水の音"""

    # 1. detailsなしでリクエスト（phraseが返らない）
    print("=== Test 1: Without details option ===")
    response = httpx.post(
        f"{BASE_URL}/detect",
        json={"text": test_text, "only_valid": True},
    )
    data = response.json()
    print(f"Success: {data['success']}")
    print(f"Count: {data['count']}")

    if data["results"]:
        result = data["results"][0]
        print(f"Pattern: {result['pattern']}")
        print(f"Original text: {result['original_text']}")
        print(
            f"Has upper_phrase: {'upper_phrase' in result and result['upper_phrase'] is not None}"
        )
        print(
            f"Has middle_phrase: "
            f"{'middle_phrase' in result and result['middle_phrase'] is not None}"
        )
        print(
            f"Has lower_phrase: {'lower_phrase' in result and result['lower_phrase'] is not None}"
        )

    print()

    # 2. detailsありでリクエスト（phraseが返る）
    print("=== Test 2: With details option ===")
    response = httpx.post(
        f"{BASE_URL}/detect",
        json={"text": test_text, "only_valid": True, "details": True},
    )
    data = response.json()
    print(f"Success: {data['success']}")
    print(f"Count: {data['count']}")

    if data["results"]:
        result = data["results"][0]
        print(f"Pattern: {result['pattern']}")
        print(f"Original text: {result['original_text']}")
        print(
            f"Has upper_phrase: {'upper_phrase' in result and result['upper_phrase'] is not None}"
        )
        print(
            f"Has middle_phrase: "
            f"{'middle_phrase' in result and result['middle_phrase'] is not None}"
        )
        print(
            f"Has lower_phrase: {'lower_phrase' in result and result['lower_phrase'] is not None}"
        )

        if result["upper_phrase"]:
            print(f"Upper phrase text: {result['upper_phrase']['text']}")
            print(f"Upper phrase reading: {result['upper_phrase']['reading']}")

    print()

    # 3. 改行が区切り文字として機能するかテスト
    print("=== Test 3: Newline as separator ===")
    test_text_inline = "春風にポッポーという汽笛聞く古池や蛙飛び込む水の音"

    response = httpx.post(
        f"{BASE_URL}/detect",
        json={"text": test_text_inline, "only_valid": True},
    )
    data = response.json()
    print(f"Inline text count: {data['count']}")

    response = httpx.post(
        f"{BASE_URL}/detect",
        json={"text": test_text, "only_valid": True},
    )
    data = response.json()
    print(f"With newlines count: {data['count']}")
    print("Newlines work as separator:", data["count"] > 0)


if __name__ == "__main__":
    try:
        test_detect_endpoint()
    except httpx.ConnectError:
        print("Error: API server is not running. Please start it with:")
        print("  cd detector && uv run python src/detector/api.py")
    except Exception as e:
        print(f"Error: {e}")

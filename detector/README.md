# Senryu Detector - Detector

川柳検知のメインロジックです。

## 俳句検知ロジック

テキストを形態素解析し、得られた読みを用いて川柳を検知します。

- 読みの中から5-7-5となるような組み合わせを見つけます
- 5-8-5, 6-7-5, 5-7-6の場合も字余り川柳として検知します
- 数字はモーラ数を基本とします
- 「ゃゅょ」のような拗音は基本的にモーラ数としてカウントしませんが、「っ」はモーラ数としてカウントします

## 利用ライブラリ

Pythonで記載します。

形態素解析はSudachiPy + SucachiDict-fullを用います。

APIはFastAPIを利用して提供します。

## 提供方法

API、およびコマンドラインによるREPLにより提供します。

### FastAPI REST API

川柳検知機能をREST APIとして提供します。

#### APIサーバーの起動

```bash
# uvicornで直接起動
uv run python -m detector.api

# または、スクリプトコマンドで起動（pyproject.tomlで定義）
senryu-api

# 開発モード（自動リロード有効）
uv run uvicorn detector.api:app --host 0.0.0.0 --port 8000 --reload
```

#### APIエンドポイント

- `GET /` - API基本情報
- `GET /health` - ヘルスチェック
- `GET /docs` - Swagger UI（自動生成されたAPI文書）
- `GET /redoc` - ReDoc（自動生成されたAPI文書）
- `GET /examples` - 川柳の例文取得
- `POST /detect` - 単一テキストの川柳検知
- `POST /detect/batch` - 複数テキストの一括検知

#### API使用例

```bash
# ヘルスチェック
curl http://localhost:8000/health

# 川柳検知
curl -X POST http://localhost:8000/detect \
  -H "Content-Type: application/json" \
  -d '{"text": "古池や蛙飛び込む水の音", "only_valid": true}'

# 一括検知
curl -X POST http://localhost:8000/detect/batch \
  -H "Content-Type: application/json" \
  -d '{
    "texts": ["古池や蛙飛び込む水の音", "夏草や兵どもが夢の跡"],
    "only_valid": false
  }'
```

#### Pythonでの利用例

```python
import requests

# 単一検知
response = requests.post(
    "http://localhost:8000/detect",
    json={"text": "古池や蛙飛び込む水の音", "only_valid": True}
)

data = response.json()
print(f"検知数: {data['count']}")
for result in data['results']:
    print(f"パターン: {result['pattern']}")
    print(f"読み: {result['full_reading']}")
    print(f"有効: {'✅' if result['is_valid'] else '❌'}")
```

#### APIテストの実行

```bash
# 統合テスト実行（APIサーバー不要）
uv run python test_api.py

# 実用例の実行（APIサーバーが必要）
uv run python api_usage_example.py
```

## CLI

### 形態素解析ツール

`analyze.py`は文字列の形態素解析結果と品詞情報を詳細表示するコマンドラインツールです。

```bash
# 基本使用法
uv run python analyze.py "古池や蛙飛び込む水の音"

# ヘルプ表示
uv run python analyze.py -h
```

#### 出力例

```
📝 入力テキスト: 古池や蛙飛び込む水の音
============================================================
🔍 形態素解析結果 (7トークン)
------------------------------------------------------------
 1. 表記: 古池         読み: ふるいけ
    品詞: 名詞                   モーラ数: 4
    計算済みモーラ数: 4

 2. 表記: や          読み: や
    品詞: 助詞                   モーラ数: 1
    計算済みモーラ数: 1

[...省略...]

📊 総モーラ数: 17

🎋 川柳パターン適合性:
------------------------------
✅ 標準川柳: [5, 7, 5] (合計17モーラ)
❌ 字余り5-8-5: [5, 8, 5] (合計18モーラ)
❌ 字余り6-7-5: [6, 7, 5] (合計18モーラ)
❌ 字余り5-7-6: [5, 7, 6] (合計18モーラ)
```

### 対話型REPL

`repl.py`は川柳検知の対話型テストツールです。

```bash
# 対話モード起動
uv run python repl.py
```

#### 使用例

```
🎋 川柳検知器 対話テスト
テキストを入力してください（'q'で終了）
========================================

> 古池や蛙飛び込む水の音
✅ 1件検知:
  1. [5-7-5] 有効
     古池や蛙飛び込む水の音 (ふるいけやかわずとびこむみずのおと)

> プログラミングは楽しい作業だ
❌ 川柳は検知されませんでした

> q
終了します。
```

### その他のCLIツール

プロジェクトルートには他にも便利な実行スクリプトがあります：

```bash
# メインデモスクリプト（詳細な出力）
uv run python run_detector.py

# クイックテスト（推奨）
uv run python quick_test.py

# APIサーバー起動
uv run python -m detector.api
```

## REPLでの実行例

### 1. 基本的な使用方法

```python
# パッケージのインポート
from detector import SenryuDetector

# 検知器を初期化（二値判定システム）
detector = SenryuDetector()

# 川柳を検知
text = "ふるいけやかわずとびこむみずのおと"
results = detector.detect(text)

# 結果を表示
for result in results:
    print(f"パターン: {result.pattern.value}")
    print(f"有効: {'✅' if result.is_valid else '❌'}")
    print(f"読み: {result.full_reading}")
    print(f"上句: {result.upper_phrase.reading} ({result.upper_phrase.mora_count})")
    print(f"中句: {result.middle_phrase.reading} ({result.middle_phrase.mora_count})")
    print(f"下句: {result.lower_phrase.reading} ({result.lower_phrase.mora_count})")
```

### 2. モーラ計算のテスト

```python
from detector.core.mora import count_mora

# 様々なテキストのモーラ数を確認
examples = [
    "こんにちは",      # 5モーラ
    "きょう",          # 2モーラ（きょ=き+ょ、ょは0モーラ）
    "がっこう",        # 4モーラ（が+っ+こ+う）
    "コンピューター",  # 6モーラ
]

for text in examples:
    count = count_mora(text)
    print(f"{text}: {count}モーラ")
```

### 3. パターンマッチングのテスト

```python
from detector.core.patterns import is_valid_senryu_pattern, get_pattern_type

# 様々なモーラパターンをテスト
patterns = [
    (5, 7, 5),  # 標準川柳
    (5, 8, 5),  # 字余り川柳1
    (6, 7, 5),  # 字余り川柳2
    (5, 7, 6),  # 字余り川柳3
    (3, 5, 3),  # 無効なパターン
]

for pattern in patterns:
    valid = is_valid_senryu_pattern(pattern)
    pattern_type = get_pattern_type(pattern)
    print(f"{pattern}: 有効={valid}, タイプ={pattern_type}")
```

### 4. 有効/無効な検知結果の確認

```python
text = "ふるいけやかわずとびこむみずのおと"

detector = SenryuDetector()
results = detector.detect(text)

print(f"検知結果: {len(results)}件")
for i, result in enumerate(results, 1):
    status = "有効" if result.is_valid else "無効"
    print(f"{i}. {status}: {result.pattern.value} - {result.full_reading}")
```

### 5. 複数の川柳候補を含むテキスト

```python
# 長いテキストから川柳を抽出
text = "昨日は良い天気でした。ふるいけやかわずとびこむみずのおと。今日は雨が降っています。"

detector = SenryuDetector()
results = detector.detect(text)

print(f"検知された川柳: {len(results)}件")
for i, result in enumerate(results, 1):
    status = "✅" if result.is_valid else "❌"
    print(f"{i}. {status} {result.original_text}")
    print(f"   パターン: {result.pattern.value}")
    print(f"   位置: {result.start_position}-{result.end_position}")
```

## デモスクリプトの実行

```bash
# 基本デモ
python examples/repl_demo.py --mode demo

# 対話モード
python examples/repl_demo.py --mode interactive

# 信頼度テスト
python examples/repl_demo.py --mode confidence

# REPL実行例の表示
python examples/repl_demo.py --mode examples
```

## 実行方法

### クイックテスト（推奨）
```bash
# 基本テスト実行
uv run python quick_test.py

# 対話モード
uv run python quick_test.py -i
```

### 詳細デモ
```bash
# メインデモスクリプト
uv run python run_detector.py

# または引数付きで直接テキスト分析
uv run python run_detector.py "古池や蛙飛び込む水の音"
```

### モジュールとして実行
```bash
# パッケージとして実行
uv run python -m detector.main

# 直接実行（パス設定済み）
uv run python src/detector/main.py
```

## 開発・テスト用コマンド

```bash
# 依存関係インストール
uv sync --dev

# 品質チェック
uv run ruff check .        # Lint
uv run ruff format .       # Format
uv run mypy .             # 型チェック

# テスト実行
uv run pytest            # 基本実行
uv run pytest -v        # 詳細出力
uv run pytest --cov=src # カバレッジ付き
```

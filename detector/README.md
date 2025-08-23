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

### API

// TODO

## CLI

// TODO

## REPLでの実行例

### 1. 基本的な使用方法

```python
# パッケージのインポート
from detector import SenryuDetector

# 検知器を初期化
detector = SenryuDetector(min_confidence=0.5)

# 川柳を検知
text = "ふるいけやかわずとびこむみずのおと"
results = detector.detect(text)

# 結果を表示
for result in results:
    print(f"パターン: {result.pattern.value}")
    print(f"信頼度: {result.confidence:.3f}")
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

### 4. 信頼度による結果の違い

```python
text = "ふるいけやかわずとびこむみずのおと"

# 異なる信頼度閾値での結果を比較
thresholds = [0.1, 0.5, 0.9]

for threshold in thresholds:
    detector = SenryuDetector(min_confidence=threshold)
    results = detector.detect(text)
    print(f"信頼度閾値 {threshold}: {len(results)}件の結果")
```

### 5. 複数の川柳候補を含むテキスト

```python
# 長いテキストから川柳を抽出
text = "昨日は良い天気でした。ふるいけやかわずとびこむみずのおと。今日は雨が降っています。"

detector = SenryuDetector(min_confidence=0.3)
results = detector.detect(text)

print(f"検知された川柳: {len(results)}件")
for i, result in enumerate(results, 1):
    print(f"{i}. {result.original_text}")
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

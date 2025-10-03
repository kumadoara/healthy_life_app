# ヘルシーライフアプリ - テスト実行ガイド

## 📋 概要

このドキュメントは ヘルシーライフアプリの開発者向けテスト実行ガイド です。
pytest をベースに、ユニット・統合・API テストやカバレッジ測定、CI/CD 連携までを網羅しています

## 🚀 クイックスタート

### 1. テスト環境のセットアップ

```bash
# 依存関係のインストール
# 1. テスト依存関係のインストール
pip install -r test_requirements.txt

# 2. （オプション）仮想環境の作成と有効化
python -m venv test_env
source test_env/bin/activate  # macOS/Linux
test_env\Scripts\activate  # Windows

# または Makefileを使用
make test
```
### 2. 基本的なテスト実行

```bash
# 全テスト実行（デフォルト: カバレッジ付き）
python run_tests.py

# 単体テストのみ
python run_tests.py --type unit

# 特定のテストファイル
python run_tests.py --file test_models.py

# カバレッジなしで実行
python run_tests.py --no-coverage

```

## 📁 テストファイル構成

```
healthy_life_app/
├── src/
│   ├── models/
│   ├── services/
│   └── utils/
├── tests/
│   ├── test_requirements.txt - テスト依存関係
│   ├── pytest.ini - pytest設定
│   ├── conftest.py - テスト設定とフィクスチャ
│   ├── run_tests.py- テスト実行スクリプト
│   ├── test_models.py - モデル関連のテスト
│   ├── test_helpers.py - ヘルパー関数のテスト
│   ├── test_data_manager.py - データマネージャー関連のテスト
│   ├── テスト用Makefile
│   ├── models/test_user_profile.py - ユーザープロフィールモデルテスト
│   ├── models/test_workout_record.py - ワークアウト記録モデルテスト
│   ├── models/test_nutrition_record.py - 栄養記録モデルテスト
│   ├── utils/test_bmi_calculator.py - BMI計算機能テスト
│   ├── utils/test_bmr_calculator.py - BMR計算機能テスト
│   ├── utils/test_tdee_calculator.py - TDEE計算機能テスト
│   ├── utils/test_macro_calculator.py - マクロ栄養素計算機能テスト
│   ├── services/test_data_manager_profiles.py - データマネージャー プロフィール管理テスト
│   ├── services/test_data_manager_workouts.py - データマネージャー ワークアウト記録管理テスト
│   ├── services/test_data_manager_nutrition.py - データマネージャー 栄養記録管理テスト
│   ├── services/test_food_nutrition_info.py - 食品栄養情報テスト
│   ├── services/test_food_nutrition_service.py - 食品栄養サービステスト
│   ├── services/test_nutrition_cal.py - 栄養計算機能テスト
│   ├── services/test_chat_service_initialization.py - チャットサービス 初期化機能テスト
│   ├── services/test_chat_service_nutrition.py - チャットサービス 栄養相談機能テスト
│   ├── services/test_chat_service_training.py - チャットサービスのトレーニング相談機能テスト
│   └── services/test_services_chat_service.py - チャットサービス全般テスト
│   └── services/test_workout_feedback_service.py - ワークアウトフィードバック機能テスト
└── README.md - このドキュメント
```

## 🎯 テストタイプ別実行

## 📄 特定のテストファイル実行

```bash
# 特定のテストファイルを実行
python run_tests.py --file test_models.py

# 特定のテストクラスを実行
pytest tests/test_models.py::TestUserProfile

# 特定のテストメソッドを実行
pytest tests/test_models.py::TestUserProfile::test_valid_user_profile_creation
```

## 📊 カバレッジレポート

```bash
# HTMLレポートを確認
# macOS
open htmlcov/index.html
# Windows
start htmlcov/index.html
# Linux
xdg-open htmlcov/index.html

# ターミナルで表示
pytest --cov=src --cov-report=term-missing tests/

```

## 🔍 コード品質チェック

### 静的解析実行

```bash
# Lintingを実行
python run_tests.py --lint

# 手動でflake8実行
flake8 src/ --max-line-length=100 --ignore=E203,W503
```

## 📈 テストレポート生成

```bash
# HTMLテストレポートを生成
python run_tests.py --report

# 確認（OSごとに）
open test_report.html      # macOS
start test_report.html     # Windows
xdg-open test_report.html  # Linux
```

## 🧹 クリーンアップ

```bash
# テストキャッシュ・カバレッジを削除
python run_tests.py --clean
```

## ⚙️ 詳細なテスト実行オプション

### pytest直接実行

```bash
# 詳細出力でテスト実行
pytest -v tests/

# 特定のマーカーでテスト実行
pytest -m "unit" tests/
pytest -m "integration" tests/
pytest -m "api" tests/
pytest -m "not slow" tests/   # 遅いテストを除外

# デバッグモードで実行
pytest --pdb tests/

# 最初の失敗で停止
pytest -x tests/

# 並列実行（pytest-xdistが必要）
pytest -n auto tests/
```

## 🐛 トラブルシューティング

### よくある問題と解決方法

#### 1. 依存関係エラー

```bash
# 依存関係を再インストール
pip install -r test_requirements.txt

# 仮想環境を使用
python -m venv test_env
source test_env/bin/activate  # Linux/Mac
test_env\Scripts\activate     # Windows
pip install -r test_requirements.txt
```

#### 2. インポートエラー

```bash
# PYTHONPATHを設定
export PYTHONPATH="${PYTHONPATH}:${PWD}"  # Linux/Mac
set PYTHONPATH=%PYTHONPATH%;%CD%          # Windows
```

#### 3. APIキーエラー

```bash
# テスト用の環境変数を設定（オプション）
export OPENAI_API_KEY="test_key"
```

## 📝 テストの書き方

### 新しいテストファイルの作成

```python
# tests/test_new_feature.py
import pytest
from src.models.new_feature import NewFeature

class TestNewFeature:
    """新機能のテスト"""
    
@pytest.fixture
def sample_feature():
    return NewFeature("sample")

class TestNewFeature:
    def test_creation(self, sample_feature):
        assert sample_feature.name == "sample"

    @pytest.mark.unit
    def test_method(self, sample_feature):
        assert sample_feature.process() is not None
```

## 🔧 設定ファイル

### pytest.ini

```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --tb=short
    --strict-markers
    --disable-warnings
    --cov=src
    --cov-report=html
    --cov-report=term-missing
markers =
    unit: 単体テスト
    integration: 統合テスト
    api: API関連テスト
    slow: 実行時間が長いテスト
```

## 📊 カバレッジ目標

- **全体カバレッジ**: 80%以上
- **重要なビジネスロジック**: 95%以上
- **ユーティリティ関数**: 90%以上

## 🚨 CI/CD統合

### GitHub Actions例

```yaml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - uses: actions/setup-python@v4
      with:
        python-version: "3.10"
    - name: Install dependencies
      run: python -m pip install -r test_requirements.txt
    - name: Run tests with coverage
      run: pytest --cov=src --cov-report=xml tests/
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml

```

## 🎉 ベストプラクティス

1. **テストファーストアプローチ**: 新機能開発前にテストを書く
2. **小さなテスト**: 1つのテストで1つの機能をテスト
3. **明確な命名**: テスト名から何をテストしているかが分かる
4. **独立性**: テスト間で依存関係を持たない
5. **モック使用**: 外部依存をモック化する
6. **データクリーンアップ**: テスト後のデータクリーンアップを確実に行う

## 📈 継続的改善

- 定期的なテスト実行
- カバレッジ率の監視
- 新機能追加時のテスト追加
- リファクタリング時のテスト更新

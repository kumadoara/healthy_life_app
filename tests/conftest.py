"""テスト設定とフィクスチャ"""

import pytest
import tempfile
import shutil
import sys
from pathlib import Path
from datetime import datetime
from unittest.mock import patch, mock_open
import os

# プロジェクトルートを sys.path に追加
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.models.user_profile import UserProfile, WorkoutRecord, NutritionRecord
from src.services.data_manager import DataManager

@pytest.fixture
def temp_data_dir() -> dir:
    """テスト用の一時ディレクトリを作成"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)

@pytest.fixture
def sample_user_profile() -> UserProfile:
    """サンプルユーザープロフィール"""
    return UserProfile(
        name="テストユーザー",
        age=30,
        gender="男性",
        height=175.0,
        weight=70.0,
        activity_level="適度な運動",
        goal="体重維持"
    )

@pytest.fixture
def sample_workout_record() -> WorkoutRecord:
    """サンプルワークアウト記録"""
    return WorkoutRecord(
        date=datetime(2025, 1, 1, 10, 0),
        exercise="ランニング",
        duration=30,
        calories=300,
        intensity="中",
        notes="朝のジョギング"
    )

@pytest.fixture
def sample_nutrition_record() -> NutritionRecord:
    """サンプル栄養記録"""
    return NutritionRecord(
        date=datetime(2025, 1, 1, 12, 0),
        meal_type="昼食",
        foods=[{
            "name": "鶏胸肉",
            "calories": 200.0,
            "protein": 25.0,
            "carbs": 0.0,
            "fat": 5.0
        }],
        total_calories=200.0,
        notes="高タンパク質ランチ"
    )

@pytest.fixture
def data_manager(temp_data_dir) -> DataManager:
    """テスト用データマネージャー"""
    return DataManager(data_dir=temp_data_dir)

@pytest.fixture
def mock_openai_client():
    """モック化されたOpenAIクライアント"""
    with patch('openai.OpenAI') as mock_client:
        mock_instance = mock_client.return_value
        mock_instance.chat.completions.create.return_value = {
            "choices": [{"message": {"content": '{"test": "response"}'}}]
        }

        yield mock_instance

@pytest.fixture(autouse=True)
def mock_streamlit():
    """Streamlitのモック"""
    with patch.multiple(
        'streamlit',
        session_state={},
        error=lambda msg: None,
        success=lambda msg: None,
        warning=lambda msg: None,
        info=lambda msg: None,
    ) as mocks:
        yield mocks

@pytest.fixture(autouse=True)
def setup_test_environment():
    """テスト環境のセットアップ"""
    # 環境変数のクリア
    test_env_vars = ['OPENAI_API_KEY']
    original_values = {}

    for var in test_env_vars:
        original_values[var] = os.environ.get(var)
        if var in os.environ:
            del os.environ[var]
    
    yield

    # 環境変数の復元
    for var, value in original_values.items():
        if value is not None:
            os.environ[var] = value

@pytest.fixture
def mock_file_operations():
    """ファイル操作のモック"""
    with patch('pathlib.Path.exists', return_value=True) as mock_exists, \
         patch('pathlib.Path.mkdir') as mock_mkdir, \
         patch('builtins.open', mock_open(read_data="dummy")) as mock_file:

        yield {
            'exists': mock_exists,
            'mkdir': mock_mkdir,
            'open': mock_open
        }

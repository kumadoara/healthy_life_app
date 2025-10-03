"""DataManagerクラスのテスト"""

import pytest
import json
from pathlib import Path
from datetime import datetime
from freezegun import freeze_time

from src.services.data_manager import DataManager
from src.models.user_profile import UserProfile, WorkoutRecord, NutritionRecord

# -------------------------
# 共通フィクスチャ
# -------------------------
@pytest.fixture
def workout_samples():
    """複数のワークアウト記録を返す"""
    return [
        WorkoutRecord(
            date=datetime(2025, 1, 1),
            exercise="ランニング",
            duration=30,
            calories=300,
            intensity="中"
        ),
        WorkoutRecord(
            date=datetime(2025, 1, 2),
            exercise="筋トレ",
            duration=45,
            calories=200,
            intensity="高"
        )
    ]

@pytest.fixture
def nutrition_samples():
    """複数の栄養記録を返す"""
    return [
        NutritionRecord(
            date=datetime(2025, 1, 1, 8, 0),
            meal_type="朝食",
            foods=[{"name": "パン", "calories": 200.0, "protein": 8.0, "carbs": 40.0, "fat": 2.0}],
            total_calories=200.0
        ),
        NutritionRecord(
            date=datetime(2025, 1, 1, 12, 0),
            meal_type="昼食",
            foods=[{"name": "米", "calories": 300.0, "protein": 6.0, "carbs": 65.0, "fat": 1.0}],
            total_calories=300.0
        )
    ]

class TestDataManager:
    """DataManagerクラスのテスト"""

    def test_initialization_creates_required_files(self, temp_data_dir: str):
        """初期化時に必要なJSONファイルが作成される"""
        dm = DataManager(data_dir=temp_data_dir)
        assert dm.data_dir == Path(temp_data_dir)
        assert (dm.data_dir / "workouts.json").exists()
        assert (dm.data_dir / "nutrition.json").exists()
    
    def test_save_and_load_profile_roundtrip(self, data_manager: DataManager, sample_user_profile: UserProfile):
        """プロフィールの保存後に同じ内容を読み込める"""
        assert data_manager.save_profile(sample_user_profile) is True
        loaded = data_manager.load_profile()
        assert loaded is not None
        assert loaded.name == sample_user_profile.name
        assert loaded.age == sample_user_profile.age
    
    def test_load_profile_returns_none_if_not_exists(self, data_manager: DataManager):
        """プロフィールが存在しない場合は None を返す"""
        assert data_manager.load_profile() is None

    @freeze_time("2025-01-01 08:00:00")
    def test_save_and_load_workout_with_frozen_time(self, data_manager: DataManager):
        """ワークアウト記録の保存後に同じ日時で読み込める"""
        record = WorkoutRecord(
            date=datetime.now(),
            exercise="ランニング",
            duration=30,
            calories=300,
            intensity="中"
        )
        assert data_manager.save_workout(record) is True
        workouts = data_manager.load_workouts()
        assert workouts[0].date == datetime(2025, 1, 1, 8, 0, 0)
    
    def test_save_multiple_workouts_and_load_all(self, data_manager: DataManager, workout_samples: list[WorkoutRecord]):
        """複数ワークアウト記録を保存・読み込める"""
        for w in workout_samples:
            data_manager.save_workout(w)
        workouts = data_manager.load_workouts()
        assert len(workouts) == 2
        assert {w.exercise for w in workouts} == {"ランニング", "筋トレ"}
    
    @pytest.mark.parametrize("index, expected_result, expected_count", [
        (0, True, 0),  # 有効なインデックス（1つの要素を削除すると0になる）
        (10, False, 1), # 無効なインデックス（削除されず1つ残る）
    ])
    def test_delete_workout_handles_valid_and_invalid_index(
        self,
        data_manager: DataManager,
        sample_workout_record: WorkoutRecord,
        index: int, 
        expected_result: bool,
        expected_count: int
    ):
        """ワークアウト削除が有効・無効なインデックスで正しく動作する"""
        data_manager.save_workout(sample_workout_record)
        result = data_manager.delete_workout(index)
        assert result is expected_result
        assert len(data_manager.load_workouts()) == expected_count
    
    def test_save_and_load_nutrition_roundtrip(self, data_manager: DataManager, sample_nutrition_record: NutritionRecord):
        """栄養記録の保存後に同じ内容を読み込める"""
        assert data_manager.save_nutrition(sample_nutrition_record) is True
        records = data_manager.load_nutrition()
        assert len(records) == 1
        assert records[0].meal_type == sample_nutrition_record.meal_type
    
    def test_delete_nutrition_removes_record(self, data_manager: DataManager, nutrition_samples: list[NutritionRecord]):
        """栄養記録を削除できる"""
        for n in nutrition_samples:
            data_manager.save_nutrition(n)
        assert data_manager.delete_nutrition(0) is True
        records = data_manager.load_nutrition()
        assert len(records) == 1
        assert records[0].meal_type == "昼食"
    
    def test_load_empty_files_returns_empty_lists(self, data_manager: DataManager):
        """空ファイルを読み込むと空リストが返る"""
        assert data_manager.load_workouts() == []
        assert data_manager.load_nutrition() == []
    
    def test_load_corrupted_json_recovers_to_empty(self, temp_data_dir: str):
        """破損したJSONを読み込むと空リストに回復する"""
        dm = DataManager(data_dir=temp_data_dir)
        corrupted_file = dm.data_dir / "workouts.json"
        corrupted_file.write_text("{ invalid json }")

        workouts = dm.load_workouts()
        assert workouts == []

        with open(corrupted_file, "r", encoding="utf-8") as f:
            assert json.load(f) == []
    
    def test_ensure_json_files_initializes_empty_lists(self, temp_data_dir: str):
        """ensure_json_files が空リストでファイルを初期化する"""
        dm = DataManager(data_dir=temp_data_dir)
        for fname in ("workouts.json", "nutrition.json"):
            path = dm.data_dir / fname
            assert path.exists()
            with open(path, "r", encoding="utf-8") as f:
                assert json.load(f) == []
    
    def test_clear_all_data_removes_all_records(
            self,
            data_manager: DataManager,
            sample_workout_record: WorkoutRecord,
            sample_nutrition_record: NutritionRecord
    ):
        """全データクリアでワークアウトと栄養記録が消去される"""
        data_manager.save_workout(sample_workout_record)
        data_manager.save_nutrition(sample_nutrition_record)
        assert len(data_manager.load_workouts()) == 1
        assert len(data_manager.load_nutrition()) == 1

        data_manager.clear_all_data()
        assert data_manager.load_workouts() == []
        assert data_manager.load_nutrition() == []

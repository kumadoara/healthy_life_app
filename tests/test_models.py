"""モデルクラスのテスト"""

import pytest
from datetime import datetime
from pydantic import ValidationError
from freezegun import freeze_time

from src.models.user_profile import UserProfile, WorkoutRecord, NutritionRecord

class TestUserProfile:
    """UserProfileモデルのテスト"""

    def test_user_profile_creation_with_valid_data(self, sample_user_profile: UserProfile):
        """正常なユーザープロフィールが作成できる"""
        profile = sample_user_profile
        assert profile.name == "テストユーザー"
        assert profile.age == 30
        assert profile.gender == "男性"
        assert profile.height == 175.0
        assert profile.weight == 70.0
        assert profile.activity_level == "適度な運動"
        assert profile.goal == "体重維持"
    
    @pytest.mark.parametrize("field, value", [
        ("age", -1),
        ("height", -10.0),
        ("weight", -5.0),
    ])

    def test_user_profile_invalid_fields_raise_validation_error(self, field: str, value):
        """不正な値が指定された場合 ValidationError が発生する"""
        data = dict(
            name="テスト",
            age=30,
            gender="男性",
            height=175.0,
            weight=70.0,
            activity_level="適度な運動",
            goal="体重維持",
        )
        data[field] = value
        with pytest.raises(ValidationError):
            UserProfile(**data)
    
    def test_user_profile_model_dump_returns_dict(self, sample_user_profile: UserProfile):
        """model_dump の結果が正しい辞書形式になる"""
        profile_dict = sample_user_profile.model_dump()
        assert isinstance(profile_dict, dict)
        assert profile_dict["name"] == "テストユーザー"
        assert profile_dict["age"] == 30

    def test_user_profile_has_datetime_fields(self, sample_user_profile: UserProfile):
        """UserProfile に created_at / updated_at が含まれる"""
        assert isinstance(sample_user_profile.created_at, datetime)
        assert isinstance(sample_user_profile.updated_at, datetime)

class TestWorkoutRecord:
    """WorkoutRecordモデルのテスト"""

    def test_workout_record_creation_with_valid_data(self, sample_workout_record: WorkoutRecord):
        """正常なワークアウト記録が作成できる"""
        record = sample_workout_record
        assert record.exercise == "ランニング"
        assert record.duration == 30
        assert record.calories == 300
        assert record.intensity == "中"
        assert record.notes == "朝のジョギング"

    def test_workout_record_without_notes_is_allowed(self):
        """メモなしでもワークアウト記録が作成できる"""
        record = WorkoutRecord(
            date=datetime.now(),
            exercise="筋トレ",
            duration=45,
            calories=200,
            intensity="高"
        )
        assert record.notes is None
    
    def test_workout_record_model_dump_returns_dict(self, sample_workout_record: WorkoutRecord):
        """model_dump の結果が正しい辞書形式になる"""
        record_dict = sample_workout_record.model_dump()
        assert isinstance(record_dict, dict)
        assert record_dict["exercise"] == "ランニング"
        assert record_dict["duration"] == 30

    @pytest.mark.parametrize("field, value", [
        ("duration", -10),
        ("calories", -50),
    ])

    def test_invalid_workout_record_fields_raise_validation_error(self, field: str, value):
        """不正な値が指定された場合 ValidationError が発生する"""
        data = dict(
            date=datetime.now(),
            exercise="ランニング",
            duration=30,
            calories=300,
            intensity="中",
        )
        data[field] = value
        with pytest.raises(ValidationError):
            WorkoutRecord(**data)
        
    @freeze_time("2025-01-01 10:00:00")
    def test_workout_record_with_frozen_datetime(self):
        """freezegun で固定した日時を利用できる"""
        record = WorkoutRecord(
            date=datetime.now(),
            exercise="サイクリング",
            duration=60,
            calories=400,
            intensity="高"
        )
        assert record.date == datetime(2025, 1, 1, 10, 0, 0)

class TestNutritionRecord:
    """NutritionRecordモデルのテスト"""

    def test_nutrition_record_creation_with_valid_data(self, sample_nutrition_record: NutritionRecord):
        """正常な栄養記録が作成できる"""
        record = sample_nutrition_record
        assert record.meal_type == "昼食"
        assert len(record.foods) == 1
        assert record.total_calories == 200.0
        assert record.notes == "高タンパク質ランチ"
    
    def test_nutrition_record_without_notes_is_allowed(self):
        """メモなしでも栄養記録が作成できる"""
        record = NutritionRecord(
            date=datetime.now(),
            meal_type="朝食",
            foods=[{
                "name": "卵",
                "calories": 150.0,
                "protein": 12.0,
                "carbs": 1.0,
                "fat": 10.0
            }],
            total_calories=150.0
        )
        assert record.notes is None

    def test_nutrition_record_model_dump_includes_foods(self, sample_nutrition_record: NutritionRecord):
        """model_dump の結果に食品情報が含まれる"""
        record_dict = sample_nutrition_record.model_dump()
        assert isinstance(record_dict, dict)
        assert record_dict["meal_type"] == "昼食"
        assert isinstance(record_dict["foods"], list)
        assert len(record_dict["foods"]) == 1
        assert record_dict["foods"][0]["name"] == "鶏胸肉" 
    
    def test_nutrition_record_with_empty_foods_is_allowed(self):
        """食品リストが空でも栄養記録が作成できる"""
        record = NutritionRecord(
            date=datetime.now(),
            meal_type="間食",
            foods=[],
            total_calories=0.0
        )
        assert len(record.foods) == 0
        assert record.total_calories == 0.0

    def test_nutrition_record_with_multiple_foods(self):
        """複数食品の栄養記録を作成できる"""
        foods = [
            {"name": "ご飯", "calories": 250.0, "protein": 5.0, "carbs": 55.0, "fat": 1.0},
            {"name": "味噌汁", "calories": 50.0, "protein": 3.0, "carbs": 5.0, "fat": 1.0},
        ]
        record = NutritionRecord(
            date=datetime.now(),
            meal_type="朝食",
            foods=foods,
            total_calories=300.0
        )
        assert len(record.foods) == 2
        assert record.total_calories == 300.0

    @pytest.mark.parametrize("field, value", [
        ("total_calories", -100.0),
    ])

    def test_invalid_nutrition_record_fields_raise_validation_error(self, field: str, value):
        """不正な値が指定された場合 ValidationError が発生する"""
        data = dict(
            date=datetime.now(),
            meal_type="夕食",
            foods=[],
            total_calories=0.0,
        )
        data[field] = value
        with pytest.raises(ValidationError):
            NutritionRecord(**data)

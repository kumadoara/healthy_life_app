"""データマネージャー - 栄養記録管理のテスト"""

import pytest
import json
from datetime import datetime, timedelta
from unittest.mock import patch

from src.services.data_manager import DataManager
from src.models.user_profile import NutritionRecord, FoodItem


# -----------------------
# 共通 fixture
# -----------------------
@pytest.fixture
def dm(temp_data_dir):
    """テスト用 DataManager インスタンス"""
    return DataManager(data_dir=temp_data_dir)

@pytest.fixture
def sample_food():
    """共通で使う食品データ"""
    return {"name": "テスト食品", "calories": 200.0, "protein": 10.0, "carbs": 20.0, "fat": 5.0}

# -----------------------
# 保存テスト
# -----------------------
def test_save_single_nutrition_record(dm):
    record = NutritionRecord(
        date=datetime(2025, 1, 15, 12, 30),
        meal_type="昼食",
        foods=[{"name": "鶏胸肉", "calories": 200.0, "protein": 25.0, "carbs": 0.0, "fat": 5.0}],
        total_calories=200.0,
        notes="高タンパク質ランチ",
    )
    assert dm.save_nutrition(record) is True
    assert (dm.data_dir / "nutrition.json").exists()

def test_save_multiple_nutrition_records(dm, sample_food):
    meal_types = ["朝食", "昼食", "夕食"]
    for i, meal in enumerate(meal_types):
        dm.save_nutrition(NutritionRecord(date=datetime(2025, 1, 15, 8 + i, 0), meal_type=meal, foods=[sample_food], total_calories=200.0))
    assert len(dm.load_nutrition()) == 3

def test_save_nutrition_with_food_item(dm):
    food_item = FoodItem(name="サーモン", calories=208.0, protein=25.4, carbs=0.0, fat=12.4)
    record = NutritionRecord(date=datetime.now(), meal_type="夕食", foods=[food_item], total_calories=208.0)
    assert dm.save_nutrition(record) is True
    loaded = dm.load_nutrition()
    assert loaded[0].foods[0].name == "サーモン"

def test_save_nutrition_mixed_food_formats(dm):
    food_item = FoodItem(name="リンゴ", calories=52.0, protein=0.3, carbs=14.0, fat=0.2)
    food_dict = {"name": "オレンジ", "calories": 47.0, "protein": 0.9, "carbs": 12.0, "fat": 0.1}
    record = NutritionRecord(date=datetime.now(), meal_type="間食", foods=[food_item, food_dict], total_calories=99.0)
    dm.save_nutrition(record)
    loaded = dm.load_nutrition()
    assert [f.name for f in loaded[0].foods] == ["リンゴ", "オレンジ"]

def test_save_nutrition_datetime_serialization(dm, sample_food):
    meal_date = datetime(2025, 1, 15, 12, 30, 45)
    record = NutritionRecord(date=meal_date, meal_type="昼食", foods=[sample_food], total_calories=200.0)
    dm.save_nutrition(record)
    with open(dm.data_dir / "nutrition.json", "r", encoding="utf-8") as f:
        saved_data = json.load(f)
    assert saved_data[0]["date"] == meal_date.isoformat()

# -----------------------
# 読み込みテスト
# -----------------------
def test_load_empty_nutrition(dm):
    assert dm.load_nutrition() == []

def test_load_saved_nutrition(dm, sample_food):
    original = NutritionRecord(date=datetime(2025, 1, 15, 12, 30), meal_type="昼食", foods=[sample_food], total_calories=300.0, notes="テストメモ")
    dm.save_nutrition(original)
    loaded = dm.load_nutrition()[0]
    assert loaded.meal_type == "昼食"
    assert loaded.total_calories == 300.0
    assert loaded.notes == "テストメモ"
    assert loaded.foods[0].name == "テスト食品"

def test_load_corrupted_nutrition_file(dm):
    with open(dm.data_dir / "nutrition.json", "w", encoding="utf-8") as f:
        f.write("{ invalid json }")
    result = dm.load_nutrition()
    assert result == []

# -----------------------
# 削除テスト (parametrize)
# -----------------------
@pytest.mark.parametrize(
    "meal_types, delete_index, expected_remaining",
    [
        (["朝食", "昼食", "夕食"], 0, ["昼食", "夕食"]),
        (["朝食", "昼食", "夕食"], 1, ["朝食", "夕食"]),
        (["朝食", "昼食", "夕食"], 2, ["朝食", "昼食"]),
    ],
)
def test_delete_nutrition_cases(dm, meal_types, delete_index, expected_remaining, sample_food):
    for meal in meal_types:
        dm.save_nutrition(NutritionRecord(date=datetime.now(), meal_type=meal, foods=[sample_food], total_calories=200.0))
    assert dm.delete_nutrition(delete_index) is True
    assert [n.meal_type for n in dm.load_nutrition()] == expected_remaining

def test_delete_only_nutrition(dm, sample_food):
    record = NutritionRecord(date=datetime.now(), meal_type="間食", foods=[sample_food], total_calories=100.0)
    dm.save_nutrition(record)
    assert dm.delete_nutrition(0) is True
    assert dm.load_nutrition() == []

@pytest.mark.parametrize("invalid_index", [-1, 10])
def test_delete_invalid_index(dm, invalid_index, sample_food):
    record = NutritionRecord(date=datetime.now(), meal_type="昼食", foods=[sample_food], total_calories=200.0)
    dm.save_nutrition(record)
    assert dm.delete_nutrition(invalid_index) is False
    assert len(dm.load_nutrition()) == 1

def test_delete_from_empty(dm):
    result = dm.delete_nutrition(0)
    assert result is False

# -----------------------
# エラーハンドリング
# -----------------------
def test_save_nutrition_permission_error(dm, sample_food):
    record = NutritionRecord(date=datetime.now(), meal_type="夕食", foods=[sample_food], total_calories=200.0)
    with patch("builtins.open", side_effect=PermissionError("Permission denied")):
        result = dm.save_nutrition(record)
        assert result is False

def test_delete_nutrition_file_error(dm, sample_food):
    record = NutritionRecord(date=datetime.now(), meal_type="間食", foods=[sample_food], total_calories=200.0)
    dm.save_nutrition(record)
    with patch("builtins.open", side_effect=IOError("Input/output error")):
        result = dm.delete_nutrition(0)
        assert result is False

def test_save_invalid_record_missing_date(dm, sample_food):
    # バリデーションをバイパスして無効なレコードを作成
    record = NutritionRecord(date=datetime.now(), meal_type="朝食", foods=[sample_food], total_calories=200.0)
    record.date = None  # 後で無効な値を設定
    result = dm.save_nutrition(record)
    assert result is False

def test_save_invalid_record_empty_foods(dm):
    record = NutritionRecord(date=datetime.now(), meal_type="昼食", foods=[], total_calories=0.0)
    result = dm.save_nutrition(record)
    assert result is False

def test_save_invalid_food_type(dm):
    # バリデーションをバイパスして無効なレコードを作成
    record = NutritionRecord(date=datetime.now(), meal_type="夕食", foods=[{"name": "テスト", "calories": 100.0, "protein": 1.0, "carbs": 1.0, "fat": 1.0}], total_calories=100.0)
    record.foods = [12345]  # 後で無効な値を設定
    result = dm.save_nutrition(record)
    assert result is False

# -----------------------
# エッジケース & パフォーマンス
# -----------------------
def test_save_nutrition_with_unicode(dm):
    record = NutritionRecord(
        date=datetime.now(),
        meal_type="朝食",
        foods=[{"name": "寿司 🍣", "calories": 200.0, "protein": 15.0, "carbs": 25.0, "fat": 5.0}],
        total_calories=200.0,
        notes="美味しい和食でした 😋",
    )
    dm.save_nutrition(record)
    loaded = dm.load_nutrition()[0]
    assert loaded.meal_type == "朝食"
    assert loaded.foods[0].name == "寿司 🍣"

@pytest.mark.performance
def test_save_many_nutrition_records_performance(dm, sample_food):
    import time

    start = time.time()
    valid_meal_types = ['朝食', '昼食', '夕食', '間食', '夜食']
    for i in range(50):
        meal_type = valid_meal_types[i % len(valid_meal_types)]
        record = NutritionRecord(date=datetime.now() - timedelta(hours=i), meal_type=meal_type, foods=[sample_food], total_calories=200.0)
        dm.save_nutrition(record)
    duration = time.time() - start
    assert duration < 2.0
    assert len(dm.load_nutrition()) == 50

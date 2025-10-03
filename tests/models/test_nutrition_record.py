"""栄養記録モデルのテスト"""

import pytest
from datetime import datetime
from pydantic import ValidationError
from src.models.user_profile import NutritionRecord, FoodItem

# -----------------------------
# Fixtures
# -----------------------------
@pytest.fixture
def base_food():
    """標準的な食品データ"""
    return {"name": "テスト食品", "calories": 100.0, "protein": 5.0, "carbs": 10.0, "fat": 2.0}

@pytest.fixture
def base_record(base_food):
    """標準的な栄養記録"""
    return NutritionRecord(
        date=datetime(2025, 1, 15, 12, 30),
        meal_type="昼食",
        foods=[base_food],
        total_calories=100.0,
        notes="テストメモ"
    )


# -----------------------------
# 正常ケース
# -----------------------------
def test_valid_nutrition_record(base_record):
    """正常に栄養記録が作成できる"""
    assert base_record.meal_type == "昼食"
    assert base_record.total_calories == 100.0
    assert len(base_record.foods) == 1
    assert base_record.notes == "テストメモ"

@pytest.mark.parametrize("meal_type", ["朝食", "昼食", "夕食", "間食", "夜食"])
def test_meal_types(base_food, meal_type):
    """食事タイプごとの作成テスト"""
    record = NutritionRecord(
        date=datetime.now(),
        meal_type=meal_type,
        foods=[base_food],
        total_calories=100.0,
    )
    assert record.meal_type == meal_type

@pytest.mark.parametrize("food", [
    {"name": "ご飯", "calories": 250.0, "protein": 5.0, "carbs": 55.0, "fat": 1.0},
    {"name": "味噌汁", "calories": 50.0, "protein": 3.0, "carbs": 5.0, "fat": 1.0},
    {"name": "焼き魚", "calories": 180.0, "protein": 25.0, "carbs": 0.0, "fat": 8.0},
])
def test_multiple_foods(food):
    """複数食品を個別に検証"""
    record = NutritionRecord(
        date=datetime.now(),
        meal_type="夕食",
        foods=[food],
        total_calories=food["calories"]
    )
    # FoodItemオブジェクトの場合は属性でアクセス、辞書の場合は辞書でアクセス
    if hasattr(record.foods[0], 'name'):
        assert record.foods[0].name == food["name"]
    else:
        assert record.foods[0]["name"] == food["name"]
    assert record.total_calories == food["calories"]


# -----------------------------
# バリデーション
# -----------------------------
@pytest.mark.parametrize("invalid_calories", [-1.0, -100.0])
def test_invalid_total_calories(base_food, invalid_calories):
    """負のカロリーはエラー"""
    with pytest.raises(ValidationError):
        NutritionRecord(
            date=datetime.now(),
            meal_type="朝食",
            foods=[base_food],
            total_calories=invalid_calories,
        )

@pytest.mark.parametrize("invalid_calories", ["文字列", None])
def test_invalid_total_calories_type(base_food, invalid_calories):
    with pytest.raises(ValidationError):
        NutritionRecord(
        date=datetime.now(),
        meal_type="朝食",
        foods=[base_food],
        total_calories=invalid_calories,
    )

@pytest.mark.parametrize("invalid_meal_type", ["", None])
def test_invalid_meal_type(base_food, invalid_meal_type):
    """食事タイプが無効ならエラー"""
    with pytest.raises(ValidationError):
        NutritionRecord(
            date=datetime.now(),
            meal_type=invalid_meal_type,
            foods=[base_food],
            total_calories=100.0,
        )

def test_future_date_error(base_food):
    with pytest.raises(ValidationError):
        NutritionRecord(
            date=datetime(2100, 1, 1),
            meal_type="朝食",
            foods=[base_food],
            total_calories=100.0,
        )

def test_foods_none_error():
    with pytest.raises(ValidationError):
        NutritionRecord(
            date=datetime.now(),
            meal_type="夕食",
            foods=None,
            total_calories=200.0,
        )

def test_foods_invalid_type_error():
    with pytest.raises(ValidationError):
        NutritionRecord(
            date=datetime.now(),
            meal_type="夕食",
            foods="不正な文字列",
            total_calories=200.0,
        )

def test_empty_foods_is_allowed():
    """食品リストが空でも作成できる"""
    record = NutritionRecord(
        date=datetime.now(),
        meal_type="間食",
        foods=[],
        total_calories=0.0,
    )
    assert record.total_calories == 0.0
    assert record.foods == []

# -----------------------------
# FoodItem
# -----------------------------
@pytest.mark.parametrize("food_data", [
    {"name": "バナナ", "calories": 89.0, "protein": 1.1, "carbs": 22.8, "fat": 0.3},
    {"name": "水", "calories": 0.0, "protein": 0.0, "carbs": 0.0, "fat": 0.0},
])
def test_food_item_creation(food_data):
    """FoodItem の生成テスト"""
    food = FoodItem(**food_data)
    for key, value in food_data.items():
        assert getattr(food, key) == value

def test_food_item_invalid_name():
    """名前が空のFoodItemはエラー"""
    with pytest.raises(ValidationError):
        FoodItem(name="", calories=100.0, protein=5.0, carbs=10.0, fat=2.0)

# -----------------------------
# シリアライズ
# -----------------------------
def test_model_dump(base_record):
    """model_dump で dict が得られる"""
    record_dict = base_record.model_dump()
    assert record_dict["meal_type"] == "昼食"
    assert isinstance(record_dict["foods"], list)

def test_model_dump_json(base_record):
    """JSON シリアライズ/デシリアライズの確認"""
    import json
    json_str = base_record.model_dump_json()
    record_dict = json.loads(json_str)
    assert record_dict["meal_type"] == "昼食"
    assert record_dict["foods"][0]["name"] == "テスト食品"

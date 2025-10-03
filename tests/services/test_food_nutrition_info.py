import pytest
import requests
from unittest.mock import Mock, patch

class FoodNutrition:
    def __init__(self, name, calories_per_100g, protein=0, carbs=0, fat=0):
        self.name = name
        self.calories_per_100g = calories_per_100g
        self.protein = protein
        self.carbs = carbs
        self.fat = fat
        self.vitamins = {}
        self.minerals = {}

    def calculate_nutrition(self, weight_grams):
        if weight_grams < 0:
            raise ValueError("重量は0以上で入力してください")
        factor = weight_grams / 100
        return {
            'calories': self.calories_per_100g * factor,
            'protein': self.protein * factor,
            'carbs': self.carbs * factor,
            'fat': self.fat * factor
        }

class NutritionCalculator:
    @staticmethod
    def calculate_daily_needs(age, gender, weight, height, activity_level):
        if age <= 0:
            raise ValueError("年齢は正の整数で入力してください")
        if weight <= 0:
            raise ValueError("体重は1kg以上で入力してください")
        if height <= 0:
            raise ValueError("身長は正の数値で入力してください")
        if gender.lower() not in ["male", "female"]:
            raise ValueError("性別は male または female を指定してください")
        if gender.lower() == 'male':
            bmr = 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age)
        else:
            bmr = 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age)
        activity_multipliers = {
            'sedentary': 1.2,
            'light': 1.375,
            'moderate': 1.55,
            'active': 1.725,
            'very_active': 1.9
        }
        daily_calories = bmr * activity_multipliers.get(activity_level, 1.2)
        return {
            'bmr': round(bmr, 2),
            'daily_calories': round(daily_calories, 2),
            'protein_grams': round(weight * 0.8, 2),
            'carbs_grams': round(daily_calories * 0.45 / 4, 2),
            'fat_grams': round(daily_calories * 0.25 / 9, 2)
        }

    @staticmethod
    def calculate_meal_nutrition(meal_items):
        """食事全体の栄養価を計算"""
        total_nutrition = {
            'calories': 0,
            'protein': 0,
            'carbs': 0,
            'fat': 0
        }

        for item in meal_items:
            food = item['food']
            weight = item['weight']
            nutrition = food.calculate_nutrition(weight)

            for key in total_nutrition:
                total_nutrition[key] += nutrition[key]

        return total_nutrition

class NutritionService:
    def __init__(self, db_manager=None):
        self.db_manager = db_manager

    def search_food(self, query):
        if not query:
            raise ValueError("検索クエリを入力してください")
        mock_results = [
            {'name': 'Apple', 'id': 1, 'calories_per_100g': 52},
            {'name': 'Banana', 'id': 2, 'calories_per_100g': 89},
            {'name': 'Rice', 'id': 3, 'calories_per_100g': 130}
        ]
        return [item for item in mock_results if query.lower() in item['name'].lower()]

    def get_food_details(self, food_id):
        if not isinstance(food_id, int) or food_id <= 0:
            raise ValueError("食品IDは正の整数で入力してください")
        food_database = {
            1: FoodNutrition("Apple", 52, protein=0.3, carbs=14, fat=0.2),
            2: FoodNutrition("Banana", 89, protein=1.1, carbs=23, fat=0.3),
            3: FoodNutrition("Rice", 130, protein=2.7, carbs=28, fat=0.3)
        }
        return food_database.get(food_id)

# -------------------------
# 共通フィクスチャ
# -------------------------
@pytest.fixture
def sample_food():
    return FoodNutrition("Apple", 52, protein=0.3, carbs=14, fat=0.2)

@pytest.fixture
def nutrition_calculator():
    return NutritionCalculator()

@pytest.fixture
def nutrition_service():
    return NutritionService()

@pytest.fixture
def sample_meal():
    apple = FoodNutrition("Apple", 52, protein=0.3, carbs=14, fat=0.2)
    banana = FoodNutrition("Banana", 89, protein=1.1, carbs=23, fat=0.3)
    return [
        {"food": apple, "weight": 150},
        {"food": banana, "weight": 120}
    ]

# -------------------------
# テスト
# -------------------------
class TestFoodNutritionErrors:
    def test_negative_weight_error(self, sample_food):
        with pytest.raises(ValueError, match="重量は0以上で入力してください"):
            sample_food.calculate_nutrition(-100)

class TestNutritionCalculatorErrors:
    def test_negative_age_error(self, nutrition_calculator):
        with pytest.raises(ValueError, match="年齢は正の整数で入力してください"):
            nutrition_calculator.calculate_daily_needs(-5, "male", 70, 175, "moderate")

    def test_zero_weight_error(self, nutrition_calculator):
        with pytest.raises(ValueError, match="体重は1kg以上で入力してください"):
            nutrition_calculator.calculate_daily_needs(30, "male", 0, 175, "active")

    def test_invalid_height_error(self, nutrition_calculator):
        with pytest.raises(ValueError, match="身長は正の数値で入力してください"):
            nutrition_calculator.calculate_daily_needs(30, "male", 70, 0, "active")

    def test_invalid_gender_error(self, nutrition_calculator):
        with pytest.raises(ValueError, match="性別は male または female を指定してください"):
            nutrition_calculator.calculate_daily_needs(30, "other", 70, 175, "active")

    def test_calculate_meal_nutrition(self, nutrition_calculator, sample_meal):
        total = nutrition_calculator.calculate_meal_nutrition(sample_meal)
        assert total['calories'] > 0
        assert total['protein'] > 0

# ---------------------------
# エラーハンドリング
# ---------------------------
class TestNutritionServiceErrors:
    def test_empty_query_error(self, nutrition_service):
        with pytest.raises(ValueError, match="検索クエリを入力してください"):
            nutrition_service.search_food("")

    def test_none_query_error(self, nutrition_service):
        with pytest.raises(ValueError, match="検索クエリを入力してください"):
            nutrition_service.search_food(None)

    def test_invalid_food_id_type(self, nutrition_service):
        with pytest.raises(ValueError, match="食品IDは正の整数で入力してください"):
            nutrition_service.get_food_details("abc")

    def test_invalid_food_id_negative(self, nutrition_service):
        with pytest.raises(ValueError, match="食品IDは正の整数で入力してください"):
            nutrition_service.get_food_details(-1)

class TestNutritionAPIErrorHandling:
    @patch('requests.get')
    def test_invalid_json_response(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = Exception("不正なJSONレスポンス")
        mock_get.return_value = mock_response

        def fetch_nutrition_data(food_name):
            response = requests.get(f"https://api.fake.com?q={food_name}")
            if response.status_code == 200:
                return response.json()
            return None

        with pytest.raises(Exception, match="不正なJSONレスポンス"):
            fetch_nutrition_data("apple")
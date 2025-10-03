"""ヘルパー関数のテスト"""

import pytest
from datetime import datetime

from src.utils.helpers import (
    calculate_bmi, calculate_bmr, calculate_tdee,
    calculate_macros, format_date_jp, get_bmi_category
)

# -------------------------
# BMI 関連
# -------------------------
class TestBMIHelpers:
    """BMI 関連関数のテスト"""
    @pytest.mark.parametrize("bmi, expected_category, expected_emoji", [
        (17.0, "低体重", "🔵"),
        (22.0, "標準", "🟢"),
        (27.0, "やや肥満", "🟡"),
        (32.0, "肥満", "🔴"),
    ])
    def test_get_bmi_category_returns_expected_category(
        self, bmi: float, expected_category: str, expected_emoji: str
    ):
        """BMI 値から正しいカテゴリーと絵文字を返す"""
        category, emoji = get_bmi_category(bmi)
        assert category == expected_category
        assert emoji == expected_emoji

    @pytest.mark.parametrize("bmi, expected_category", [
        (18.4, "低体重"),
        (18.5, "標準"),
        (24.9, "標準"),
        (25.0, "やや肥満"),
    ])
    def test_get_bmi_category_boundary_values(
        self, bmi: float, expected_category: str
    ):
        """境界値で正しいカテゴリーを返す"""
        category, _ = get_bmi_category(bmi)
        assert category == expected_category
    
    def test_calculate_bmi_normal_values(self):
        """正常値でのBMI計算"""
        bmi = calculate_bmi(175.0, 70.0)  # 175cm, 70kg
        expected = 70.0 / (1.75 ** 2)
        assert abs(bmi - expected) < 0.01
    
    def test_calculate_bmi_edge_cases(self):
        """極端な値でも正のBMIを返す"""
        assert calculate_bmi(150.0, 40.0) > 0
        assert calculate_bmi(200.0, 100.0) > 0

# -------------------------
# 日付フォーマット
# -------------------------
class TestDateFormatHelpers:
    """日付フォーマットのテスト"""

    def test_format_date_jp_returns_correct_string(self):
        """日本語フォーマットに変換できる"""
        assert format_date_jp(datetime(2025, 1, 15)) == "2025年01月15日"
        assert format_date_jp(datetime(2024, 12, 3)) == "2024年12月03日"


# -------------------------
# BMR 関連
# -------------------------
class TestBMRHelpers:
    """基礎代謝量 (BMR) のテスト"""

    def test_bmr_for_male_matches_formula(self):
        """男性のBMRが Harris-Benedict の式と一致する"""
        bmr = calculate_bmr(175.0, 70.0, 30, "男性")
        expected = 88.362 + (13.397 * 70.0) + (4.799 * 175.0) - (5.677 * 30)
        assert abs(bmr - expected) < 0.01
    
    def test_bmr_for_female_matches_formula(self):
        """女性のBMRが Harris-Benedict の式と一致する"""
        bmr = calculate_bmr(160.0, 55.0, 25, "女性")
        expected = 447.593 + (9.247 * 55.0) + (3.098 * 160.0) - (4.330 * 25)
        assert abs(bmr - expected) < 0.01
    
    def test_bmr_gender_difference(self):
        """同条件では男性のBMRが女性より高い"""
        bmr_male = calculate_bmr(170.0, 65.0, 30, "男性")
        bmr_female = calculate_bmr(170.0, 65.0, 30, "女性")
        assert bmr_male > bmr_female

# -------------------------
# TDEE 関連
# -------------------------
class TestTDEEHelpers:
    """総消費エネルギー量 (TDEE) のテスト"""

    def test_tdee_increases_with_activity_level(self):
        """活動レベルが上がるとTDEEも増える"""
        bmr = 1600.0
        activity_levels = ["座りがち", "軽い運動", "適度な運動", "活発", "非常に活発"]
        previous_tdee = 0
        for level in activity_levels:
            current_tdee = calculate_tdee(bmr, level)
            assert current_tdee > previous_tdee
            previous_tdee = current_tdee
    
    def test_tdee_returns_default_for_unknown_level(self):
        """未知の活動レベルではデフォルト係数 (1.55) を使う"""
        bmr = 1500.0
        assert calculate_tdee(bmr, "未知の活動") == bmr * 1.55
    
    def test_tdee_values_match_expected_multipliers(self):
        """活動レベルごとの係数が正しい"""
        bmr = 1500.0
        assert calculate_tdee(bmr, "座りがち") == bmr * 1.2
        assert calculate_tdee(bmr, "軽い運動") == bmr * 1.375
        assert calculate_tdee(bmr, "適度な運動") == bmr * 1.55
        assert calculate_tdee(bmr, "活発") == bmr * 1.725
        assert calculate_tdee(bmr, "非常に活発") == bmr * 1.9


# -------------------------
# マクロ栄養素
# -------------------------
class TestMacroHelpers:
    """マクロ栄養素計算のテスト"""

    @pytest.mark.parametrize("goal, ratios", [
        ("減量", (0.30, 0.35, 0.35)),
        ("増量", (0.25, 0.45, 0.30)),
        ("体重維持", (0.20, 0.50, 0.30)),
    ])
    def test_calculate_macros_respects_ratios(self, goal: str, ratios: tuple[float, float, float]):
        """ゴールごとに正しい比率で計算される"""
        calories = 2000.0
        macros = calculate_macros(calories, goal)
        p_ratio = macros["protein"]["calories"] / calories
        c_ratio = macros["carbs"]["calories"] / calories
        f_ratio = macros["fat"]["calories"] / calories
        assert abs(p_ratio - ratios[0]) < 0.01
        assert abs(c_ratio - ratios[1]) < 0.01
        assert abs(f_ratio - ratios[2]) < 0.01
    
    def test_calculate_macros_total_calories_matches_input(self):
        """マクロ栄養素合計が入力カロリーと一致する"""
        for calories in [1500, 2000, 2500, 3000]:
            macros = calculate_macros(calories, "体重維持")
            total = sum(v["calories"] for v in macros.values())
            assert abs(total - calories) < 1.0
    
    def test_calculate_macros_returns_positive_values(self):
        """極端に低いカロリーでも正の値を返す"""
        macros = calculate_macros(800.0, "減量")
        assert macros["protein"]["grams"] > 0
        assert macros["carbs"]["grams"] > 0
        assert macros["fat"]["grams"] > 0
    
    def test_calculate_macros_extremely_high_calories(self):
        """極端に高いカロリーでも合計が一致する"""
        calories = 5000.0
        macros = calculate_macros(calories, "増量")
        total = sum(v["calories"] for v in macros.values())
        assert abs(total - calories) < 1.0

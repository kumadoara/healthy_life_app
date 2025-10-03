"""
HealthCalculator（栄養計算サービス）のテスト
"""

import pytest
from unittest.mock import MagicMock

from src.services.nutrition_cal import HealthCalculator
from src.models.user_profile import UserProfile


class TestHealthCalculatorBMI:
    """BMI計算関連のテスト"""

    def test_calculate_bmi_normal_range(self):
        """正常範囲のBMI計算"""
        # 身長175cm、体重70kgの場合（BMI=22.9）
        bmi = HealthCalculator.calculate_bmi(175, 70)
        assert bmi == 22.9

    def test_calculate_bmi_various_values(self):
        """様々な値でのBMI計算テスト"""
        test_cases = [
            (160, 50, 19.5),  # 普通体重
            (170, 80, 27.7),  # 肥満1度
            (180, 60, 18.5),  # 境界値
        ]

        for height, weight, expected in test_cases:
            result = HealthCalculator.calculate_bmi(height, weight)
            assert result == expected

    def test_get_bmi_category_classifications(self):
        """BMIカテゴリ分類のテスト"""
        test_cases = [
            (17.0, "低体重"),
            (20.0, "普通体重"),
            (27.0, "肥満（1度）"),
            (32.0, "肥満（2度）"),
            (37.0, "肥満（3度）"),
        ]

        for bmi, expected_category in test_cases:
            result = HealthCalculator.get_bmi_category(bmi)
            assert result == expected_category

    def test_get_bmi_category_boundary_values(self):
        """BMIカテゴリの境界値テスト"""
        boundary_cases = [
            (18.4, "低体重"),
            (18.5, "普通体重"),
            (24.9, "普通体重"),
            (25.0, "肥満（1度）"),
            (29.9, "肥満（1度）"),
            (30.0, "肥満（2度）"),
            (34.9, "肥満（2度）"),
            (35.0, "肥満（3度）"),
        ]

        for bmi, expected in boundary_cases:
            result = HealthCalculator.get_bmi_category(bmi)
            assert result == expected


class TestHealthCalculatorBMR:
    """BMR（基礎代謝率）計算のテスト"""

    @pytest.fixture
    def sample_male_profile(self):
        """男性プロフィールのサンプル"""
        return UserProfile(
            name="テスト男性",
            age=30,
            gender="男性",
            height=175.0,
            weight=70.0,
            activity_level="活発",
            goal="体重維持"
        )

    @pytest.fixture
    def sample_female_profile(self):
        """女性プロフィールのサンプル"""
        return UserProfile(
            name="テスト女性",
            age=25,
            gender="女性",
            height=160.0,
            weight=55.0,
            activity_level="適度な運動",
            goal="体重維持"
        )

    def test_calculate_bmr_male(self, sample_male_profile):
        """男性のBMR計算テスト"""
        bmr = HealthCalculator.calculate_bmr(sample_male_profile, "male")
        # BMR = 88.362 + (13.397 × 70) + (4.799 × 175) - (5.677 × 30)
        # BMR = 88.362 + 937.79 + 839.825 - 170.31 = 1695.667
        expected_bmr = round(88.362 + (13.397 * 70) + (4.799 * 175) - (5.677 * 30))
        assert bmr == expected_bmr

    def test_calculate_bmr_female(self, sample_female_profile):
        """女性のBMR計算テスト"""
        bmr = HealthCalculator.calculate_bmr(sample_female_profile, "female")
        # BMR = 447.593 + (9.247 × 55) + (3.098 × 160) - (4.330 × 25)
        expected_bmr = round(447.593 + (9.247 * 55) + (3.098 * 160) - (4.330 * 25))
        assert bmr == expected_bmr

    def test_calculate_bmr_edge_cases(self):
        """BMR計算の極端なケース"""
        # 高齢者のケース
        elderly_profile = UserProfile(
            name="高齢者",
            age=80,
            gender="男性",
            height=165.0,
            weight=60.0,
            activity_level="座りがち",
            goal="体重維持"
        )
        bmr = HealthCalculator.calculate_bmr(elderly_profile, "male")
        assert isinstance(bmr, int)
        assert bmr > 0

        # 若い人のケース
        young_profile = UserProfile(
            name="若者",
            age=18,
            gender="女性",
            height=155.0,
            weight=45.0,
            activity_level="非常に活発",
            goal="増量"
        )
        bmr = HealthCalculator.calculate_bmr(young_profile, "female")
        assert isinstance(bmr, int)
        assert bmr > 0


class TestHealthCalculatorCalories:
    """カロリー計算のテスト"""

    @pytest.fixture
    def base_profile(self):
        return UserProfile(
            name="基本ユーザー",
            age=30,
            gender="男性",
            height=175.0,
            weight=70.0,
            activity_level="適度な運動",
            goal="体重維持"
        )

    def test_calculate_daily_calories_various_activity_levels(self, base_profile):
        """様々な活動レベルでの日消費カロリー計算"""
        activity_levels = [
            ("座りがち", 1.2),
            ("軽い運動", 1.375),
            ("適度な運動", 1.55),
            ("活発", 1.725),
            ("非常に活発", 1.9),
        ]

        for activity, multiplier in activity_levels:
            profile = base_profile.model_copy()
            profile.activity_level = activity

            daily_calories = HealthCalculator.calculate_daily_calories(profile, "male")
            bmr = HealthCalculator.calculate_bmr(profile, "male")
            expected = round(bmr * multiplier)

            assert daily_calories == expected

    def test_calculate_daily_calories_unknown_activity_level(self, base_profile):
        """未知の活動レベルでのデフォルト処理"""
        profile = base_profile.model_copy()
        profile.activity_level = "unknown"

        daily_calories = HealthCalculator.calculate_daily_calories(profile, "male")
        bmr = HealthCalculator.calculate_bmr(profile, "male")
        expected = round(bmr * 1.725)  # デフォルト値

        assert daily_calories == expected

    def test_calculate_target_calories_various_goals(self):
        """様々な目標での推奨カロリー計算"""
        base_calories = 2000

        test_cases = [
            ("減量", base_calories - 300),
            ("増量", base_calories + 300),
            ("体重維持", base_calories),
            ("unknown", base_calories),  # デフォルト処理
        ]

        for goal, expected in test_cases:
            result = HealthCalculator.calculate_target_calories(base_calories, goal)
            assert result == expected


class TestHealthCalculatorProtein:
    """タンパク質必要量計算のテスト"""

    def test_calculate_protein_requirement_gain_goal(self):
        """増量目標のタンパク質必要量"""
        protein = HealthCalculator.calculate_protein_requirement(70, "増量", "適度な運動")
        expected = round(70 * 2.0)  # 増量: 2.0g/kg
        assert protein == expected

    def test_calculate_protein_requirement_lose_goal(self):
        """減量目標のタンパク質必要量"""
        protein = HealthCalculator.calculate_protein_requirement(60, "減量", "軽い運動")
        expected = round(60 * 1.8)  # 減量: 1.8g/kg
        assert protein == expected

    def test_calculate_protein_requirement_maintain_goal(self):
        """維持目標のタンパク質必要量"""
        protein = HealthCalculator.calculate_protein_requirement(65, "体重維持", "適度な運動")
        expected = round(65 * 1.4)  # 維持: 1.4g/kg
        assert protein == expected

    def test_calculate_protein_requirement_high_activity(self):
        """高活動レベルのタンパク質必要量"""
        # 維持目標でも高活動なら2.0g/kg
        protein = HealthCalculator.calculate_protein_requirement(70, "体重維持", "非常に活発")
        expected = round(70 * 2.0)
        assert protein == expected

        protein_active = HealthCalculator.calculate_protein_requirement(70, "体重維持", "活発")
        expected_active = round(70 * 2.0)
        assert protein_active == expected_active


class TestHealthCalculatorMacronutrients:
    """マクロ栄養素計算のテスト"""

    def test_calculate_macronutrients_standard_calories(self):
        """標準的なカロリーでのマクロ栄養素配分"""
        total_calories = 2000
        macros = HealthCalculator.calculate_macronutrients(total_calories)

        # 炭水化物: 50% (4kcal/g)
        expected_carbs = round(2000 * 0.5 / 4)
        # タンパク質: 20% (4kcal/g)
        expected_protein = round(2000 * 0.2 / 4)
        # 脂質: 30% (9kcal/g)
        expected_fat = round(2000 * 0.3 / 9)

        assert macros["carbs"] == expected_carbs
        assert macros["protein"] == expected_protein
        assert macros["fat"] == expected_fat

    def test_calculate_macronutrients_various_calories(self):
        """様々なカロリーでのマクロ栄養素計算"""
        test_calories = [1200, 1800, 2500, 3000]

        for calories in test_calories:
            macros = HealthCalculator.calculate_macronutrients(calories)

            # 各マクロが正の整数であることを確認
            assert isinstance(macros["carbs"], int)
            assert isinstance(macros["protein"], int)
            assert isinstance(macros["fat"], int)
            assert macros["carbs"] > 0
            assert macros["protein"] > 0
            assert macros["fat"] > 0


class TestHealthCalculatorComprehensive:
    """総合的な健康統計計算のテスト"""

    @pytest.fixture
    def comprehensive_profile(self):
        return UserProfile(
            name="総合テストユーザー",
            age=28,
            gender="女性",
            height=165.0,
            weight=58.0,
            activity_level="活発",
            goal="減量"
        )

    def test_get_health_stats_complete(self, comprehensive_profile):
        """総合健康統計の完全テスト"""
        stats = HealthCalculator.get_health_stats(comprehensive_profile, "female")

        # 全ての必要なキーが存在することを確認
        required_keys = [
            "bmi", "bmi_category", "bmr", "daily_calories",
            "target_calories", "protein_requirement", "macronutrients"
        ]
        for key in required_keys:
            assert key in stats

        # BMI計算の確認
        expected_bmi = HealthCalculator.calculate_bmi(
            comprehensive_profile.height, comprehensive_profile.weight
        )
        assert stats["bmi"] == expected_bmi

        # BMIカテゴリの確認
        expected_category = HealthCalculator.get_bmi_category(expected_bmi)
        assert stats["bmi_category"] == expected_category

        # マクロ栄養素が辞書形式であることを確認
        assert isinstance(stats["macronutrients"], dict)
        assert "carbs" in stats["macronutrients"]
        assert "protein" in stats["macronutrients"]
        assert "fat" in stats["macronutrients"]

    def test_get_health_stats_consistency(self, comprehensive_profile):
        """健康統計の一貫性テスト"""
        stats = HealthCalculator.get_health_stats(comprehensive_profile, "female")

        # 個別計算と総合計算の結果が一致することを確認
        individual_bmr = HealthCalculator.calculate_bmr(comprehensive_profile, "female")
        assert stats["bmr"] == individual_bmr

        individual_daily = HealthCalculator.calculate_daily_calories(comprehensive_profile, "female")
        assert stats["daily_calories"] == individual_daily

        individual_target = HealthCalculator.calculate_target_calories(
            individual_daily, comprehensive_profile.goal
        )
        assert stats["target_calories"] == individual_target


class TestHealthCalculatorIdealWeight:
    """理想体重計算のテスト"""

    def test_calculate_ideal_weight_range_standard_heights(self):
        """標準的な身長での理想体重範囲計算"""
        test_cases = [
            (160, 18.5 * (1.6 ** 2), 24.9 * (1.6 ** 2)),
            (170, 18.5 * (1.7 ** 2), 24.9 * (1.7 ** 2)),
            (180, 18.5 * (1.8 ** 2), 24.9 * (1.8 ** 2)),
        ]

        for height, expected_min, expected_max in test_cases:
            min_weight, max_weight = HealthCalculator.calculate_ideal_weight_range(height)
            assert min_weight == round(expected_min)
            assert max_weight == round(expected_max)

    def test_calculate_ideal_weight_range_extreme_heights(self):
        """極端な身長での理想体重範囲計算"""
        # 低身長
        min_w, max_w = HealthCalculator.calculate_ideal_weight_range(150)
        assert min_w > 0
        assert max_w > min_w

        # 高身長
        min_w, max_w = HealthCalculator.calculate_ideal_weight_range(200)
        assert min_w > 0
        assert max_w > min_w


class TestHealthCalculatorExerciseCalories:
    """運動消費カロリー計算のテスト"""

    def test_estimate_calories_burned_known_exercises(self):
        """既知の運動での消費カロリー計算"""
        weight = 70  # kg
        duration = 60  # 分

        test_cases = [
            ("ウォーキング", 3.5),
            ("ランニング", 8.0),
            ("筋トレ", 4.0),
            ("水泳", 8.0),
            ("ヨガ", 2.5),
        ]

        for exercise, expected_met in test_cases:
            calories = HealthCalculator.estimate_calories_burned(exercise, weight, duration)
            expected_calories = round(expected_met * weight * (duration / 60))
            assert calories == expected_calories

    def test_estimate_calories_burned_unknown_exercise(self):
        """未知の運動でのデフォルト処理"""
        calories = HealthCalculator.estimate_calories_burned("未知の運動", 70, 60)
        # デフォルトMET値4.0を使用
        expected = round(4.0 * 70 * 1.0)
        assert calories == expected

    def test_estimate_calories_burned_various_durations(self):
        """様々な時間での消費カロリー計算"""
        weight = 60
        exercise = "ランニング"  # MET = 8.0

        test_durations = [30, 45, 90, 120]
        for duration in test_durations:
            calories = HealthCalculator.estimate_calories_burned(exercise, weight, duration)
            expected = round(8.0 * weight * (duration / 60))
            assert calories == expected

    def test_estimate_calories_burned_various_weights(self):
        """様々な体重での消費カロリー計算"""
        exercise = "サイクリング"  # MET = 7.5
        duration = 60

        test_weights = [50, 65, 80, 95]
        for weight in test_weights:
            calories = HealthCalculator.estimate_calories_burned(exercise, weight, duration)
            expected = round(7.5 * weight * 1.0)
            assert calories == expected


class TestHealthCalculatorErrorHandling:
    """エラーハンドリングのテスト"""

    def test_calculate_bmi_zero_height(self):
        """身長0での除算エラーテスト"""
        with pytest.raises(ZeroDivisionError):
            HealthCalculator.calculate_bmi(0, 70)

    def test_calculate_bmr_with_mock_profile(self):
        """不正なプロフィールでのBMR計算テスト"""
        mock_profile = MagicMock()
        mock_profile.weight = 70.0
        mock_profile.height = 175.0
        mock_profile.age = 30

        # 正常に計算できることを確認
        bmr = HealthCalculator.calculate_bmr(mock_profile, "male")
        assert isinstance(bmr, int)
        assert bmr > 0

    def test_activity_multipliers_completeness(self):
        """活動レベル倍数の完全性テスト"""
        expected_levels = ["座りがち", "軽い運動", "適度な運動", "活発", "非常に活発"]

        for level in expected_levels:
            assert level in HealthCalculator.ACTIVITY_MULTIPLIERS
            assert isinstance(HealthCalculator.ACTIVITY_MULTIPLIERS[level], (int, float))
            assert HealthCalculator.ACTIVITY_MULTIPLIERS[level] > 0


class TestHealthCalculatorEdgeCases:
    """エッジケースのテスト"""

    def test_extreme_bmi_values(self):
        """極端なBMI値のテスト"""
        # 非常に低いBMI
        low_bmi = HealthCalculator.calculate_bmi(200, 50)
        assert HealthCalculator.get_bmi_category(low_bmi) == "低体重"

        # 非常に高いBMI
        high_bmi = HealthCalculator.calculate_bmi(150, 120)
        assert HealthCalculator.get_bmi_category(high_bmi) == "肥満（3度）"

    def test_zero_weight_protein_calculation(self):
        """体重0でのタンパク質計算"""
        protein = HealthCalculator.calculate_protein_requirement(0, "maintain", "moderate")
        assert protein == 0

    def test_zero_calories_macronutrient_calculation(self):
        """0カロリーでのマクロ栄養素計算"""
        macros = HealthCalculator.calculate_macronutrients(0)
        assert macros["carbs"] == 0
        assert macros["protein"] == 0
        assert macros["fat"] == 0

    def test_negative_duration_exercise_calories(self):
        """負の時間での運動消費カロリー"""
        calories = HealthCalculator.estimate_calories_burned("ランニング", 70, -30)
        # 負の結果が返されることを確認
        assert calories < 0


class TestHealthCalculatorIntegration:
    """統合テスト"""

    def test_full_health_calculation_workflow(self):
        """完全な健康計算ワークフローのテスト"""
        # 完全なユーザープロフィールを作成
        profile = UserProfile(
            name="統合テストユーザー",
            age=35,
            gender="男性",
            height=180.0,
            weight=75.0,
            activity_level="活発",
            goal="減量"
        )

        # 全ての計算を実行
        stats = HealthCalculator.get_health_stats(profile, "male")
        ideal_weight = HealthCalculator.calculate_ideal_weight_range(profile.height)
        exercise_calories = HealthCalculator.estimate_calories_burned(
            "ランニング", profile.weight, 45
        )

        # 結果の妥当性を検証
        assert stats["bmi"] > 0
        assert stats["bmr"] > 0
        assert stats["daily_calories"] > stats["bmr"]
        assert stats["target_calories"] < stats["daily_calories"]  # 減量目標
        assert ideal_weight[0] < ideal_weight[1]
        assert exercise_calories > 0

        # 計算の一貫性を確認
        assert stats["target_calories"] == stats["daily_calories"] - 300  # 減量調整
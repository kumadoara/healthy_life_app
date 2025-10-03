"""マクロ栄養素計算機能のテスト"""

import pytest
from src.utils.helpers import calculate_macros

# ---------------------------
# Fixtures
# ---------------------------
@pytest.fixture
def goals():
    """サポートされている全ての目標"""
    return ["減量", "増量", "筋肉増強", "体重維持", "健康維持"]

@pytest.fixture
def default_calories():
    """標準テスト用のカロリー値"""
    return 2000.0

# ---------------------------
# ゴール別マクロ比率テスト
# ---------------------------
@pytest.mark.parametrize(
    "goal, expected_ratios",
    [
        ("減量", {"protein": 0.30, "carbs": 0.35, "fat": 0.35}),
        ("増量", {"protein": 0.25, "carbs": 0.45, "fat": 0.30}),
        ("筋肉増強", {"protein": 0.25, "carbs": 0.45, "fat": 0.30}),
        ("体重維持", {"protein": 0.20, "carbs": 0.50, "fat": 0.30}),
        ("健康維持", {"protein": 0.20, "carbs": 0.50, "fat": 0.30}),
    ],
)
def test_macro_ratios(default_calories, goal, expected_ratios):
    macros = calculate_macros(default_calories, goal)
    for macro, ratio in expected_ratios.items():
        assert macros[macro]["calories"] / default_calories == pytest.approx(ratio, rel=1e-2)

# ---------------------------
# グラム数・カロリー一貫性
# ---------------------------
@pytest.mark.parametrize("calories,goal", [(1800.0, "減量"), (2400.0, "体重維持"), (3000.0, "増量")])
def test_macro_calories_consistency(calories, goal):
    macros = calculate_macros(calories, goal)
    total_calories = sum(v["calories"] for v in macros.values())
    assert total_calories == pytest.approx(calories, rel=1e-3)
    # グラム数とカロリーの一貫性
    assert macros["protein"]["calories"] == pytest.approx(macros["protein"]["grams"] * 4, rel=1e-3)
    assert macros["carbs"]["calories"] == pytest.approx(macros["carbs"]["grams"] * 4, rel=1e-3)
    assert macros["fat"]["calories"] == pytest.approx(macros["fat"]["grams"] * 9, rel=1e-3)

# ---------------------------
# 境界値テスト
# ---------------------------
def test_boundary_values():
    """境界値テスト - ゼロカロリー"""
    macros = calculate_macros(0.0, "体重維持")
    assert all(v["grams"] == 0.0 and v["calories"] == 0.0 for v in macros.values())

def test_unknown_goal(default_calories):
    """未知の目標は維持の比率を使う"""
    macros = calculate_macros(default_calories, "未知の目標")
    assert macros["protein"]["calories"] / default_calories == pytest.approx(0.20, rel=1e-2)
    assert macros["carbs"]["calories"] / default_calories == pytest.approx(0.50, rel=1e-2)
    assert macros["fat"]["calories"] / default_calories == pytest.approx(0.30, rel=1e-2)

# ---------------------------
# 異常系テスト
# ---------------------------
def test_calories_invalid_type():
    """カロリーが数値でない場合エラー"""
    with pytest.raises(TypeError, match="カロリーは数値で入力してください"):
        calculate_macros("2000", "減量")

@pytest.mark.parametrize("calories", [-5000, -1e6])
def test_calories_negative(calories):
    """負のカロリーはエラー"""
    with pytest.raises(ValueError, match="カロリーは正の数値で入力してください"):
        calculate_macros(calories, "体重維持")

def test_goal_invalid_type(default_calories):
    """ゴールが文字列以外ならエラー"""
    with pytest.raises(TypeError, match="目標は文字列で指定してください"):
        calculate_macros(default_calories, 12345)

def test_goal_empty_string(default_calories):
    """空文字のゴールはエラー"""
    with pytest.raises(ValueError, match="目標は空文字では指定できません"):
        calculate_macros(default_calories, "")

def test_calories_overflow():
    """極端に大きなカロリーでも計算可能"""
    # Pythonの浮動小数点は非常に大きな値まで対応するため、
    # 実際的には1e308レベルでもOverflowErrorは発生しない
    import math
    macros = calculate_macros(1e6, "減量")
    # 全ての値が有限数であることを確認
    for macro_data in macros.values():
        assert math.isfinite(macro_data["calories"])
        assert math.isfinite(macro_data["grams"])
        
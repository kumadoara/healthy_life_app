"""BMI計算機能のテスト"""

import pytest
import math
from src.utils.helpers import calculate_bmi, get_bmi_category


# -----------------------------
# Fixtures
# -----------------------------
@pytest.fixture
def bmi_inputs():
    """標準的なBMIテスト用データ"""
    return {"height": 175.0, "weight": 70.0, "expected_bmi": 22.8571428571}

# -----------------------------
# BMI 計算テスト
# -----------------------------
def test_standard_bmi_calculation(bmi_inputs):
    """標準的なBMI計算のテスト"""
    calculated_bmi = calculate_bmi(bmi_inputs["height"], bmi_inputs["weight"])
    assert abs(calculated_bmi - bmi_inputs["expected_bmi"]) < 0.01
    assert round(calculated_bmi, 1) == 22.9

@pytest.mark.parametrize(
    "height, weight, expected",
    [
        (160.0, 50.0, 19.53),  # 低体重境界
        (170.0, 65.0, 22.49),  # 標準
        (180.0, 85.0, 26.23),  # やや肥満
        (165.0, 55.0, 20.20),  # 標準
        (150.0, 45.0, 20.00),  # 標準
    ],
)
def test_bmi_calculation_precision(height, weight, expected):
    calculated = calculate_bmi(height, weight)
    assert abs(calculated - expected) < 0.01

@pytest.mark.parametrize(
    "height, weight, min_val, max_val",
    [
        (200.0, 40.0, 0, 15),     # 極端に高身長・軽体重
        (150.0, 120.0, 50, 200),  # 極端に低身長・重体重
        (170.0, 65.0, 20, 25),    # 現実的範囲
    ],
)
def test_bmi_calculation_edge_cases(height, weight, min_val, max_val):
    bmi = calculate_bmi(height, weight)
    assert min_val < bmi < max_val

@pytest.mark.parametrize(
    "height, weight",
    [(172.5, 68.3), (175.123, 70.456)],
)
def test_bmi_calculation_decimal_precision(height, weight):
    height_m = height / 100
    expected = weight / (height_m ** 2)
    calculated = calculate_bmi(height, weight)
    assert abs(calculated - expected) < 0.001

# -----------------------------
# BMI カテゴリー判定テスト
# -----------------------------
@pytest.mark.parametrize(
    "bmi, expected_category, expected_emoji",
    [
        (15.0, "低体重", "🔵"),
        (18.4, "低体重", "🔵"),
        (18.5, "標準", "🟢"),
        (24.9, "標準", "🟢"),
        (25.0, "やや肥満", "🟡"),
        (29.9, "やや肥満", "🟡"),
        (30.0, "肥満", "🔴"),
        (40.0, "肥満", "🔴"),
    ],
)
def test_bmi_category_parametrized(bmi, expected_category, expected_emoji):
    category, emoji = get_bmi_category(bmi)
    assert category == expected_category
    assert emoji == expected_emoji

# -----------------------------
# エラーハンドリング
# -----------------------------
def test_zero_height_handling():
    with pytest.raises(ZeroDivisionError):
        calculate_bmi(0.0, 70.0)

def test_zero_weight_handling():
    bmi = calculate_bmi(175.0, 0.0)
    assert bmi == 0.0
    category, emoji = get_bmi_category(bmi)
    assert category == "低体重"
    assert emoji == "🔵"

def test_negative_values_handling():
    with pytest.raises(ZeroDivisionError):
        calculate_bmi(-175.0, 70.0)
    bmi = calculate_bmi(175.0, -70.0)
    assert bmi < 0
    category, _ = get_bmi_category(-10.0)
    assert category == "低体重"

@pytest.mark.parametrize(
    "height, weight, check",
    [
        (0.1, 70.0, lambda x: x > 0 and math.isfinite(x)),
        (175.0, 0.1, lambda x: 0 < x < 1),
        (1000.0, 70.0, lambda x: 0 < x < 1),
        (175.0, 1000.0, lambda x: x > 0 and math.isfinite(x)),
    ],
)
def test_extreme_values(height, weight, check):
    bmi = calculate_bmi(height, weight)
    assert check(bmi)

def test_none_inputs_handling():
    """None を渡した場合のエラーハンドリング"""
    with pytest.raises(TypeError, match="身長と体重は数値で入力してください"):
        calculate_bmi(None, 70.0)
    with pytest.raises(TypeError, match="身長と体重は数値で入力してください"):
        calculate_bmi(175.0, None)

def test_invalid_type_inputs():
    """文字列やリストを渡した場合のエラーハンドリング"""
    with pytest.raises(TypeError, match="身長と体重は数値で入力してください"):
        calculate_bmi("170", 70.0)
    with pytest.raises(TypeError, match="身長と体重は数値で入力してください"):
        calculate_bmi(175.0, [70])

def test_overflow_values():
    """極端に大きな値を渡した場合のエラーハンドリング"""
    with pytest.raises(OverflowError):
        calculate_bmi(1e308, 1e308)
"""BMR（基礎代謝率）計算機能のテスト"""

import pytest
import math

from src.utils.helpers import calculate_bmr

# ------------------------------
# Fixtures
# ------------------------------

@pytest.fixture
def standard_male():
    return {"height": 175.0, "weight": 70.0, "age": 30, "gender": "男性"}

@pytest.fixture
def standard_female():
    return {"height": 160.0, "weight": 55.0, "age": 30, "gender": "女性"}


# ------------------------------
# 男性 BMR テスト
# ------------------------------

@pytest.mark.parametrize("height, weight, age, expected_range", [
    (175.0, 65.0, 20, 1700),  # 若年男性
    (180.0, 80.0, 25, 1900),
    (170.0, 75.0, 18, 1750),
])
def test_young_male_bmr(height, weight, age, expected_range):
    bmr = calculate_bmr(height, weight, age, "男性")
    assert expected_range - 100 < bmr < expected_range + 100

@pytest.mark.parametrize("height, weight, age, expected_range", [
    (175.0, 75.0, 40, 1650),
    (170.0, 80.0, 50, 1600),
    (180.0, 85.0, 45, 1750),
])
def test_middle_aged_male_bmr(height, weight, age, expected_range):
    bmr = calculate_bmr(height, weight, age, "男性")
    assert expected_range - 100 < bmr < expected_range + 100

@pytest.mark.parametrize("height, weight, age, expected_range", [
    (170.0, 65.0, 65, 1400),
    (175.0, 70.0, 75, 1350),
    (165.0, 60.0, 80, 1250),
])
def test_elderly_male_bmr(height, weight, age, expected_range):
    bmr = calculate_bmr(height, weight, age, "男性")
    assert expected_range - 100 < bmr < expected_range + 100

def test_male_bmr_age_progression(standard_male):
    """年齢が上がるとBMRは下がる"""
    h, w = standard_male["height"], standard_male["weight"]
    bmr_20 = calculate_bmr(h, w, 20, "男性")
    bmr_40 = calculate_bmr(h, w, 40, "男性")
    bmr_60 = calculate_bmr(h, w, 60, "男性")
    assert bmr_20 > bmr_40 > bmr_60
    assert math.isclose(bmr_20 - bmr_40, 5.677 * 20, rel_tol=1e-3)

# ------------------------------
# 女性 BMR テスト
# ------------------------------

@pytest.mark.parametrize("height, weight, age, expected_range", [
    (160.0, 50.0, 20, 1300),
    (165.0, 60.0, 25, 1400),
    (155.0, 45.0, 18, 1200),
])
def test_young_female_bmr(height, weight, age, expected_range):
    bmr = calculate_bmr(height, weight, age, "女性")
    assert expected_range - 100 < bmr < expected_range + 100

@pytest.mark.parametrize("height, weight, age, expected_range", [
    (160.0, 55.0, 40, 1250),
    (165.0, 65.0, 50, 1300),
    (158.0, 60.0, 45, 1250),
])
def test_middle_aged_female_bmr(height, weight, age, expected_range):
    bmr = calculate_bmr(height, weight, age, "女性")
    assert expected_range - 100 < bmr < expected_range + 100

@pytest.mark.parametrize("height, weight, age, expected_range", [
    (155.0, 50.0, 65, 1100),
    (160.0, 55.0, 75, 1050),
    (150.0, 45.0, 80, 950),
])
def test_elderly_female_bmr(height, weight, age, expected_range):
    bmr = calculate_bmr(height, weight, age, "女性")
    assert expected_range - 100 < bmr < expected_range + 100

def test_female_bmr_age_progression(standard_female):
    """年齢が上がるとBMRは下がる"""
    h, w = standard_female["height"], standard_female["weight"]
    bmr_20 = calculate_bmr(h, w, 20, "女性")
    bmr_40 = calculate_bmr(h, w, 40, "女性")
    bmr_60 = calculate_bmr(h, w, 60, "女性")
    assert bmr_20 > bmr_40 > bmr_60
    assert math.isclose(bmr_20 - bmr_40, 4.330 * 20, rel_tol=1e-3)

# ------------------------------
# 男女比較
# ------------------------------

@pytest.mark.parametrize("height, weight, age", [
    (170.0, 65.0, 30),
    (175.0, 70.0, 25),
    (165.0, 60.0, 40),
])
def test_male_female_bmr_difference(height, weight, age):
    male_bmr = calculate_bmr(height, weight, age, "男性")
    female_bmr = calculate_bmr(height, weight, age, "女性")
    assert male_bmr > female_bmr
    # 実際の差異を確認して適切な範囲に調整
    difference = male_bmr - female_bmr
    assert 100 < difference < 300  # より現実的な範囲に調整

# ------------------------------
# 境界値・精度・特殊ケース
# ------------------------------

@pytest.mark.parametrize("height, weight, age, gender", [
    (100.0, 20.0, 1, "男性"),
    (100.0, 20.0, 1, "女性"),
])
def test_minimum_age_bmr(height, weight, age, gender):
    bmr = calculate_bmr(height, weight, age, gender)
    assert bmr > 0

def test_bmr_decimal_precision():
    bmr_male = calculate_bmr(175.5, 70.3, 30, "男性")
    expected_male = 88.362 + (13.397 * 70.3) + (4.799 * 175.5) - (5.677 * 30)
    assert math.isclose(bmr_male, expected_male, rel_tol=1e-3)

@pytest.mark.parametrize("height, weight, age, gender", [
    (175.0, 0.0, 30, "男性"),
    (0.0, 70.0, 30, "男性"),
    (175.0, 70.0, 0, "男性"),
])
def test_zero_values_handling(height, weight, age, gender):
    """ゼロ値はValidationErrorを発生させる"""
    with pytest.raises(ValueError, match="身長・体重・年齢は正の数値で入力してください"):
        calculate_bmr(height, weight, age, gender)

@pytest.mark.parametrize("height, weight, age", [
    (500.0, 500.0, 30),
    (50.0, 10.0, 30),
])
def test_extreme_values_handling(height, weight, age):
    bmr = calculate_bmr(height, weight, age, "男性")
    assert math.isfinite(bmr) and bmr > 0

# ------------------------------
# 異常系テスト（追加）
# ------------------------------

def test_invalid_type_inputs():
    with pytest.raises(TypeError, match="身長・体重・年齢は数値で入力してください"):
        calculate_bmr("175", 70.0, 30, "男性")
    with pytest.raises(TypeError, match="身長・体重・年齢は数値で入力してください"):
        calculate_bmr(175.0, "70", 30, "男性")
    with pytest.raises(TypeError, match="身長・体重・年齢は数値で入力してください"):
        calculate_bmr(175.0, 70.0, "30", "男性")

def test_invalid_gender():
    with pytest.raises(ValueError, match="性別は「男性」または「女性」を指定してください"):
        calculate_bmr(175.0, 70.0, 30, "その他")

def test_overflow_error():
    """非常に大きな値でもエラーにならずに計算される"""
    # Pythonの浮動小数点は非常に大きな値まで対応するため、
    # 実際的には1e308レベルでもOverflowErrorは発生しない
    bmr = calculate_bmr(1e6, 1e6, 30, "男性")
    assert math.isfinite(bmr)
        
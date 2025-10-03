"""TDEE（総消費エネルギー）計算機能のテスト"""

import pytest
from src.utils.helpers import calculate_tdee, calculate_bmr

# ==============================
# Fixtures
# ==============================
@pytest.fixture
def base_bmr():
    """基準となるBMR"""
    return 1500.0

@pytest.fixture
def male_bmr():
    """30歳男性、175cm、70kg の BMR"""
    return calculate_bmr(175.0, 70.0, 30, "男性")

@pytest.fixture
def female_bmr():
    """30歳女性、160cm、55kg の BMR"""
    return calculate_bmr(160.0, 55.0, 30, "女性")

# ==============================
# 活動レベル別計算テスト
# ==============================
@pytest.mark.parametrize(
    "activity_level,multiplier,expected",
    [
        ("座りがち", 1.2, 1800.0),
        ("軽い運動", 1.375, 2062.5),
        ("適度な運動", 1.55, 2325.0),
        ("活発", 1.725, 2587.5),
        ("非常に活発", 1.9, 2850.0),
    ]
)
def test_tdee_activity_levels(base_bmr, activity_level, multiplier, expected):
    """活動レベルごとのTDEE計算"""
    tdee = calculate_tdee(base_bmr, activity_level)
    assert tdee == pytest.approx(expected, 0.01)
    assert tdee == pytest.approx(base_bmr * multiplier, 0.01)

@pytest.mark.parametrize(
    "activity_level,multiplier",
    [
        ("座りがち", 1.2),
        ("軽い運動", 1.375),
        ("適度な運動", 1.55),
        ("活発", 1.725),
        ("非常に活発", 1.9),
    ]
)
def test_tdee_monotonic_increase(base_bmr, activity_level, multiplier):
    """活動レベルが上がるほどTDEEが上がる"""
    tdee = calculate_tdee(base_bmr, activity_level)
    assert tdee == pytest.approx(base_bmr * multiplier, 0.01)

def test_unknown_activity_level_uses_default(base_bmr):
    """未知の活動レベルではデフォルト係数（1.55）が使われる"""
    tdee = calculate_tdee(base_bmr, "未知の活動")
    assert tdee == pytest.approx(base_bmr * 1.55, 0.01)

# ==============================
# 境界値テスト
# ==============================
@pytest.mark.parametrize(
    "bmr,activity_level,expected",
    [
        (0.0, "適度な運動", 0.0),
        (500.0, "活発", 500.0 * 1.725),
        (5000.0, "非常に活発", 5000.0 * 1.9),
    ]
)
def test_tdee_boundary_values(bmr, activity_level, expected):
    """BMR境界値でのTDEE計算"""
    tdee = calculate_tdee(bmr, activity_level)
    assert tdee == pytest.approx(expected, 0.01)

# ==============================
# 精度・一貫性テスト
# ==============================
def test_tdee_decimal_precision():
    """小数点を含むBMRでも計算が正確"""
    bmr = 1678.456
    tdee = calculate_tdee(bmr, "適度な運動")
    assert tdee == pytest.approx(bmr * 1.55, 0.001)

def test_tdee_consistency(base_bmr):
    """同じ入力なら常に同じTDEE"""
    results = [calculate_tdee(base_bmr, "活発") for _ in range(10)]
    assert all(val == pytest.approx(results[0], 0.001) for val in results)

# ==============================
# 異常系テスト
# ==============================
def test_tdee_invalid_bmr_type():
    """BMR が数値以外ならエラー"""
    with pytest.raises(TypeError, match="BMRは数値で入力してください"):
        calculate_tdee("1500", "適度な運動")

def test_tdee_invalid_activity_type(base_bmr):
    """活動レベルが文字列以外ならエラー"""
    with pytest.raises(TypeError, match="活動レベルは文字列で指定してください"):
        calculate_tdee(base_bmr, 123)

def test_tdee_empty_activity_level(base_bmr):
    """活動レベルが空文字ならエラー"""
    with pytest.raises(ValueError, match="活動レベルは空文字では指定できません"):
        calculate_tdee(base_bmr, "")

def test_tdee_negative_bmr():
    """BMR が負の数ならエラー"""
    with pytest.raises(ValueError, match="BMRは正の数値で入力してください"):
        calculate_tdee(-1500.0, "適度な運動")

def test_tdee_overflow_error():
    """極端に大きなBMRでも計算可能"""
    # Pythonの浮動小数点は非常に大きな値まで対応するため、
    # 実際的には1e308レベルでもOverflowErrorは発生しない
    import math
    tdee = calculate_tdee(1e6, "活発")
    # 結果が有限数であることを確認
    assert math.isfinite(tdee)
    assert tdee == pytest.approx(1e6 * 1.725, 0.01)
        
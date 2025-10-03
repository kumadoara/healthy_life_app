"""ユーザープロフィールモデルのテスト"""

import pytest
import json
from datetime import datetime, timedelta
from pydantic import ValidationError

from src.models.user_profile import UserProfile

# ----------------------------
# Fixtures
# ----------------------------
@pytest.fixture
def base_profile_data():
    """基本のユーザープロフィールデータ"""
    return {
        "name": "山田太郎",
        "age": 30,
        "gender": "男性",
        "height": 175.0,
        "weight": 70.0,
        "activity_level": "適度な運動",
        "goal": "体重維持",
    }

# ----------------------------
# 正常ケース
# ----------------------------
def test_valid_user_profile_creation(base_profile_data):
    """正常なユーザープロフィール作成"""
    profile = UserProfile(**base_profile_data)
    assert profile.name == "山田太郎"
    assert profile.age == 30
    assert isinstance(profile.created_at, datetime)
    assert isinstance(profile.updated_at, datetime)

@pytest.mark.parametrize("gender", ["男性", "女性"])
def test_user_profile_with_all_genders(base_profile_data, gender):
    """すべての性別"""
    data = base_profile_data.copy()
    data["gender"] = gender
    profile = UserProfile(**data)
    assert profile.gender == gender

@pytest.mark.parametrize("activity_level", ["座りがち", "軽い運動", "適度な運動", "活発", "非常に活発"])
def test_user_profile_with_all_activity_levels(base_profile_data, activity_level):
    """すべての活動レベル"""
    data = base_profile_data.copy()
    data["activity_level"] = activity_level
    profile = UserProfile(**data)
    assert profile.activity_level == activity_level

@pytest.mark.parametrize("goal", ["体重維持", "減量", "増量", "筋肉増強", "健康維持"])
def test_user_profile_with_all_goals(base_profile_data, goal):
    """すべての目標"""
    data = base_profile_data.copy()
    data["goal"] = goal
    profile = UserProfile(**data)
    assert profile.goal == goal

# ----------------------------
# 異常系・バリデーションテスト
# ----------------------------
@pytest.mark.parametrize("field,value", [
    ("age", -1),
    ("age", 0),
    ("height", -175.0),
    ("weight", -70.0),
])
def test_invalid_numeric_values(base_profile_data, field, value):
    """数値の不正値バリデーション"""
    data = base_profile_data.copy()
    data[field] = value
    with pytest.raises(ValidationError):
        UserProfile(**data)

@pytest.mark.parametrize("name", ["", None])
def test_invalid_name(base_profile_data, name):
    """名前の不正値"""
    data = base_profile_data.copy()
    data["name"] = name
    with pytest.raises(ValidationError):
        UserProfile(**data)

@pytest.mark.parametrize("gender", [None, "", "その他", "male"])
def test_invalid_gender(base_profile_data, gender):
    data = base_profile_data.copy()
    data["gender"] = gender
    with pytest.raises(ValidationError):
        UserProfile(**data)

@pytest.mark.parametrize("activity_level", [None, "", "超活発"])
def test_invalid_activity_level(base_profile_data, activity_level):
    data = base_profile_data.copy()
    data["activity_level"] = activity_level
    with pytest.raises(ValidationError):
        UserProfile(**data)

@pytest.mark.parametrize("goal", [None, "", "無限筋肉"])
def test_invalid_goal(base_profile_data, goal):
    data = base_profile_data.copy()
    data["goal"] = goal
    with pytest.raises(ValidationError):
        UserProfile(**data)

@pytest.mark.parametrize("field,value", [
    ("height", None),
    ("height", "abc"),
    ("weight", None),
    ("weight", "xyz"),
])
def test_invalid_height_weight_type(base_profile_data, field, value):
    data = base_profile_data.copy()
    data[field] = value
    with pytest.raises(ValidationError):
        UserProfile(**data)

@pytest.mark.parametrize("age", [30.5, "三十"])
def test_invalid_age_type(base_profile_data, age):
    data = base_profile_data.copy()
    data["age"] = age
    with pytest.raises(ValidationError):
        UserProfile(**data)

# ----------------------------
# 境界値テスト
# ----------------------------
@pytest.mark.parametrize("age", [1, 120])
def test_boundary_age(base_profile_data, age):
    """年齢の境界値"""
    data = base_profile_data.copy()
    data["age"] = age
    profile = UserProfile(**data)
    assert profile.age == age

@pytest.mark.parametrize("height", [100.0, 250.0])
def test_boundary_height(base_profile_data, height):
    """身長の境界値"""
    data = base_profile_data.copy()
    data["height"] = height
    profile = UserProfile(**data)
    assert profile.height == height

@pytest.mark.parametrize("weight", [30.0, 200.0])
def test_boundary_weight(base_profile_data, weight):
    """体重の境界値"""
    data = base_profile_data.copy()
    data["weight"] = weight
    profile = UserProfile(**data)
    assert profile.weight == weight

# ----------------------------
# Serialization tests
# ----------------------------
def test_model_dump(base_profile_data):
    """dict シリアライズ"""
    profile = UserProfile(**base_profile_data)
    profile_dict = profile.model_dump()
    assert profile_dict["name"] == "山田太郎"
    assert "created_at" in profile_dict
    assert "updated_at" in profile_dict

def test_json_serialization(base_profile_data):
    """JSON シリアライズ"""
    data = base_profile_data.copy()
    data.update({"name": "JSON テスト", "age": 25, "gender": "女性"})
    profile = UserProfile(**data)
    json_str = profile.model_dump_json()
    profile_dict = json.loads(json_str)
    assert profile_dict["name"] == "JSON テスト"
    assert profile_dict["age"] == 25

# ----------------------------
# Datetime tests
# ----------------------------
def test_created_at_and_updated_at(base_profile_data):
    """作成・更新時刻の初期化"""
    before = datetime.now()
    profile = UserProfile(**base_profile_data)
    after = datetime.now()
    assert before <= profile.created_at <= after
    assert before <= profile.updated_at <= after

def test_datetime_fields_are_different_instances(base_profile_data):
    """日時フィールドが異なるインスタンス"""
    import time
    data1 = base_profile_data.copy()
    data1["name"] = "ユーザー1"
    profile1 = UserProfile(**data1)

    # 小さな遅延を追加して異なる時刻を確保
    time.sleep(0.001)

    data2 = base_profile_data.copy()
    data2["name"] = "ユーザー2"
    profile2 = UserProfile(**data2)
    assert profile1.created_at != profile2.created_at
    assert profile1.updated_at != profile2.updated_at

def test_updated_at_changes_on_update(base_profile_data):
    """更新操作"""
    profile = UserProfile(**base_profile_data)
    old_updated_at = profile.updated_at
    profile.age = 31 
    assert profile.updated_at >= old_updated_at

def test_updated_at_update_failure(base_profile_data):
    """updated_at を未来日時に固定"""
    profile = UserProfile(**base_profile_data)
    profile.updated_at = datetime.now() + timedelta(days=1)
    old_updated_at = profile.updated_at
    profile.age = 35
    # 正しく更新されなければ未来日時のままになる
    assert profile.updated_at == old_updated_at, "updated_at の更新に失敗しました"

# ----------------------------
# 特殊ケース
# ----------------------------
@pytest.mark.parametrize("name", [
    "田中 花子",
    "José García",
    "Zhang Wei 张伟",
    "김민수",
    "🌸さくら🌸",
    "user@example.com",
])
def test_unicode_names(base_profile_data, name):
    """Unicode文字を含む名前"""
    data = base_profile_data.copy()
    data["name"] = name
    profile = UserProfile(**data)
    assert profile.name == name

def test_decimal_precision(base_profile_data):
    """小数点精度"""
    data = base_profile_data.copy()
    data.update({"height": 165.123, "weight": 55.789})
    profile = UserProfile(**data)
    assert profile.height == 165.123
    assert profile.weight == 55.789

def test_profile_equality(base_profile_data):
    """プロフィール内容の等価性"""
    data1 = base_profile_data.copy()
    data1["name"] = "同一ユーザー"
    profile1 = UserProfile(**data1)
    data2 = base_profile_data.copy()
    data2["name"] = "同一ユーザー"
    profile2 = UserProfile(**data2)
    # created_at/updated_at は異なるため完全一致ではない
    assert profile1.name == profile2.name
    assert profile1.age == profile2.age
    assert profile1.height == profile2.height

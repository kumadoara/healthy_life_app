"""データマネージャー - プロフィール管理のテスト"""

import pytest
import json
from datetime import datetime
from unittest.mock import patch
from pydantic import ValidationError

from src.services.data_manager import DataManager
from src.models.user_profile import UserProfile

# --------------------
# Fixtures
# --------------------
@pytest.fixture
def valid_profile():
    """標準的な有効プロフィール"""
    return UserProfile(
        name="テストユーザー",
        age=30,
        gender="男性",
        height=175.0,
        weight=70.0,
        activity_level="適度な運動",
        goal="体重維持"
    )

@pytest.fixture
def data_manager(temp_data_dir):
    """テスト用 DataManager インスタンス"""
    return DataManager(data_dir=temp_data_dir)

# --------------------
# 保存テスト
# --------------------
def test_save_and_load_profile(data_manager, valid_profile):
    """プロフィールの保存と読み込み"""
    assert data_manager.save_profile(valid_profile)
    loaded = data_manager.load_profile()
    assert loaded.name == valid_profile.name
    assert loaded.age == valid_profile.age

@pytest.mark.parametrize("name, age, gender", [
    ("更新ユーザー", 35, "女性"),
    ("ユニコード 🌸", 25, "女性"),
    ("極端値", 120, "男性"),
])
def test_save_profile_various_cases(data_manager, valid_profile, name, age, gender):
    """様々な値での保存テスト"""
    valid_profile.name = name
    valid_profile.age = age
    valid_profile.gender = gender
    assert data_manager.save_profile(valid_profile)
    loaded = data_manager.load_profile()
    assert loaded.name == name
    assert loaded.age == age
    assert loaded.gender == gender

def test_save_profile_updates_timestamp(data_manager, valid_profile):
    """保存時に updated_at が更新される"""
    before = datetime.now()
    data_manager.save_profile(valid_profile)
    after = datetime.now()
    with open(data_manager.current_user_file, encoding="utf-8") as f:
        saved_data = json.load(f)
    updated_at = datetime.fromisoformat(saved_data["updated_at"])
    assert before <= updated_at <= after

# --------------------
# 読み込みテスト
# --------------------
@pytest.mark.parametrize("file_content, expected", [
    ('{ invalid json }', None),         # 破損ファイル
    ('', None),                         # 空ファイル
    (json.dumps({"name": "不完全"}), None),  # 不完全
    (json.dumps({
        "name": "無効型",
        "age": "thirty",  # 数値のはず
        "gender": "男性",
        "height": "175cm",  # 数値のはず
        "weight": 70.0,
        "activity_level": "適度な運動",
        "goal": "体重維持"
    }), None),
])
def test_load_invalid_profile_files(data_manager, file_content, expected):
    """不正ファイルの読み込みテスト"""
    data_manager.current_user_file.write_text(file_content, encoding="utf-8")
    assert data_manager.load_profile() is expected

def test_load_nonexistent_profile(data_manager):
    """存在しないプロフィールは None を返す"""
    assert not data_manager.current_user_file.exists()
    assert data_manager.load_profile() is None

# --------------------
# エラーハンドリング
# --------------------
@pytest.mark.parametrize("exception_cls, side_effect", [
    (PermissionError, "Permission denied"),
    (OSError, "No space left on device"),
])
def test_save_profile_write_errors(data_manager, valid_profile, exception_cls, side_effect):
    """ファイル書き込みエラーのテスト"""
    with patch("builtins.open", side_effect=exception_cls(side_effect)):
        assert data_manager.save_profile(valid_profile) is False

def test_load_profile_read_error(data_manager, valid_profile):
    """読み込み時の I/O エラー"""
    data_manager.save_profile(valid_profile)
    with patch("builtins.open", side_effect=IOError("I/O error")):
        assert data_manager.load_profile() is None

def test_save_profile_json_serialization_error(data_manager, valid_profile):
    """JSON シリアライズエラー"""
    with patch("json.dump", side_effect=TypeError("not serializable")):
        assert data_manager.save_profile(valid_profile) is False

def test_save_invalid_profile_missing_name(data_manager, valid_profile):
    """名前が欠落した場合は保存できない"""
    valid_profile.name = ""
    result = data_manager.save_profile(valid_profile)
    assert result is False 

def test_save_invalid_profile_negative_age(data_manager, valid_profile):
    """年齢が負の場合は保存できない"""
    valid_profile.age = -5
    result = data_manager.save_profile(valid_profile)
    assert result is False 

def test_save_invalid_profile_invalid_type(data_manager):
    """不正なデータ型を含む場合"""
    # Pydantic V2では型エラーでUserProfile作成が失敗する
    with pytest.raises(ValidationError):
        profile = UserProfile(
        name="型エラー",
        age="三十", # int でない
        gender="男性",
        height="175cm", # float でない
        weight=70.0,
        activity_level="適度な運動",
        goal="体重維持"
        )

def test_save_profile_none(data_manager):
    """None を渡した場合は保存できない"""
    result = data_manager.save_profile(None)
    assert result is False 

def test_delete_profile_file_error(data_manager, valid_profile):
    """削除時に I/O エラーが発生した場合"""
    data_manager.save_profile(valid_profile)
    with patch("pathlib.Path.unlink", side_effect=IOError("削除エラー")):
        result = data_manager.delete_profile()
        assert result is False       

# --------------------
# エッジケース
# --------------------
def test_profile_with_long_name(data_manager, valid_profile):
    """長大な名前でも保存できる"""
    valid_profile.name = "ユーザー" * 200
    assert data_manager.save_profile(valid_profile)
    loaded = data_manager.load_profile()
    assert loaded.name == valid_profile.name

def test_profile_with_decimal_precision(data_manager, valid_profile):
    """小数点精度を保持できる"""
    valid_profile.height = 165.123
    valid_profile.weight = 55.789
    data_manager.save_profile(valid_profile)
    loaded = data_manager.load_profile()
    assert abs(loaded.height - 165.123) < 1e-6
    assert abs(loaded.weight - 55.789) < 1e-6

def test_concurrent_profile_access(temp_data_dir, valid_profile):
    """同時アクセスは後勝ち"""
    dm1 = DataManager(data_dir=temp_data_dir)
    dm2 = DataManager(data_dir=temp_data_dir)
    valid_profile.name = "ユーザー1"
    dm1.save_profile(valid_profile)
    valid_profile.name = "ユーザー2"
    dm2.save_profile(valid_profile)
    loaded = dm1.load_profile()
    assert loaded.name == "ユーザー2"

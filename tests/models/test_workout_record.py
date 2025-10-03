"""ワークアウト記録モデルのテスト"""

import pytest
import json
from datetime import datetime, timedelta
from pydantic import ValidationError

from src.models.user_profile import WorkoutRecord

# ----------------------------
# Fixtures
# ----------------------------
@pytest.fixture
def base_workout_data():
    """基本のワークアウト記録データ"""
    return {
        "date": datetime(2025, 1, 15, 10, 30),
        "exercise": "ランニング",
        "duration": 30,
        "calories": 300,
        "intensity": "中",
    }

# ----------------------------
# 正常系テストケース
# ----------------------------
def test_valid_workout_record_creation(base_workout_data):
    """正常なワークアウト記録作成"""
    data = base_workout_data.copy()
    data["notes"] = "朝のジョギング"
    record = WorkoutRecord(**data)
    assert record.exercise == "ランニング"
    assert record.duration == 30
    assert record.calories == 300
    assert record.intensity == "中"
    assert record.notes == "朝のジョギング"

def test_workout_record_without_notes(base_workout_data):
    """メモなしで作成"""
    record = WorkoutRecord(**base_workout_data)
    assert record.notes is None

@pytest.mark.parametrize("exercise", [
    "ランニング", "ウォーキング", "筋トレ", "ヨガ", "水泳",
    "サイクリング", "テニス", "バスケットボール", "サッカー",
    "エアロビクス", "ピラティス", "ストレッチ", "なわとび"
])
def test_workout_record_with_various_exercises(base_workout_data, exercise):
    """様々な運動種目"""
    data = base_workout_data.copy()
    data["exercise"] = exercise
    record = WorkoutRecord(**data)
    assert record.exercise == exercise

@pytest.mark.parametrize("intensity", ["低", "中", "高"])
def test_workout_record_with_various_intensities(base_workout_data, intensity):
    """様々な強度"""
    data = base_workout_data.copy()
    data["intensity"] = intensity
    record = WorkoutRecord(**data)
    assert record.intensity == intensity

# ----------------------------
# 異常系
# ----------------------------
@pytest.mark.parametrize("field,value", [
    ("duration", -10),
    ("duration", 0),
    ("calories", -100),
])
def test_invalid_numeric_values(base_workout_data, field, value):
    """負やゼロの値はバリデーションエラー"""
    data = base_workout_data.copy()
    data[field] = value
    with pytest.raises(ValidationError):
        WorkoutRecord(**data)

def test_empty_exercise_validation(base_workout_data):
    """exerciseがブランク"""
    data = base_workout_data.copy()
    data["exercise"] = ""
    with pytest.raises(ValidationError):
        WorkoutRecord(**data)

def test_none_exercise_validation(base_workout_data):
    """exerciseがNone"""
    data = base_workout_data.copy()
    data["exercise"] = None
    with pytest.raises(ValidationError):
        WorkoutRecord(**data)

def test_numeric_exercise_invalid(base_workout_data):
    """exerciseが数値"""
    data = base_workout_data.copy()
    data["exercise"] = 12345
    with pytest.raises(ValidationError):
        WorkoutRecord(**data)

@pytest.mark.parametrize("field,value,error_msg", [
    ("duration", None, "時間は正の整数で入力してください"),
    ("duration", "abc", "時間は正の整数で入力してください"),
    ("duration", 10000, "時間が長すぎます"),
    ("calories", None, "消費カロリーは正の整数で入力してください"),
    ("calories", "xyz", "消費カロリーは正の整数で入力してください"),
    ("calories", 100000, "消費カロリーが大きすぎます"),
])
def test_invalid_numeric_fields(base_workout_data, field, value, error_msg):
    data = base_workout_data.copy()
    data[field] = value
    with pytest.raises(ValidationError):
        WorkoutRecord(**data)

def test_invalid_date_type(base_workout_data):
    """dateが文字列"""
    data = base_workout_data.copy()
    data["date"] = "2025-01-15"
    with pytest.raises(ValidationError):
        WorkoutRecord(**data)

def test_none_date(base_workout_data):
    """dateがNone"""
    data = base_workout_data.copy()
    data["date"] = None
    with pytest.raises(ValidationError):
        WorkoutRecord(**data)

def test_notes_too_long(base_workout_data):
    """文字数超過"""
    long_notes = "あ" * 2000
    data = base_workout_data.copy()
    data["notes"] = long_notes
    with pytest.raises(ValidationError):
        WorkoutRecord(**data)

def test_invalid_intensity_validation(base_workout_data):
    """無効な強度のバリデーションテスト"""
    data = base_workout_data.copy()
    data["intensity"] = "無効な強度"
    with pytest.raises(ValidationError, match="強度は「低」「中」「高」のいずれかで入力してください"):
        WorkoutRecord(**data)

# ----------------------------
# 境界値テスト
# ----------------------------
@pytest.mark.parametrize("duration", [1, 480])
def test_boundary_duration(base_workout_data, duration):
    """最小・最大妥当な時間"""
    data = base_workout_data.copy()
    data["duration"] = duration
    record = WorkoutRecord(**data)
    assert record.duration == duration

@pytest.mark.parametrize("calories", [0, 2000])
def test_boundary_calories(base_workout_data, calories):
    """最小・最大妥当なカロリー"""
    data = base_workout_data.copy()
    data["calories"] = calories
    record = WorkoutRecord(**data)
    assert record.calories == calories

# ----------------------------
# Serialization tests
# ----------------------------
def test_model_dump(base_workout_data):
    """dict シリアライズ"""
    record = WorkoutRecord(**base_workout_data, notes="テストメモ")
    record_dict = record.model_dump()
    assert record_dict["exercise"] == "ランニング"
    assert record_dict["notes"] == "テストメモ"
    assert "date" in record_dict

def test_json_serialization(base_workout_data):
    """JSON シリアライズ"""
    record = WorkoutRecord(**base_workout_data)
    json_str = record.model_dump_json()
    record_dict = json.loads(json_str)
    assert record_dict["exercise"] == "ランニング"
    assert record_dict["duration"] == 30

# ----------------------------
# Datetimeハンドリング
# ----------------------------
@pytest.mark.parametrize("date", [
    datetime.now() - timedelta(days=7),
    datetime.now() + timedelta(days=7),
    datetime(2025, 6, 15, 6, 30, 0),
])
def test_various_dates(base_workout_data, date):
    """過去・未来・特定時刻の日付"""
    data = base_workout_data.copy()
    data["date"] = date
    record = WorkoutRecord(**data)
    assert record.date == date

# ----------------------------
# フィールドテスト
# ----------------------------
@pytest.mark.parametrize("notes", [
    "",
    "これは比較的長いメモです。" * 10,  # 12文字 * 10 = 120文字（500文字以内）
    "天気が良くて気持ちよかった🌞",
    "Très bon entraînement aujourd'hui!",
    "今日는 정말 힘들었다",
    "心情: 😅💪🏃‍♂️",
    "距離: 5km, 温度: 25℃",
])
def test_various_notes(base_workout_data, notes):
    """様々なメモ（空・長文・Unicodeなど）"""
    data = base_workout_data.copy()
    data["notes"] = notes
    record = WorkoutRecord(**data)
    assert record.notes == notes

# ----------------------------
# 特殊ケース
# ----------------------------
@pytest.mark.parametrize("duration,calories", [
    (1, 5),       # 短いストレッチ
    (240, 2400),  # マラソン
])
def test_extreme_workouts(base_workout_data, duration, calories):
    """非常に短い/長いワークアウト"""
    data = base_workout_data.copy()
    data["duration"] = duration
    data["calories"] = calories
    record = WorkoutRecord(**data)
    assert record.duration == duration
    assert record.calories == calories

def test_exercise_name_with_numbers(base_workout_data):
    """数字を含む運動名"""
    exercises = ["5km ランニング", "30分 ヨガ", "100回 腕立て伏せ", "10セット スクワット"]
    for exercise in exercises:
        data = base_workout_data.copy()
        data["exercise"] = exercise
        record = WorkoutRecord(**data)
        assert record.exercise == exercise

def test_workout_record_comparison(base_workout_data):
    """異なる日付のレコード比較"""
    date1 = datetime(2025, 1, 15, 10, 0)
    date2 = datetime(2025, 1, 15, 11, 0)
    data1 = base_workout_data.copy()
    data1["date"] = date1
    record1 = WorkoutRecord(**data1)
    data2 = base_workout_data.copy()
    data2["date"] = date2
    record2 = WorkoutRecord(**data2)
    assert record1.date != record2.date
    assert record1.exercise == record2.exercise
    assert record1.duration == record2.duration
    assert record1.calories == record2.calories

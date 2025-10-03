"""データマネージャー - ワークアウト記録管理のテスト"""

import pytest
import json
from datetime import datetime, timedelta
from unittest.mock import patch

from src.services.data_manager import DataManager
from src.models.user_profile import WorkoutRecord

# ---------------------------
# Fixtures
# ---------------------------
@pytest.fixture
def dm(temp_data_dir):
    """テスト用 DataManager インスタンス"""
    return DataManager(data_dir=temp_data_dir)

@pytest.fixture
def workout_factory():
    """ワークアウトレコード生成用ファクトリ"""
    def _create_workout(
        date=None, exercise="ランニング", duration=30, calories=200, intensity="中", notes=None
    ):
        return WorkoutRecord(
            date=date or datetime.now(),
            exercise=exercise,
            duration=duration,
            calories=calories,
            intensity=intensity,
            notes=notes,
        )
    return _create_workout

# ---------------------------
# 保存テスト
# ---------------------------
def test_save_single_workout(dm, workout_factory):
    workout = workout_factory(exercise="ジョギング", calories=300)
    result = dm.save_workout(workout)
    assert result is True
    assert (dm.data_dir / "workouts.json").exists()

@pytest.mark.parametrize("exercise, duration, calories", [
    ("ランニング", 30, 300),
    ("筋トレ", 45, 200),
    ("ヨガ", 60, 150),
])
def test_save_multiple_workouts(dm, workout_factory, exercise, duration, calories):
    workout = workout_factory(exercise=exercise, duration=duration, calories=calories)
    result = dm.save_workout(workout)
    assert result is True
    assert any(w.exercise == exercise for w in dm.load_workouts())

def test_save_workout_without_notes(dm, workout_factory):
    workout = workout_factory(exercise="筋トレ", notes=None)
    dm.save_workout(workout)
    loaded = dm.load_workouts()
    assert loaded[0].notes is None

def test_save_workout_datetime_serialization(dm, workout_factory):
    workout_date = datetime(2025, 1, 15, 10, 30, 45)
    workout = workout_factory(date=workout_date, exercise="日時テスト")
    dm.save_workout(workout)

    with open(dm.data_dir / "workouts.json", "r", encoding="utf-8") as f:
        saved = json.load(f)

    assert saved[0]["date"] == workout_date.isoformat()

# ---------------------------
# 読み込みテスト
# ---------------------------
def test_load_empty_workouts(dm):
    assert dm.load_workouts() == []

def test_load_saved_workouts(dm, workout_factory):
    workout = workout_factory(exercise="テストランニング", duration=35, calories=350, notes="テストメモ")
    dm.save_workout(workout)
    loaded = dm.load_workouts()[0]

    assert loaded.exercise == workout.exercise
    assert loaded.notes == workout.notes
    assert loaded.date == workout.date

@pytest.mark.parametrize("dates, exercises", [
    ([datetime(2025, 1, 15, 10), datetime(2025, 1, 16, 11), datetime(2025, 1, 17, 12)],
     ["ランニング", "筋トレ", "ヨガ"]),
])
def test_load_workouts_order_preservation(dm, workout_factory, dates, exercises):
    for d, ex in zip(dates, exercises):
        dm.save_workout(workout_factory(date=d, exercise=ex))

    loaded = dm.load_workouts()
    assert [w.exercise for w in loaded] == exercises
    assert [w.date for w in loaded] == dates

def test_load_corrupted_workout_file(dm):
    with open(dm.data_dir / "workouts.json", "w", encoding="utf-8") as f:
        f.write("{ invalid json }")

    assert dm.load_workouts() == []

# ---------------------------
# 削除テスト
# ---------------------------
@pytest.mark.parametrize("exercises, delete_index, expected_remaining", [
    (["ランニング", "筋トレ", "ヨガ"], 0, ["筋トレ", "ヨガ"]),
    (["ランニング", "筋トレ", "ヨガ"], 1, ["ランニング", "ヨガ"]),
    (["ランニング", "筋トレ", "ヨガ"], 2, ["ランニング", "筋トレ"]),
])
def test_delete_workout_cases(dm, workout_factory, exercises, delete_index, expected_remaining):
    for ex in exercises:
        dm.save_workout(workout_factory(exercise=ex))

    assert dm.delete_workout(delete_index)
    remaining = [w.exercise for w in dm.load_workouts()]
    assert remaining == expected_remaining

def test_delete_only_workout(dm, workout_factory):
    dm.save_workout(workout_factory(exercise="唯一のワークアウト"))
    assert dm.delete_workout(0)
    assert dm.load_workouts() == []

def test_delete_invalid_index(dm, workout_factory):
    dm.save_workout(workout_factory(exercise="テストワークアウト"))
    assert not dm.delete_workout(-1)
    assert not dm.delete_workout(10)
    assert len(dm.load_workouts()) == 1

# ---------------------------
# エラーハンドリング
# ---------------------------
def test_save_workout_permission_error(dm, workout_factory):
    workout = workout_factory(exercise="権限エラーテスト")
    with patch("builtins.open", side_effect=PermissionError("Permission denied")):
        assert dm.save_workout(workout) is False

def test_save_workout_disk_full_error(dm, workout_factory):
    workout = workout_factory(exercise="ディスク容量テスト")
    with patch("builtins.open", side_effect=OSError("No space left on device")):
        assert dm.save_workout(workout) is False

def test_delete_workout_file_error(dm, workout_factory):
    workout = workout_factory(exercise="削除エラーテスト")
    dm.save_workout(workout)
    with patch("builtins.open", side_effect=IOError("Input/output error")):
        assert dm.delete_workout(0) is False

# ---------------------------
# エッジケース
# ---------------------------
def test_save_workout_with_extreme_values(dm, workout_factory):
    workout = workout_factory(duration=480, calories=5000)
    dm.save_workout(workout)
    loaded = dm.load_workouts()[0]
    assert loaded.duration == 480
    assert loaded.calories == 5000

def test_save_workout_with_unicode(dm, workout_factory):
    workout = workout_factory(exercise="ランニング 🏃‍♂️", notes="気持ちよかった 🌞")
    dm.save_workout(workout)
    loaded = dm.load_workouts()[0]
    assert loaded.exercise == "ランニング 🏃‍♂️"
    assert "🌞" in loaded.notes

def test_save_workout_with_long_notes(dm, workout_factory):
    long_notes = "詳細な記録。" * 10
    workout = workout_factory(exercise="長いメモ", notes=long_notes)
    dm.save_workout(workout)
    assert dm.load_workouts()[0].notes == long_notes

@pytest.mark.performance
def test_save_many_workouts_performance(dm, workout_factory):
    import time
    start = time.time()
    for i in range(10):
        dm.save_workout(workout_factory(date=datetime.now() + timedelta(minutes=i), exercise=f"Workout{i}"))
    duration = time.time() - start
    assert duration < 2.0
    assert len(dm.load_workouts()) == 10

def test_concurrent_workout_operations(temp_data_dir, workout_factory):
    dm1 = DataManager(data_dir=temp_data_dir)
    dm2 = DataManager(data_dir=temp_data_dir)

    dm1.save_workout(workout_factory(exercise="同時保存1"))
    dm2.save_workout(workout_factory(exercise="同時保存2"))

    exercises = [w.exercise for w in dm1.load_workouts()]
    assert "同時保存1" in exercises and "同時保存2" in exercises

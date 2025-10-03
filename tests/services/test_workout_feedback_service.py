"""WorkoutFeedbackService のテスト"""

import pytest
import json
from unittest.mock import MagicMock
from datetime import datetime, timedelta
from pydantic import BaseModel

from src.services.workout_feedback_service import WorkoutFeedbackService

# -------------------------
# 共通フィクスチャ
# -------------------------
@pytest.fixture
def mock_openai_client(mocker):
    """OpenAI クライアントをモック化"""
    client = MagicMock()
    mocker.patch("openai.OpenAI", return_value=client)
    return client

@pytest.fixture
def service(mock_openai_client):
    """テスト対象サービス"""
    service = WorkoutFeedbackService("test_api_key")
    service.client = mock_openai_client
    return service

# -------------------------
# スキーマ定義 (レスポンス検証用)
# -------------------------
class WorkoutFeedbackSchema(BaseModel):
    performance_score: int
    intensity_assessment: str | None = None
    duration_feedback: str | None = None
    calorie_assessment: str | None = None
    form_tips: list[str] | None = None
    progression_advice: str | None = None
    recovery_recommendation: str | None = None
    goal_alignment: str | None = None
    next_workout_suggestions: list[str] | None = None
    warning_flags: list[str] | None = None

class WeeklyFeedbackSchema(BaseModel):
    weekly_score: int
    frequency_assessment: str | None = None
    variety_score: int | None = None
    intensity_balance: str | None = None
    total_volume: str | None = None
    goal_progress: str | None = None
    strengths: list[str] | None = None
    areas_for_improvement: list[str] | None = None
    next_week_plan: str | None = None
    motivation_message: str | None = None

# -------------------------
# 単体テスト
# -------------------------
class TestWorkoutFeedbackService:
    def test_service_initialization_sets_client(self, mock_openai_client):
        """サービス初期化時に OpenAI クライアントが生成される"""
        service = WorkoutFeedbackService("test_api_key")
        assert hasattr(service, "client")
        mock_openai_client.assert_not_called()

    @pytest.mark.parametrize("input_value, expected_type", [
        (datetime(2025, 1, 1, 15, 45), str),
        ({"date": datetime(2025, 1, 1)}, dict),
        ([{"date": datetime(2025, 1, 1)}], list),
    ])
    def test_convert_datetime_to_str_various_inputs(self, service, input_value, expected_type):
        """_convert_datetime_to_str が datetime を ISO 文字列に変換できる"""
        result = service._convert_datetime_to_str(input_value)
        assert isinstance(result, expected_type)

    def test_convert_datetime_to_str_invalid_type(self, service):
        """未対応型を渡すと例外を出す"""
        class CustomClass:
            pass
        with pytest.raises(TypeError, match="未対応の型が渡されました"):
            service._convert_datetime_to_str(CustomClass())      

    def test_analyze_workout_returns_valid_feedback(self, mock_openai_client, service):
        """ワークアウト分析で有効な JSON を返す場合、辞書が返る"""
        feedback_result = {"performance_score": 8, "intensity_assessment": "適切"}
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content=json.dumps(feedback_result)))]
        mock_openai_client.chat.completions.create.return_value = mock_response

        workout = {"exercise": "ランニング", "duration": 30, "date": datetime.now()}
        profile = {"age": 30, "goal": "維持"}

        result = service.analyze_workout(workout, profile)
        validated = WorkoutFeedbackSchema(**result)
        assert validated.performance_score == 8
        assert validated.intensity_assessment == "適切"

    def test_analyze_workout_returns_none_on_invalid_json(self, mock_openai_client, service):
        """無効 JSON の場合 None を返す"""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="invalid"))]
        mock_openai_client.chat.completions.create.return_value = mock_response
        result = service.analyze_workout({"exercise": "test"}, {"age": 20})
        assert result is None
    
    def test_analyze_workout_returns_none_on_missing_field(self, mock_openai_client, service):
        """必須フィールド欠落時に None を返す"""
        feedback_result = {"intensity_assessment": "不足"}
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content=json.dumps(feedback_result)))]
        mock_openai_client.chat.completions.create.return_value = mock_response
        result = service.analyze_workout({"exercise": "test"}, {"age": 20})
        assert result is None

    def test_analyze_workout_returns_none_on_api_error(self, mock_openai_client, service, mocker):
        """API エラーの場合 None を返し streamlit.error を呼ぶ"""
        mock_openai_client.chat.completions.create.side_effect = Exception("API error")
        mock_st_error = mocker.patch("streamlit.error")
        result = service.analyze_workout({"exercise": "test"}, {"age": 20})
        assert result is None
        mock_st_error.assert_called_once()

    def test_analyze_workout_includes_recent_workouts_in_prompt(self, mock_openai_client, service):
        """最近のワークアウト履歴がプロンプトに含まれる"""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content='{"performance_score": 7}'))]
        mock_openai_client.chat.completions.create.return_value = mock_response
        workout = {"exercise": "筋トレ", "duration": 40}
        profile = {"age": 25}
        history = [{"exercise": "ランニング", "duration": 20}]
        result = service.analyze_workout(workout, profile, history)
        assert result["performance_score"] == 7
        assert mock_openai_client.chat.completions.create.called
        call_args = mock_openai_client.chat.completions.create.call_args
        prompt = call_args.kwargs["messages"][1]["content"]
        assert "過去の運動履歴" in prompt

    def test_analyze_weekly_progress_returns_valid_feedback(self, mock_openai_client, service):
        """週間分析が有効な JSON を返す場合、辞書が返る"""
        weekly_result = {"weekly_score": 6, "variety_score": 3, "strengths": ["継続"]}
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content=json.dumps(weekly_result)))]
        mock_openai_client.chat.completions.create.return_value = mock_response
        workouts = [{"exercise": "ランニング", "duration": 20, "date": datetime.now()}]
        profile = {"goal": "減量"}
        result = service.analyze_weekly_progress(workouts, profile)
        validated = WeeklyFeedbackSchema(**result)
        assert validated.weekly_score == 6
        assert "継続" in validated.strengths

    def test_analyze_weekly_progress_with_empty_list(self, mock_openai_client, service):
        """週間分析で空のワークアウトリストを渡す場合でも処理される"""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content='{"weekly_score": 0}'))]
        mock_openai_client.chat.completions.create.return_value = mock_response
        result = service.analyze_weekly_progress([], {"goal": "維持"})
        assert result["weekly_score"] == 0

    def test_analyze_weekly_progress_with_none(self, mock_openai_client, service):
        """週間分析に None を渡すと None を返す"""
        result = service.analyze_weekly_progress(None, {"goal": "維持"})
        assert result is None

    def test_analyze_weekly_progress_invalid_json(self, mock_openai_client, service):
        """週間分析で無効 JSON の場合 None を返す"""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="invalid"))]
        mock_openai_client.chat.completions.create.return_value = mock_response
        result = service.analyze_weekly_progress([], {"goal": "維持"})
        assert result is None

# -------------------------
# エッジケース
# -------------------------
class TestWorkoutFeedbackServiceEdgeCases:
    def test_analyze_workout_with_incomplete_profile(self, mock_openai_client, service):
        """プロフィールの一部が欠けていても分析が実行される"""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content='{"performance_score": 5}'))]
        mock_openai_client.chat.completions.create.return_value = mock_response
        workout = {"exercise": "テスト", "duration": 30}
        result = service.analyze_workout(workout, {"age": 30})
        assert result["performance_score"] == 5
        prompt = mock_openai_client.chat.completions.create.call_args.kwargs["messages"][1]["content"]
        assert "不明" in prompt

    def test_analyze_workout_with_extreme_values(self, mock_openai_client, service):
        """極端な値を含むワークアウトを分析"""
        feedback = {"performance_score": 3, "warning_flags": ["過度な運動"]}
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content=json.dumps(feedback)))]
        mock_openai_client.chat.completions.create.return_value = mock_response
        workout = {"exercise": "マラソン", "duration": 300, "calories": 3000, "date": datetime.now()}
        profile = {"age": 20}
        result = service.analyze_workout(workout, profile)
        assert "過度な運動" in result["warning_flags"]

    def test_analyze_weekly_progress_with_single_workout(self, mock_openai_client, service):
        """1回のみのワークアウトを分析"""
        feedback = {"weekly_score": 4, "variety_score": 1}
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content=json.dumps(feedback)))]
        mock_openai_client.chat.completions.create.return_value = mock_response
        workouts = [{"exercise": "ウォーキング", "duration": 20, "date": datetime.now()}]
        result = service.analyze_weekly_progress(workouts, {"goal": "減量"})
        assert result["variety_score"] == 1

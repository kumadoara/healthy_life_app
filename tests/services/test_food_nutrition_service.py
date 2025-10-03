"""FoodNutritionService のテスト"""

import pytest
import json
import base64
from unittest.mock import MagicMock

import pydantic
from src.services.food_nutrition_service import FoodNutritionService


# -------------------------
# 共通フィクスチャ
# -------------------------
@pytest.fixture
def mock_openai_client(mocker):
    """OpenAI クライアントをモック化"""
    client = MagicMock()
    mocker.patch("openai.OpenAI", return_value=client)
    return client

# -------------------------
# JSON スキーマ (pydantic)
# ------------------------
class NutritionSchema(pydantic.BaseModel):
    food_name: str
    calories: float | int | None = None
    protein: float | None = None
    carbs: float | None = None
    fat: float | None = None
    confidence: float | None = None

# -------------------------
# FoodNutritionService テスト
# -------------------------
class TestFoodNutritionService:
    """FoodNutritionService の単体テスト"""

    def test_service_initialization_creates_client(self, mock_openai_client):
        """サービス初期化時に OpenAI クライアントが生成される"""
        service = FoodNutritionService("test_api_key")
        assert hasattr(service, "client")
        mock_openai_client.assert_not_called()  # fixture は呼ばれるが内部生成はされる

    @pytest.mark.parametrize("content, expected_name, expected_calories", [
        (json.dumps({"food_name": "鶏胸肉", "calories": 165, "protein": 31.0, "confidence": 0.9}), "鶏胸肉", 165),
        (f"```json\n{json.dumps({'food_name': 'バナナ', 'calories': 89})}\n```", "バナナ", 89),
        ("{ invalid json }", None, None),
    ])
    def test_get_nutrition_info_various_responses(
        self, mock_openai_client, content, expected_name, expected_calories
    ):
        """栄養情報取得がレスポンス形式に応じて動作する"""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content=content))]
        mock_openai_client.chat.completions.create.return_value = mock_response

        service = FoodNutritionService("test_api_key")
        result = service.get_nutrition_info("テスト食品")

        if expected_name is None:
            assert result is None
        else:
            parsed = NutritionSchema(**result)  # スキーマでバリデーション
            assert parsed.food_name == expected_name
            assert parsed.calories == expected_calories
    
    def test_get_nutrition_info_handles_api_error(self, mock_openai_client, mocker):
        """API エラー時に None を返し、エラーメッセージが出力される"""
        mock_openai_client.chat.completions.create.side_effect = Exception("API Error")
        mock_st_error = mocker.patch("streamlit.error")
        service = FoodNutritionService("test_api_key")
        result = service.get_nutrition_info("エラー食品")
        assert result is None
        mock_st_error.assert_called_once()
        assert "エラー" in mock_st_error.call_args[0][0]
    
    def test_get_nutrition_info_with_invalid_json_structure(self, mock_openai_client, mocker):
        """必須フィールド欠落の JSON は None を返す"""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content=json.dumps({"calories": 100})))]
        mock_openai_client.chat.completions.create.return_value = mock_response
        mock_st_error = mocker.patch("streamlit.error")
        service = FoodNutritionService("test_api_key")
        result = service.get_nutrition_info("欠落食品")
        assert result is None
        mock_st_error.assert_called_once()
        assert "必須フィールド" in mock_st_error.call_args[0][0]

    def test_get_nutrition_info_with_empty_response(self, mock_openai_client, mocker):
        """API が空レスポンスを返した場合 None を返す"""
        mock_response = MagicMock()
        mock_response.choices = []
        mock_openai_client.chat.completions.create.return_value = mock_response
        mock_st_error = mocker.patch("streamlit.error")
        service = FoodNutritionService("test_api_key")
        result = service.get_nutrition_info("空食品")
        assert result is None
        mock_st_error.assert_called_once()
        assert "レスポンスが空" in mock_st_error.call_args[0][0]

    def test_analyze_meal_image_successfully_parses_json(self, mock_openai_client):
        """画像分析が正常に JSON を返す"""
        analysis_result = {"detected_foods": ["ご飯", "味噌汁"], "overall_score": 4}
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content=json.dumps(analysis_result)))]
        mock_openai_client.chat.completions.create.return_value = mock_response
        service = FoodNutritionService("test_api_key")
        result = service.analyze_meal_image(b"fake_image")
        assert result["detected_foods"] == ["ご飯", "味噌汁"]
        assert result["overall_score"] == 4
    
    def test_analyze_meal_image_encodes_base64(self, mock_openai_client):
        """画像が Base64 でエンコードされて API に送られる"""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content='{"detected_foods": ["テスト"]}'))]
        mock_openai_client.chat.completions.create.return_value = mock_response
        service = FoodNutritionService("test_api_key")
        test_image = b"image_bytes"
        expected_b64 = base64.b64encode(test_image).decode("utf-8")
        service.analyze_meal_image(test_image)
        messages = mock_openai_client.chat.completions.create.call_args.kwargs["messages"]
        image_url = messages[0]["content"][1]["image_url"]["url"]
        assert expected_b64 in image_url
        assert image_url.startswith("data:image/jpeg;base64,")

    def test_analyze_meal_image_handles_gpt4_vision_unavailable(self, mock_openai_client, mocker):
        """GPT-4 Vision モデル未対応エラーを警告に変換"""
        mock_openai_client.chat.completions.create.side_effect = Exception("gpt-4-vision not available")
        mock_st_warning = mocker.patch("streamlit.warning")
        service = FoodNutritionService("test_api_key")
        result = service.analyze_meal_image(b"img")
        assert result is None
        mock_st_warning.assert_called_once()
    
    def test_analyze_meal_image_invalid_json_returns_none(self, mock_openai_client):
        """無効な JSON が返ってきた場合 None を返す"""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="invalid json"))]
        mock_openai_client.chat.completions.create.return_value = mock_response
        service = FoodNutritionService("test_api_key")
        result = service.analyze_meal_image(b"img")
        assert result is None

    def test_analyze_meal_image_with_none_input(self, mock_openai_client, mocker):
        """画像が None の場合はエラーになる"""
        service = FoodNutritionService("test_api_key")
        mock_st_error = mocker.patch("streamlit.error")
        result = service.analyze_meal_image(None)
        assert result is None
        mock_st_error.assert_called_once()
        assert "画像が指定されていません" in mock_st_error.call_args[0][0]

    def test_analyze_meal_image_unexpected_exception(self, mock_openai_client, mocker):
        """予期しない例外はエラーに変換される"""
        mock_openai_client.chat.completions.create.side_effect = RuntimeError("Unknown Error")
        mock_st_error = mocker.patch("streamlit.error")
        service = FoodNutritionService("test_api_key")
        result = service.analyze_meal_image(b"img")
        assert result is None
        mock_st_error.assert_called_once()
        assert "予期しないエラー" in mock_st_error.call_args[0][0]
    
class TestFoodNutritionServiceEdgeCases:
    """FoodNutritionService のエッジケース"""
    
    def test_empty_food_name_is_handled(self, mock_openai_client):
        """空の食品名でも処理できる"""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content=json.dumps({"food_name": "", "confidence": 0.0})))]
        mock_openai_client.chat.completions.create.return_value = mock_response
        service = FoodNutritionService("test_api_key")
        result = service.get_nutrition_info("")
        assert result["food_name"] == ""
        assert result["confidence"] == 0.0
    
    def test_large_image_data_is_processed(self, mock_openai_client):
        """大きな画像データ（1MB 以上）でも処理される"""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content='{"detected_foods": ["ok"]}'))]
        mock_openai_client.chat.completions.create.return_value = mock_response
        large_image = b"x" * (1024 * 1024)  # 1MB
        service = FoodNutritionService("test_api_key")
        result = service.analyze_meal_image(large_image)
        assert result["detected_foods"] == ["ok"]
    
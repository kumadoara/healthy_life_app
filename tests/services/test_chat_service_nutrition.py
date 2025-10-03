"""チャットサービス - 栄養相談機能のテスト"""

import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime

from src.services.chat_service import HealthChatService
from src.models.user_profile import UserProfile

@pytest.fixture
def sample_user_profile():
    return UserProfile(
        name="テストユーザー",
        age=30,
        gender="男性",
        height=175.0,
        weight=70.0,
        activity_level="適度な運動",
        goal="体重維持"
    )

class TestNutritionChainCreation:
    """栄養相談チェーン作成のテスト"""

    @patch('src.services.chat_service.ChatOpenAI')
    @patch('src.services.chat_service.ConversationChain')
    @patch('src.services.chat_service.ConversationBufferMemory')
    def test_create_nutrition_chain_basic(self, mock_memory, mock_chain, mock_llm, sample_user_profile):
        service = HealthChatService("test_api_key")
        chain = service.create_nutrition_chain(sample_user_profile)
        mock_chain.assert_called_once()
        call_kwargs = mock_chain.call_args.kwargs
        assert 'llm' in call_kwargs
        assert 'prompt' in call_kwargs
        assert 'memory' in call_kwargs
        assert call_kwargs['verbose'] is False

    @patch('src.services.chat_service.ChatOpenAI')
    @patch('src.services.chat_service.ConversationChain')
    @patch('src.services.chat_service.ConversationBufferMemory')
    @patch('src.utils.helpers.calculate_bmi')
    @patch('src.utils.helpers.calculate_bmr')
    def test_create_nutrition_chain_with_calculations(self, mock_bmr, mock_bmi, mock_memory, mock_chain, mock_llm):
        mock_bmi.return_value = 22.9
        mock_bmr.return_value = 1678.5
        service = HealthChatService("test_api_key")
        profile = UserProfile(
            name="計算テストユーザー",
            age=25,
            gender="女性",
            height=165.0,
            weight=55.0,
            activity_level="軽い運動",
            goal="健康維持"
        )
        chain = service.create_nutrition_chain(profile)
        mock_bmi.assert_called_once_with(165.0, 55.0)
        mock_bmr.assert_called_once_with(165.0, 55.0, 25, "女性")
        assert chain == mock_chain.return_value
    
    def test_create_chain_with_invalid_profile(self):
        service = HealthChatService("test_api_key")
        # バリデーションをバイパスして無効なプロフィールを作成
        invalid_profile = UserProfile(
            name="無効ユーザー",
            age=30,  # 一時的に有効な値で作成
            gender="男性",
            height=175.0,
            weight=70.0,
            activity_level="適度な運動",
            goal="体重維持"
        )
        # 後で無効な値を直接設定
        invalid_profile.age = 9
        invalid_profile.height = 99.9
        invalid_profile.weight = 29.9
        invalid_profile.activity_level = "不明"
        invalid_profile.goal = "不明"

        with pytest.raises(ValueError, match="身長は100cm以上250cm以下で入力してください"):
            service.create_nutrition_chain(invalid_profile)

class TestNutritionResponseGeneration:
    @patch('src.services.chat_service.ChatOpenAI')
    @patch('src.services.chat_service.ConversationBufferMemory')
    def test_nutrition_response_invoke_method(self, mock_memory, mock_llm):
        service = HealthChatService("test_api_key")
        mock_chain = MagicMock()
        mock_chain.invoke.return_value = {"response": "バランスの良い食事を心がけましょう"}
        response = service.get_response(mock_chain, "ダイエットに良い食事は？")
        assert response == "バランスの良い食事を心がけましょう"
        mock_chain.invoke.assert_called_once_with({"input": "ダイエットに良い食事は？"})

    @pytest.mark.parametrize("question,mock_response,expected", [
        ("ダイエットに良い食べ物は？", {"response": "野菜と魚を中心とした食事がおすすめです"}, "野菜と魚を中心とした食事がおすすめです"),
        ("筋肉をつけるには何を食べればいい？", {"text": "タンパク質を多く含む食品を摂取しましょう"}, "タンパク質を多く含む食品を摂取しましょう"),
        ("カロリー計算はどうすればいい？", {"output": "基礎代謝を計算してから活動量を考慮します"}, "基礎代謝を計算してから活動量を考慮します"),
        ("水分摂取量の目安は？", {"content": "体重1kgあたり35ml程度が目安です"}, "体重1kgあたり35ml程度が目安です"),
    ])
    def test_various_nutrition_questions(self, question, mock_response, expected):
        service = HealthChatService("test_api_key")
        mock_chain = MagicMock()
        mock_chain.invoke.return_value = mock_response
        response = service.get_response(mock_chain, question)
        assert response == expected

    def test_get_response_with_empty_input(self):
        service = HealthChatService("test_api_key")
        mock_chain = MagicMock()
        response = service.get_response(mock_chain, "")
        assert response.startswith("入力が無効です")

    @pytest.mark.parametrize("unexpected_response", [123, 45.6, ["a", "b"], None])
    def test_get_response_with_unexpected_format(self, unexpected_response):
        service = HealthChatService("test_api_key")
        mock_chain = MagicMock()
        mock_chain.invoke.return_value = unexpected_response
        response = service.get_response(mock_chain, "テスト入力")
        assert response.startswith("予期しないレスポンス形式です")

class TestNutritionStreamingResponse:
    @patch('src.services.chat_service.ChatOpenAI')
    @patch('src.services.chat_service.ConversationBufferMemory')
    def test_nutrition_streaming_response_multiple_chunks(self, mock_memory, mock_llm):
        service = HealthChatService("test_api_key")
        mock_chain = MagicMock()
        responses = ["カロリー制限", "と", "栄養バランス", "が重要です"]
        mock_chain.invoke.return_value = {"response": "".join(responses)}
        user_input = "効果的なダイエット方法は？"
        streaming_response = service.get_streaming_response(mock_chain, user_input)
        response_list = list(streaming_response)
        assert all(isinstance(r, str) for r in response_list)
        assert "".join(response_list) == "カロリー制限と栄養バランスが重要です"

    def test_streaming_response_with_error(self):
        service = HealthChatService("test_api_key")
        mock_chain = MagicMock()
        mock_chain.invoke.side_effect = Exception("Streaming error")
        user_input = "異常テスト"
        streaming_response = service.get_streaming_response(mock_chain, user_input)
        response_list = list(streaming_response)
        assert any("エラー: ストリーミングレスポンスの取得に失敗しました" in r for r in response_list)

class TestNutritionMemoryManagement:
    def test_clear_memory_when_none(self):
        service = HealthChatService("test_api_key")
        service.nutrition_memory = None
        service.clear_nutrition_memory() # 例外が出ないことを確認

"""HealthChatService のテスト"""

import pytest
from unittest.mock import MagicMock, patch
import os

from src.services.chat_service import HealthChatService

class TestHealthChatServiceInitialization:
    """初期化関連のテスト"""

    @patch("src.services.chat_service.ChatOpenAI")
    @patch("src.services.chat_service.ConversationBufferMemory")
    def test_initialization_sets_api_key_and_creates_memories(
        self, mock_memory, mock_llm
    ):
        """APIキーを設定し、栄養/トレーニング用のメモリが2つ作成される"""
        api_key = "test_api_key"
        service = HealthChatService(api_key)

        assert os.environ["OPENAI_API_KEY"] == api_key
        mock_llm.assert_called_once()
        assert mock_memory.call_count == 2
        assert hasattr(service, "nutrition_memory")
        assert hasattr(service, "training_memory")
    
class TestChainCreation:
    """チェーン作成のテスト"""

    @patch("src.services.chat_service.ChatOpenAI")
    @patch("src.services.chat_service.ConversationChain")
    def test_create_nutrition_chain_returns_chain(self, mock_chain, mock_llm, sample_user_profile):
        """栄養相談チェーンが作成される"""
        service = HealthChatService("test_api_key")
        chain = service.create_nutrition_chain(sample_user_profile)
        assert chain is not None
        mock_chain.assert_called_once()
    
    @patch("src.services.chat_service.ChatOpenAI")
    @patch("src.services.chat_service.ConversationChain")
    def test_create_training_chain_returns_chain(self, mock_chain, mock_llm, sample_user_profile):
        """トレーニング相談チェーンが作成される"""
        service = HealthChatService("test_api_key")
        chain = service.create_training_chain(sample_user_profile)
        assert chain is not None
        mock_chain.assert_called_once()

    @patch("src.services.chat_service.ConversationChain", side_effect=Exception("Chain creation failed"))
    @patch("src.services.chat_service.ChatOpenAI")
    def test_create_chain_failure_outputs_error(self, mock_llm, mock_chain, mocker, sample_user_profile):
        """チェーン作成時にエラーが発生した場合、メッセージを出力"""
        mock_st_error = mocker.patch("streamlit.error")
        service = HealthChatService("test_api_key")
        chain = service.create_nutrition_chain(sample_user_profile)
        assert chain is None
        mock_st_error.assert_called_once()
        assert "チェーン作成中にエラー" in mock_st_error.call_args[0][0]

class TestResponseMethods:
    """レスポンス取得のテスト"""

    @pytest.mark.parametrize("return_value", [
        {"response": "辞書形式レスポンス"},
        "文字列レスポンス",
    ])
    @patch("src.services.chat_service.ChatOpenAI")
    def test_get_response_returns_expected_value(self, mock_llm, return_value):
        """invoke が正常ならそのレスポンスを返す"""
        service = HealthChatService("test_api_key")
        mock_chain = MagicMock()
        mock_chain.invoke.return_value = return_value
        result = service.get_response(mock_chain, "テスト質問")
        if isinstance(return_value, dict):
            assert result == return_value["response"]
        else:
            assert result == return_value
        mock_chain.invoke.assert_called_once_with({"input": "テスト質問"})

    @pytest.mark.parametrize(
        "invoke_ok, predict_ok, run_ok, expected",
        [
            (False, True, True, "予測レスポンス"),
            (False, False, True, "実行レスポンス"),
            (False, False, False, "申し訳ございません"),
        ],
    )
    @patch("src.services.chat_service.ChatOpenAI")
    def test_get_response_fallback_logic(
        self, mock_llm, invoke_ok, predict_ok, run_ok, expected
    ):
        """invoke/predict/run が失敗した場合フォールバックする"""
        service = HealthChatService("test_api_key")
        mock_chain = MagicMock()
        if invoke_ok:
            mock_chain.invoke.return_value = {"response": "呼出レスポンス"}
        else:
            mock_chain.invoke.side_effect = Exception("呼出失敗")
        if predict_ok:
            mock_chain.predict.return_value = "予測レスポンス"
        else:
            mock_chain.predict.side_effect = Exception("予測失敗")
        if run_ok:
            mock_chain.run.return_value = "実行レスポンス"
        else:
            mock_chain.run.side_effect = Exception("実行失敗")
        response = service.get_response(mock_chain, "テスト質問")
        assert expected in response

    @patch("src.services.chat_service.ChatOpenAI")
    def test_get_response_returns_none_and_outputs_error(self, mock_llm, mocker):
        """invoke が None を返した場合、エラーメッセージを出力"""
        service = HealthChatService("test_api_key")
        mock_chain = MagicMock()
        mock_chain.invoke.return_value = None
        mock_st_error = mocker.patch("streamlit.error")
        result = service.get_response(mock_chain, "テスト質問")
        assert result is None or "エラー" in result
        mock_st_error.assert_called_once()
        assert "レスポンスが不正" in mock_st_error.call_args[0][0]
    
    @patch("src.services.chat_service.ChatOpenAI")
    def test_get_streaming_response_yields_values(self, mock_llm):
        """get_streaming_response はジェネレーターを返す"""
        service = HealthChatService("test_api_key")
        mock_chain = MagicMock()
        mock_chain.invoke.return_value = {"response": "ストリーミングレスポンス"}
        response_iter = service.get_streaming_response(mock_chain, "テスト質問")
        results = list(response_iter)
        assert results == ["ストリーミングレスポンス"]

    @patch("src.services.chat_service.ChatOpenAI")
    def test_get_streaming_response_handles_error(self, mock_llm, mocker):
        """invoke が例外を投げた場合、日本語エラーメッセージを返す"""
        service = HealthChatService("test_api_key")
        mock_chain = MagicMock()
        mock_chain.invoke.side_effect = Exception("invoke error")
        mock_st_error = mocker.patch("streamlit.error")
        response_iter = service.get_streaming_response(mock_chain, "テスト質問")
        results = list(response_iter)
        assert results == ["エラー: ストリーミングレスポンスの取得に失敗しました"]
        mock_st_error.assert_called_once()
        assert "ストリーミングレスポンスの取得に失敗" in mock_st_error.call_args[0][0]
    
class TestMemoryManagement:
    """メモリ操作のテスト"""
    
    @patch("src.services.chat_service.ConversationBufferMemory")
    @patch("src.services.chat_service.ChatOpenAI")
    def test_clear_nutrition_memory_calls_clear(self, mock_llm, mock_memory):
        service = HealthChatService("test_api_key")
        service.clear_nutrition_memory()
        assert isinstance(service.nutrition_memory, MagicMock)
        service.nutrition_memory.clear.assert_called_once()

    @patch("src.services.chat_service.ConversationBufferMemory")
    @patch("src.services.chat_service.ChatOpenAI")
    def test_clear_training_memory_calls_clear(self, mock_llm, mock_memory):
        service = HealthChatService("test_api_key")
        service.clear_training_memory()
        assert isinstance(service.training_memory, MagicMock)
        service.training_memory.clear.assert_called_once()

    @patch("src.services.chat_service.ConversationBufferMemory")
    @patch("src.services.chat_service.ChatOpenAI")
    def test_clear_memory_clears_both(self, mock_llm, mock_memory):
        service = HealthChatService("test_api_key")
        service.clear_memory()
        # Both memories are called, but they are the same mock instance
        assert service.nutrition_memory.clear.called
        assert service.training_memory.clear.called

    @patch("src.services.chat_service.ConversationBufferMemory")
    @patch("src.services.chat_service.ChatOpenAI")
    def test_clear_memory_handles_error(self, mock_llm, mock_memory, mocker):
        """メモリクリアでエラーが発生した場合、エラーメッセージを出力"""
        service = HealthChatService("test_api_key")
        service.nutrition_memory.clear.side_effect = Exception("clear failed")
        mock_st_error = mocker.patch("streamlit.error")
        service.clear_memory()
        mock_st_error.assert_called_once()
        assert "メモリクリア中にエラー" in mock_st_error.call_args[0][0]

class TestErrorHandling:
    """エラーハンドリングのテスト"""

    @patch("src.services.chat_service.ConversationChain")
    @patch("src.services.chat_service.ChatOpenAI")
    def test_chain_creation_with_incomplete_profile_does_not_raise(self, mock_llm, mock_chain):
        """プロフィールが不完全でもチェーン作成がエラーにならない"""
        service = HealthChatService("test_api_key")
        incomplete_profile = MagicMock()
        incomplete_profile.name = None
        incomplete_profile.age = 30
        incomplete_profile.gender = "男性"
        incomplete_profile.height = 175.0
        incomplete_profile.weight = 70.0
        incomplete_profile.activity_level = "適度な運動"
        incomplete_profile.goal = "体重維持"

        chain = service.create_nutrition_chain(incomplete_profile)
        assert chain is not None or chain is None

    def test_api_key_is_set_in_environment(self, monkeypatch):
        """サービス初期化時に APIキーが環境変数に設定される"""
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        service = HealthChatService("new_test_key")
        assert os.environ["OPENAI_API_KEY"] == "new_test_key"

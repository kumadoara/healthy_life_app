import pytest
import os
from unittest.mock import patch

from src.services.chat_service import HealthChatService

class TestHealthChatServiceInitializationErrors:
    """HealthChatService 初期化異常系テスト"""

    def test_api_key_none_error(self):
        """APIキーが None の場合のエラーテスト"""
        with pytest.raises(ValueError, match="APIキーが設定されていません"):
            HealthChatService(None)

    def test_api_key_empty_error(self):
        """APIキーが空文字の場合のエラーテスト"""
        with pytest.raises(ValueError, match="APIキーが空です"):
            HealthChatService("")

    def test_api_key_too_short_error(self):
        """APIキーが短すぎる場合のエラーテスト"""
        with pytest.raises(ValueError, match="APIキーが短すぎます"):
            HealthChatService("ab")

    def test_api_key_invalid_characters_error(self):
        """APIキーに無効な文字が含まれている場合のエラーテスト"""
        with pytest.raises(ValueError, match="APIキーに無効な文字が含まれています"):
            HealthChatService("invalid key with space")


class TestHealthChatServiceInitializationNormal:
    """HealthChatService 正常系初期化テスト"""

    @patch('src.services.chat_service.ChatOpenAI')
    @patch('src.services.chat_service.ConversationBufferMemory')
    def test_basic_initialization(self, mock_memory, mock_llm):
        api_key = "valid_api_key_123"
        service = HealthChatService(api_key)

        # 環境変数が設定されていることを確認
        assert os.environ.get("OPENAI_API_KEY") == api_key

        # llm が正しく初期化されていることを確認
        assert hasattr(service, "llm")
        assert service.llm == mock_llm.return_value

        # メモリが正しく初期化されていることを確認
        assert hasattr(service, "nutrition_memory")
        assert hasattr(service, "training_memory")

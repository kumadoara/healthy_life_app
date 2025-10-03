import pytest
from unittest.mock import MagicMock, patch

from src.services.chat_service import HealthChatService
from src.models.user_profile import UserProfile


class TestTrainingChainErrorCases:
    """トレーニングチェーン異常系テスト"""

    @patch('src.services.chat_service.ChatOpenAI')
    @patch('src.services.chat_service.ConversationBufferMemory')
    def test_invalid_age_error(self, mock_memory, mock_llm):
        """年齢が不正（負の値）の場合のエラーテスト"""
        service = HealthChatService("test_api_key")

        # バリデーションをバイパスして無効なプロフィールを作成
        invalid_profile = UserProfile(
            name="年齢エラーユーザー",
            age=30,  # 一時的に有効な値で作成
            gender="男性",
            height=175.0,
            weight=70.0,
            activity_level="活発",
            goal="筋肉増強"
        )
        # 後で無効な値を直接設定
        invalid_profile.age = -5

        with pytest.raises(ValueError, match="年齢は正の整数で入力してください"):
            service.create_training_chain(invalid_profile)

    @patch('src.services.chat_service.ChatOpenAI')
    @patch('src.services.chat_service.ConversationBufferMemory')
    def test_invalid_weight_error(self, mock_memory, mock_llm):
        """体重が0以下の場合のエラーテスト"""
        service = HealthChatService("test_api_key")

        # バリデーションをバイパスして無効なプロフィールを作成
        invalid_profile = UserProfile(
            name="体重エラーユーザー",
            age=30,
            gender="男性",
            height=180.0,
            weight=70.0,  # 一時的に有効な値で作成
            activity_level="適度な運動",
            goal="減量"
        )
        # 後で無効な値を直接設定
        invalid_profile.weight = 0.0

        with pytest.raises(ValueError, match="体重は1kg以上で入力してください"):
            service.create_training_chain(invalid_profile)

    @patch('src.services.chat_service.ChatOpenAI')
    @patch('src.services.chat_service.ConversationBufferMemory')
    def test_missing_goal_error(self, mock_memory, mock_llm):
        """目標が空の場合のエラーテスト"""
        service = HealthChatService("test_api_key")

        # バリデーションをバイパスして無効なプロフィールを作成
        invalid_profile = UserProfile(
            name="目標なしユーザー",
            age=25,
            gender="女性",
            height=160.0,
            weight=55.0,
            activity_level="軽い運動",
            goal="体重維持"  # 一時的に有効な値で作成
        )
        # 後で無効な値を直接設定
        invalid_profile.goal = ""

        with pytest.raises(ValueError, match="目標を入力してください"):
            service.create_training_chain(invalid_profile)

    @patch('src.services.chat_service.ChatOpenAI')
    @patch('src.services.chat_service.ConversationBufferMemory')
    def test_missing_gender_error(self, mock_memory, mock_llm):
        """性別が未設定の場合のエラーテスト"""
        service = HealthChatService("test_api_key")

        # バリデーションをバイパスして無効なプロフィールを作成
        invalid_profile = UserProfile(
            name="性別なしユーザー",
            age=40,
            gender="男性",  # 一時的に有効な値で作成
            height=170.0,
            weight=68.0,
            activity_level="活発",
            goal="健康維持"
        )
        # 後で無効な値を直接設定
        invalid_profile.gender = ""

        with pytest.raises(ValueError, match="性別を入力してください"):
            service.create_training_chain(invalid_profile)

    @patch('src.services.chat_service.ChatOpenAI')
    @patch('src.services.chat_service.ConversationBufferMemory')
    def test_invalid_height_error(self, mock_memory, mock_llm):
        """身長が極端に低い/高い場合のエラーテスト"""
        service = HealthChatService("test_api_key")

        # バリデーションをバイパスして無効なプロフィールを作成
        too_low_profile = UserProfile(
            name="低身長ユーザー",
            age=20,
            gender="男性",
            height=170.0,  # 一時的に有効な値で作成
            weight=50.0,
            activity_level="座りがち",
            goal="減量"
        )
        # 後で無効な値を直接設定
        too_low_profile.height = 30.0

        with pytest.raises(ValueError, match="身長は100cm以上250cm以下で入力してください"):
            service.create_training_chain(too_low_profile)

        # バリデーションをバイパスして無効なプロフィールを作成
        too_high_profile = UserProfile(
            name="高身長ユーザー",
            age=22,
            gender="女性",
            height=170.0,  # 一時的に有効な値で作成
            weight=70.0,
            activity_level="活発",
            goal="筋肉増強"
        )
        # 後で無効な値を直接設定
        too_high_profile.height = 300.0

        with pytest.raises(ValueError, match="身長は100cm以上250cm以下で入力してください"):
            service.create_training_chain(too_high_profile)

    @patch('src.services.chat_service.ChatOpenAI')
    @patch('src.services.chat_service.ConversationBufferMemory')
    def test_invalid_activity_level_error(self, mock_memory, mock_llm):
        """活動レベルが未定義の場合のエラーテスト"""
        service = HealthChatService("test_api_key")

        # バリデーションをバイパスして無効なプロフィールを作成
        invalid_profile = UserProfile(
            name="活動レベルエラーユーザー",
            age=35,
            gender="男性",
            height=172.0,
            weight=70.0,
            activity_level="適度な運動",  # 一時的に有効な値で作成
            goal="筋肉増強"
        )
        # 後で無効な値を直接設定
        invalid_profile.activity_level = ""

        with pytest.raises(ValueError, match="活動レベルを入力してください"):
            service.create_training_chain(invalid_profile)

    @patch('src.services.chat_service.ChatOpenAI')
    @patch('src.services.chat_service.ConversationChain')
    @patch('src.services.chat_service.ConversationBufferMemory')
    def test_response_failure_error(self, mock_memory, mock_chain, mock_llm):
        """レスポンス取得に失敗した場合のエラーテスト"""
        service = HealthChatService("test_api_key")

        # チェーンのモック設定
        mock_chain_instance = MagicMock()
        mock_chain_instance.invoke.side_effect = Exception("レスポンス生成に失敗しました")
        mock_chain_instance.predict.side_effect = Exception("予測失敗")
        mock_chain_instance.run.side_effect = Exception("実行失敗")
        mock_chain.return_value = mock_chain_instance

        profile = UserProfile(
            name="レスポンスエラーユーザー",
            age=28,
            gender="男性",
            height=170.0,
            weight=65.0,
            activity_level="活発",
            goal="筋肉増強"
        )

        chain = service.create_training_chain(profile)

        response = service.get_response(chain, "腕立て伏せの効果は？")
        assert "申し訳ございません" in response

    @patch('src.services.chat_service.ChatOpenAI')
    @patch('src.services.chat_service.ConversationBufferMemory')
    def test_streaming_response_error(self, mock_memory, mock_llm):
        """ストリーミングレスポンス取得時のエラーテスト"""
        service = HealthChatService("test_api_key")

        mock_chain = MagicMock()
        mock_chain.invoke.side_effect = Exception("ストリーミングレスポンスの取得に失敗しました")
        mock_chain.predict.side_effect = Exception("予測失敗")
        mock_chain.run.side_effect = Exception("実行失敗")

        responses = list(service.get_streaming_response(mock_chain, "正しいフォームを教えてください"))
        assert len(responses) > 0
        assert "エラー: ストリーミングレスポンスの取得に失敗しました" in responses[0]


class TestTrainingResponseVariations:
    """トレーニングレスポンスのバリエーションテスト"""

    @patch('src.services.chat_service.ChatOpenAI')
    @patch('src.services.chat_service.ConversationBufferMemory')
    def test_multiple_response_formats(self, mock_memory, mock_llm):
        """異なるレスポンスフォーマットのテスト"""
        service = HealthChatService("test_api_key")

        test_cases = [
            ("スクワットのやり方は？", {"response": "背筋を伸ばして腰を落とします"}),
            ("筋トレ頻度は？", {"text": "週2〜3回が目安です"}),
            ("有酸素運動は？", {"output": "ジョギングやサイクリングがおすすめです"}),
            ("ストレッチは？", {"content": "運動前は動的ストレッチ、運動後は静的ストレッチが有効です"}),
        ]

        for question, mock_result in test_cases:
            mock_chain = MagicMock()
            mock_chain.invoke.return_value = mock_result

            result = service.get_response(mock_chain, question)
            expected = list(mock_result.values())[0]
            assert result == expected

    @patch('src.services.chat_service.ChatOpenAI')
    @patch('src.services.chat_service.ConversationBufferMemory')
    def test_empty_response_handling(self, mock_memory, mock_llm):
        """空のレスポンス処理テスト"""
        service = HealthChatService("test_api_key")

        mock_chain = MagicMock()
        mock_chain.invoke.return_value = {}

        response = service.get_response(mock_chain, "腕立て伏せの正しいフォームは？")

        assert response == "回答が生成されませんでした"  # サービス側でハンドリングされることを期待

    @patch('src.services.chat_service.ChatOpenAI')
    @patch('src.services.chat_service.ConversationBufferMemory')
    def test_long_response_handling(self, mock_memory, mock_llm):
        """長文レスポンスの処理テスト"""
        service = HealthChatService("test_api_key")

        long_text = "トレーニングについての詳細な説明:" + "有酸素運動と筋トレを組み合わせることが重要です。" * 50

        mock_chain = MagicMock()
        mock_chain.invoke.return_value = {"response": long_text}

        response = service.get_response(mock_chain, "総合的なトレーニングの説明をしてください")

        assert response.startswith("トレーニングについての詳細な説明")
        assert len(response) > 200

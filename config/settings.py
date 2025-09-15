import os
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv()

class Settings:
    # API設定
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL = "o4-mini"

    # アプリ設定
    APP_NAME = "ヘルシーライフ"
    APP_VERSION = "1.0.0"
    APP_DESCRIPTION = "AIを活用したパーソナル健康管理アプリ"

    # データ設定
    DATA_DIR = "data/users"
    EXPORT_DIR = "data/exports"

    # 栄養計算の定数
    PROTEIN_CALORIES_PER_GRAM = 4
    CARBS_CALORIES_PER_GRAM = 4
    FAT_CALORIES_PER_GRAM = 9

    # 活動レベル係数
    ACTIVITY_MULTIPLIERS = {
        "座りがち": 1.2,
        "軽い運動": 1.375,
        "適度な運動": 1.55,
        "活発": 1.725,
        "非常に活発": 1.9
    }

    # 目標別マクロ配分
    MACRO_RATIOS = {
        "減量": {"protein": 0.30, "carbs": 0.35, "fat": 0.35},
        "増量": {"protein": 0.25, "carbs": 0.45, "fat": 0.30},
        "筋肉増強": {"protein": 0.30, "carbs": 0.40, "fat": 0.30},
        "体重維持": {"protein": 0.20, "carbs": 0.50, "fat": 0.30},
        "健康維持": {"protein": 0.20, "carbs": 0.50, "fat": 0.30}
    }

    # UI設定
    CHART_COLORS = {
        "primary": "#667eea",
        "secondary": "#764ba2",
        "success": "#51cf66",
        "warning": "#ffd43b",
        "danger": "#ff6b6b",
        "info": "#4dabf7"
    }

    # セッション設定
    SESSION_TIMEOUT = 3600  # 1時間
    MAX_CHAT_HISTORY = 50   # チャット履歴の最大保存数

    @classmethod
    def validate(cls):
        """設定の検証"""
        if not cls.OPENAI_API_KEY:
            raise ValueError("OpenAI APIキーが設定されていません。.envファイルを確認してください。")
        return True

settings = Settings()

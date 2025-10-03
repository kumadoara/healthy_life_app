"""食品栄養素自動判定サービス"""

import openai
import json
import streamlit as st
from typing import Dict, Optional

class FoodNutritionService:
    def __init__(self, api_key: str):
        import os
        # 環境変数にAPIキーを設定
        os.environ["OPENAI_API_KEY"] = api_key
        # openaiクライアントの初期化（バージョン1.x対応）
        self.client = openai.OpenAI()

    def get_nutrition_info(self, food_name: str, amount: str = "100g") -> Optional[Dict]:
        """食品名から栄養情報を取得"""
        try:
            # 空の食品名の場合は低信頼度の結果を返す
            if not food_name or food_name.strip() == "":
                return {
                    "food_name": "",
                    "amount": amount,
                    "calories": 0,
                    "protein": 0,
                    "carbs": 0,
                    "fat": 0,
                    "fiber": 0,
                    "sodium": 0,
                    "confidence": 0.0
                }
            prompt = f"""
以下の食品の栄養情報を日本の一般的な食品成分表に基づいて提供してください。
食品名: {food_name}
分量: {amount}

以下のJSON形式で回答してください:
{{
"food_name": "食品名",
"amount": "分量",
"calories": カロリー数値,
"protein": タンパク質数値,
"carbs": 炭水化物数値,
"fat": 脂質数値,
"fiber": 食物繊維数値,
"sodium": ナトリウム数値,
"confidence": 0.0-1.0の信頼度
}}

注意:
- 数値のみを返し、単位は含めない
- 一般的な食品でない場合は confidence を低く設定
- 不明な場合は0を設定
- JSON形式以外の文字は含めない
"""

            response = self.client.chat.completions.create(
                model = "gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "あなたは栄養士です。正確な栄養情報をJSON形式で提供してください。JSON以外の文字は含めないでください。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1
            )

            if not response.choices:
                st.error("レスポンスが空です")
                return None

            content = response.choices[0].message.content.strip()

            # JSONを抽出・クリーニング
            if "```json" in content:
                json_str = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                json_str = content.split("```")[1].strip()
            else:
                json_str = content

            # 余分な文字を削除
            json_str = json_str.replace("```", "").strip()

            try:
                nutrition_data = json.loads(json_str)

                # 必須フィールドの検証
                required_fields = ['food_name', 'calories']
                if not all(field in nutrition_data for field in required_fields):
                    st.error("レスポンスに必須フィールドが不足しています")
                    return None

                return nutrition_data
            except json.JSONDecodeError as e:
                print(f"JSON解析エラー: {e}")
                print(f"Raw content: {content}")
                return None
            
        except Exception as e:
            st.error(f"栄養情報取得エラー: {str(e)}")
            return None
    
    def analyze_meal_image(self, image_data: bytes) -> Optional[Dict]:
        """食事画像を分析して栄養バランスを評価"""
        try:
            # 入力検証
            if image_data is None:
                st.error("画像が指定されていません")
                return None

            import base64

            # 画像をbase64エンコード
            base64_image = base64.b64encode(image_data).decode('utf-8')

            prompt = """
この食事画像を分析して、以下の項目について評価してください：

1. 含まれている食品の特定
2. 五大栄養素（炭水化物、タンパク質、脂質、ビタミン、ミネラル）の充足度
3. 栄養バランスの評価とアドバイス

以下のJSON形式で回答してください：
{
    "detected_foods": ["食品1", "食品2"],
    "nutrition_balance": {
        "carbs": 1-5の評価点,
        "protein": 1-5の評価点,
        "fat": 1-5の評価点,
        "vitamins": 1-5の評価点,
        "minerals": 1-5の評価点
    },
    "overall_score": 1-5の総合評価,
    "advice": "具体的なアドバイス",
    "missing_nutrients": ["不足している栄養素"],
    "recommendations": ["追加すべき食品の提案"]
}

JSON形式以外の文字は含めないでください。
"""
            response = self.client.chat.completions.create(
                model="gpt-4o",  # 最新のビジョンモデルを使用
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=1000,
                temperature=0.3
            )

            content = response.choices[0].message.content.strip()

            # JSONを抽出・クリーニング
            if "```json" in content:
                json_str = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                json_str = content.split("```")[1].strip()
            else:
                json_str = content
            
            json_str = json_str.replace("```", "").strip()

            try:
                analysis = json.loads(json_str)
                return analysis
            
            except json.JSONDecodeError as e:
                print(f"JSON解析エラー: {e}")
                print(f"Raw content: {content}")
                return None

        except Exception as e:
            # ビジョンモデルが利用できない場合の処理
            if "gpt-4" in str(e) or "vision" in str(e):
                st.warning("画像分析機能は現在利用できません。GPT-4 Visionの利用権限を確認してください。")
            elif "a bytes-like object is required" in str(e):
                st.error("画像が指定されていません")
            else:
                st.error(f"予期しないエラーが発生しました: {str(e)}")
            return None  
        
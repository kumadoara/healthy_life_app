"""トレーニングフィードバックサービス"""

import openai
import json
import streamlit as st
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

class WorkoutFeedbackService:
    def __init__(self, api_key: str):
        import os
        os.environ["OPENAI_API_KEY"] = api_key
        self.client = openai.OpenAI()

    def _convert_datetime_to_str(self, data: Any) -> Any:
        """datetimeオブジェクトを文字列に再帰的に変換"""
        if isinstance(data, dict):
            return {k: self._convert_datetime_to_str(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._convert_datetime_to_str(item) for item in data]
        elif isinstance(data, datetime):
            return data.isoformat()
        elif hasattr(data, 'isoformat'):  # その他のdatetimeライクなオブジェクト
            return data.isoformat()
        else:
            return data       
        
    def analyze_workout(self, workout_data: Dict, user_profile: Dict, recent_workouts: List[Dict] = None) -> Optional[Dict]:
        """単一のワークアウトを分析してフィードバックを提供"""
        try:
            # datetimeオブジェクトを文字列に変換
            clean_workout_data = self._convert_datetime_to_str(workout_data)
            clean_user_profile = self._convert_datetime_to_str(user_profile)
            clean_recent_workouts = self._convert_datetime_to_str(recent_workouts) if recent_workouts else None

            recent_context = ""
            if recent_workouts:
                recent_context = f"\n過去の運動履歴：\n{json.dumps(recent_workouts, ensure_ascii=False, indent=2)}"
            
            prompt = f"""
以下のトレーニング情報を分析して、詳細なフィードバックを提供してください。

ユーザープロフィール：
- 年齢: {user_profile.get('age', '不明')}歳
- 性別: {user_profile.get('gender', '不明')}
- 目標: {user_profile.get('goal', '不明')}
- 活動レベル: {user_profile.get('activity_level', '不明')}

今回のワークアウト：
- 運動名: {workout_data.get('exercise', '不明')}
- 時間: {workout_data.get('duration', 0)}分
- 強度: {workout_data.get('intensity', '不明')}
- 消費カロリー: {workout_data.get('calories', 0)}kcal
{recent_context}

以下のJSON形式で分析結果を返してください：
{{
    "performance_score": 1-10の評価点,
    "intensity_assessment": "強度の評価コメント",
    "duration_feedback": "時間に関するフィードバック",
    "calorie_assessment": "カロリー消費の評価",
    "form_tips": ["フォームに関するアドバイス"],
    "progression_advice": "次回への改善提案",
    "recovery_recommendation": "回復に関するアドバイス",
    "goal_alignment": "目標との整合性評価",
    "next_workout_suggestions": ["次回推奨メニュー"],
    "warning_flags": ["注意すべき点があれば"]
}}

注意：
- ユーザーの安全を最優先に考慮
- 目標に応じた具体的なアドバイス
- 過度な運動を推奨しない
- 個人差を考慮した現実的な提案
"""
            response = self.client.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=[
                    {"role": "system", "content": "あなたは経験豊富なパーソナルトレーナーです。安全で効果的なフィードバックを提供してください。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )

            content = response.choices[0].message.content
            if "```json" in content:
                json_str = content.split("```json")[1].split("```")[0]
            else:
                json_str = content

            feedback = json.loads(json_str)
            return feedback
        
        except Exception as e:
            st.error(f"ワークアウト分析エラー: {str(e)}")
            return None
    
    def analyze_weekly_progress(self, weekly_workouts: List[Dict], user_profile: Dict) -> Optional[Dict]:
        """週間の運動進捗を分析"""
        try:
            prompt = f"""
以下の週間トレーニングデータを分析して、進捗評価と改善提案を提供してください。

ユーザープロフィール：
- 目標: {user_profile.get('goal', '不明')}
- 活動レベル: {user_profile.get('activity_level', '不明')}

週間ワークアウト履歴：
{json.dumps(weekly_workouts, ensure_ascii=False, indent=2)}

以下のJSON形式で分析結果を返してください：
{{
    "weekly_score": 1-10の週間評価,
    "frequency_assessment": "頻度の評価",
    "variety_score": 1-5の種目多様性,
    "intensity_balance": "強度バランスの評価",
    "total_volume": "総運動量の評価",
    "goal_progress": "目標達成度",
    "strengths": ["良かった点"],
    "areas_for_improvement": ["改善点"],
    "next_week_plan": "来週の推奨プラン",
    "motivation_message": "モチベーション向上メッセージ"
}}
"""
            response = self.client.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=[
                    {"role": "system", "content": "あなたは経験豊富なフィットネスコーチです。建設的で励みになるフィードバックを提供してください。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4
            )

            content = response.choices[0].message.content
            if "```json" in content:
                json_str = content.split("```json")[1].split("```")[0]
            else:
                json_str = content
            
            analysis = json.loads(json_str)
            return analysis
        
        except Exception as e:
            st.error(f"週間分析エラー: {str(e)}")
            return None
        
"""
ユーザーデータモデル
ユーザーの基本情報と健康目標を管理
"""

from pydantic import BaseModel
from typing import Optional, List, Dict, Union, Any
from datetime import datetime

class UserProfile(BaseModel):
    """ユーザープロフィール情報を格納するクラス"""

    name: str
    age: int
    gender: str
    height: float   # cm
    weight: float   # kg
    activity_level: str
    goal: str
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class WorkoutRecord(BaseModel):
    """ワークアウト記録情報を格納するクラス"""
    date: datetime
    exercise: str
    duration: int #minutes
    calories: int
    intensity: str
    notes: Optional[str] = None

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class FoodItem(BaseModel):
    """食品アイテムの情報を格納するクラス"""
    name: str
    calories: float
    protein: float
    carbs: float
    fat: float

    class Config:
        # 文字列から数値への変換を許可
        str_to_float = True

class NutritionRecord(BaseModel):
    """栄養記録情報を格納するクラス"""
    date: datetime
    meal_type: str # 朝食、昼食、夕食、間食
    foods: List[Union[FoodItem, Dict[str, Any]]] # FoodItemまたは辞書形式を許可
    total_calories: float
    notes: Optional[str] = None

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
    def model_dump(self, **kwargs):
        """辞書形式でデータを出力（食品情報も辞書に変換）"""
        data = super().model_dump(**kwargs)
        #   foodsを辞書形式に統一
        if 'foods' in data:
            foods_list = []
            for food in data['foods']:
                if isinstance(food, dict):
                    foods_list.append(food)
                else:
                    # FoodItemオブジェクトの場合は辞書に変換
                    foods_list.append({
                        'name': food.name, 
                        'calories': food.calories,
                        'protein': food.protein,
                        'carbs': food.carbs,
                        'fat': food.fat
                    })
            data['foods'] = foods_list
        return data
        

"""
ユーザーデータモデル
ユーザーの基本情報と健康目標を管理
"""

from pydantic import BaseModel, ConfigDict, field_serializer, field_validator, Field
from typing import Optional, List, Dict, Union, Any
from datetime import datetime

class UserProfile(BaseModel):
    """ユーザープロフィール情報を格納するクラス"""

    model_config = ConfigDict()

    name: str
    age: int
    gender: str
    height: float   # cm
    weight: float   # kg
    activity_level: str
    goal: str
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    @field_serializer('created_at', 'updated_at')
    def serialize_datetime(self, value: datetime) -> str:
        return value.isoformat()

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError('名前は必須です')
        return v

    @field_validator('age')
    @classmethod
    def validate_age(cls, v):
        if v <= 0:
            raise ValueError('年齢は正の整数で入力してください')
        if v > 150:
            raise ValueError('年齢は150歳以下で入力してください')
        return v

    @field_validator('gender')
    @classmethod
    def validate_gender(cls, v):
        valid_genders = ['男性', '女性']
        if v not in valid_genders:
            raise ValueError('性別が不正です')
        return v

    @field_validator('height')
    @classmethod
    def validate_height(cls, v):
        if v <= 0:
            raise ValueError('身長は正の数値で入力してください')
        if v < 50 or v > 300:
            raise ValueError('身長は50cm以上300cm以下で入力してください')
        return v

    @field_validator('weight')
    @classmethod
    def validate_weight(cls, v):
        if v <= 0:
            raise ValueError('体重は正の数値で入力してください')
        if v > 500:
            raise ValueError('体重は500kg以下で入力してください')
        return v

    @field_validator('activity_level')
    @classmethod
    def validate_activity_level(cls, v):
        valid_levels = ['座りがち', '軽い運動', '適度な運動', '活発', '非常に活発']
        if v not in valid_levels:
            raise ValueError('活動レベルが不正です')
        return v

    @field_validator('goal')
    @classmethod
    def validate_goal(cls, v):
        valid_goals = ['体重維持', '減量', '増量', '筋肉増強', '健康維持']
        if v not in valid_goals:
            raise ValueError('目標が不正です')
        return v

class WorkoutRecord(BaseModel):
    """ワークアウト記録情報を格納するクラス"""

    model_config = ConfigDict()

    date: datetime
    exercise: str
    duration: int #minutes
    calories: int
    intensity: str
    notes: Optional[str] = None

    @field_serializer('date')
    def serialize_datetime(self, value: datetime) -> str:
        return value.isoformat()

    @field_validator('exercise')
    @classmethod
    def validate_exercise(cls, v):
        if not v or not v.strip():
            raise ValueError('運動種目は必須です')
        return v

    @field_validator('duration')
    @classmethod
    def validate_duration(cls, v):
        if v <= 0:
            raise ValueError('時間は正の整数で入力してください')
        if v > 600:  # 10時間
            raise ValueError('時間が長すぎます')
        return v

    @field_validator('calories')
    @classmethod
    def validate_calories(cls, v):
        if v < 0:
            raise ValueError('消費カロリーは0以上で入力してください')
        if v > 10000:
            raise ValueError('消費カロリーが大きすぎます')
        return v

    @field_validator('intensity')
    @classmethod
    def validate_intensity(cls, v):
        valid_intensities = ['低', '中', '高']
        if v not in valid_intensities:
            raise ValueError('強度は「低」「中」「高」のいずれかで入力してください')
        return v

    @field_validator('notes')
    @classmethod
    def validate_notes(cls, v):
        if v is not None and len(v) > 500:
            raise ValueError('メモは500文字以内で入力してください')
        return v

class FoodItem(BaseModel):
    """食品アイテムの情報を格納するクラス"""

    model_config = ConfigDict(str_to_float=True)

    name: str
    calories: float
    protein: float
    carbs: float
    fat: float

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError('食品名は必須です')
        return v

    @field_validator('calories', 'protein', 'carbs', 'fat')
    @classmethod
    def validate_nutrition_values(cls, v):
        if v < 0:
            raise ValueError('栄養値は0以上で入力してください')
        return v

class NutritionRecord(BaseModel):
    """栄養記録情報を格納するクラス"""

    model_config = ConfigDict()

    date: datetime
    meal_type: str # 朝食、昼食、夕食、間食
    foods: List[Union[FoodItem, Dict[str, Any]]] # FoodItemまたは辞書形式を許可
    total_calories: float
    notes: Optional[str] = None

    @field_serializer('date')
    def serialize_datetime(self, value: datetime) -> str:
        return value.isoformat()

    @field_validator('date')
    @classmethod
    def validate_date(cls, v):
        from datetime import datetime
        if v > datetime.now():
            raise ValueError('未来の日付は指定できません')
        return v

    @field_validator('meal_type')
    @classmethod
    def validate_meal_type(cls, v):
        if not v or not v.strip():
            raise ValueError('食事タイプは必須です')
        valid_meal_types = ['朝食', '昼食', '夕食', '間食', '夜食']
        if v not in valid_meal_types:
            raise ValueError('食事タイプが不正です')
        return v

    @field_validator('total_calories')
    @classmethod
    def validate_total_calories(cls, v):
        if v is None:
            raise ValueError('数値型のカロリーを入力してください')
        if isinstance(v, str):
            raise ValueError('数値型のカロリーを入力してください')
        if v < 0:
            raise ValueError('総カロリーは0以上で入力してください')
        return v

    @field_validator('foods')
    @classmethod
    def validate_foods(cls, v):
        if v is None:
            raise ValueError('食品リストは必須です')
        if not isinstance(v, list):
            raise ValueError('食品リストの形式が不正です')
        return v
    
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
        

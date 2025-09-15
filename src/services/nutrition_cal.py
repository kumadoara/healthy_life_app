"""
健康計算機能サービス
BMI、カロリー、栄養素などの計算を担当
"""
from typing import Dict, Tuple
from models.user_profile import UserProfile

class HealthCalculator:
    """健康関連の計算を行うクラス"""

    # 活動レベル別の活動係数
    ACTIVITY_MULTIPLIERS = {
        "sedentary": 1.2,   # 運動しない（デスクワーク中心）
        "light": 1.375,     # 軽い運動（週1-3回）
        "moderate": 1.55,   # 中程度の運動（週3-5回）
        "active": 1.725,    # 活発な運動（週6-7回）
        "very_active": 1.9, # 非常に活発（1日2回の運動、肉体労働） 
    }

    @staticmethod
    def calculate_bmi(height: int, weight: int) -> float:
        """BMI（体格指数）を計算
        
        Args:
            height: 身長（cm）
            weight: 体重（kg）

        Returns:
            BMI値（小数点1桁）
        """
        height_m = height / 100
        bmi = weight / (height_m ** 2)
        return round(bmi, 1)
    
    @staticmethod
    def get_bmi_category(bmi: float) -> str:
        """BMI値からカテゴリを判定
        
        Args:
            bmi: BMI値

        Returns:
            BMIカテゴリの文字列
        """ 
        if bmi < 18.5:
            return "低体重"
        elif bmi < 25:
            return "普通体重"
        elif bmi < 30:
            return "肥満（1度）"
        elif bmi < 35:
            return "肥満（2度）"
        else:
            return "肥満（3度）"
    
    @staticmethod
    def calculate_bmr(profile: UserProfile, gender: str = "male") -> int:
        """基礎代謝率（BMR）を計算（Harris-Benedict方程式）
        
        Args:
            profile: ユーザープロフィール
            gender: 性別（"male" or "female"）
        
        Returns:
            基礎代謝率（kcal/日）       
        """
        if gender == "male":
            # 男性: BMR = 88.362 + (13.397 × 体重kg) + (4.799 × 身長cm) - (5.677 × 年齢)
            bmr = 88.362 + (13.397 * profile.weight) + (4.799 * profile.height) - (5.677 * profile.age)
        else:
            # 女性: BMR = 447.593 + (9.247 × 体重kg) + (3.098 × 身長cm) - (4.330 × 年齢)
            bmr = 447.593 + (9.247 * profile.weight) + (3.098 * profile.height) - (4.330 * profile.age)
        
        return round(bmr)
    
    @classmethod
    def calculate_daily_calories(cls, profile: UserProfile, gender: str = "male") -> int:
        """1日の総消費カロリーを計算
        
        Args:
            profile: ユーザープロフィール
            gender: 性別
        
        Returns:
            1日の総消費カロリー（kcal)       
        """
        bmr = cls.calculate_bmr(profile, gender)
        multiplier = cls.ACTIVITY_MULTIPLIERS.get(profile.activity_level, 1.725)
        return round(bmr * multiplier)
    
    @staticmethod
    def calculate_target_calories(daily_calories: int, goal: str) -> int:
        """目標に応じた推奨カロリーを計算
        
        Args:
            daily_calories: 1日の消費カロリー
            goal: 目標（"lose", "maintain", "gain"）
        
        Returns:
            推奨カロリー（kcal）  
        """        
        if goal == "lose":
            return daily_calories - 300  # 減量: -300kcal
        elif goal == "gain":
            return daily_calories + 300  # 増量: +300kcal
        else:
            return daily_calories   # 維持
    
    @staticmethod
    def calculate_protein_requirement(weight: int, goal: str, activity_level: str = "active") -> int:
        """タンパク質必要量を計算
        
        Args:
            weight: 体重（kg）
            goal: 目標
            activity_level: 活動レベル
        
        Returns:
            1日のタンパク質必要量（g)       
        """ 
        if goal == "gain" or activity_level in ["active", "very_active"]:
            # 筋肉増量または高活動: 体重1kgあたり2.0-2.2g
            protein_per_kg = 2.0
        elif goal == "lose":
            # 減量: 体重1kgあたり1.6-1.8g
            protein_per_kg = 1.8
        else:
            # 維持: 体重1kgあたり1.2-1.6g
            protein_per_kg = 1.4
        
        return round(weight * protein_per_kg)
    
    @staticmethod
    def calculate_macronutrients(total_calories: int) -> Dict[str, int]:
        """マクロ栄養素の配分を計算
        
        Args:
            total_calories: 総カロリー
        
        Returns:
            各栄養素のグラム数を含む辞書       
        """ 
        return {
            "carbs": round(total_calories * 0.5 / 4),   # 炭水化物: 50%（4kcal/g）
            "protein": round(total_calories * 0.2 / 4), # タンパク質: 20%（4kcal/g）
            "fat": round(total_calories * 0.3 / 9),     # 脂質: 30%（9kcal/g） 
        }
    
    @classmethod
    def get_health_stats(cls, profile: UserProfile, gender: str = "male") -> Dict[str, any]:
        """総合的な健康統計を計算
        
        Args:
            profile: ユーザープロフィール
            gender: 性別
        
        Returns:
            健康統計を含む辞書       
        """ 
        bmi = cls.calculate_bmi(profile.height, profile.weight)
        bmr = cls.calculate_bmr(profile, gender)
        daily_calories = cls.calculate_daily_calories(profile, gender)
        target_calories = cls.calculate_target_calories(daily_calories, profile.goal)
        protein_requirement = cls.calculate_protein_requirement(
            profile.weight, profile.goal, profile.activity_level
        )
        macronutrients = cls.calculate_macronutrients(target_calories)

        return {
            "bmi": bmi,
            "bmi_category": cls.get_bmi_category(bmi), 
            "bmr": bmr,
            "daily_calories": daily_calories,
            "target_calories": target_calories,
            "protein_requirement": protein_requirement,
            "macronutrients": macronutrients,
        }
    
    @staticmethod
    def calculate_ideal_weight_range(height: int) -> Tuple[int, int]:
        """理想体重範囲を計算（BMI 18.5-24.9基準）
        
        Args:
            height: 身長（cm）
        
        Returns:
            （最小理想体重、最大理想体重）のタプル       
        """ 
        height_m = height / 100
        min_weight = round(18.5 * (height_m ** 2))
        max_weight = round(24.9 * (height_m ** 2))
        return min_weight, max_weight
    
    @staticmethod
    def estimate_calories_burned(exercise: str, weight: int, duration: int) -> int:
        """運動による消費カロリーを推定
        
        Args:
            exercise: 運動名
            weight: 体重（kg）
            duration: 時間（分）

        Returns:
            推定消費カロリー（kcal）       
        """ 
        # MET値（安静時代謝の何倍かを表す）
        met_values = {
            "ウォーキング": 3.5,
            "ランニング": 8.0,
            "サイクリング": 7.5,
            "水泳": 8.0,
            "筋トレ": 4.0,
            "なわとび": 12.3,
            "ヨガ": 2.5,
            "エアロビクス": 7.3,
            "テニス": 7.3,
            "バスケットボール": 8.0,
            "サッカー": 7.0,
            "野球":5.0,
        }

        met = met_values.get(exercise, 4.0)     # デフォルト値

        # 消費カロリー = MET × 体重(kg) × 時間(h)
        calories = met * weight * (duration / 60)
        return round(calories)

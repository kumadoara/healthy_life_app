def calculate_bmi(height: float, weight: float) -> float:
    """BMIを計算"""
    height_m = height / 100
    return weight / (height_m ** 2)

def calculate_bmr(height: float, weight: float, age: int, gender: str) -> float:
    """基礎代謝率を計算（Harris-Benedict方程式）"""
    if gender == "男性":
        # 男性: BMR = 88.362 + (13.397 × 体重kg) + (4.799 × 身長cm) - (5.677 × 年齢)
        return 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age)
    else:
        # 女性: BMR = 447.593 + (9.247 × 体重kg) + (3.098 × 身長cm) - (4.330 × 年齢)
        return 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age)

def calculate_tdee(bmr: float, activity_level: str) -> float:
    """総消費カロリーを計算"""
    multipliers = {
        "座りがち": 1.2,   # 運動しない（デスクワーク中心）
        "軽い運動": 1.375,     # 軽い運動（週1-3回）
        "適度な運動": 1.55,   # 適度な運動（週3-5回）
        "活発": 1.725,    # 活発（週6-7回）
        "非常に活発": 1.9, # 非常に活発（1日2回の運動、肉体労働） 
    }
    return bmr * multipliers.get(activity_level, 1.55)

def calculate_macros(calories: float, goal: str) -> dict:
    """マクロ栄養素の配分を計算"""
    if goal == "減量":
        protein_ratio = 0.30
        carb_ratio = 0.35
        fat_ratio = 0.35
    elif goal == "増量" or goal == "筋肉増強":
        protein_ratio = 0.25
        carb_ratio = 0.45
        fat_ratio = 0.30
    else:   #  維持
        protein_ratio = 0.20
        carb_ratio = 0.50
        fat_ratio = 0.30
    
    return {
        "protein": {
            "grams": (calories * protein_ratio) / 4, 
            "calories": calories * protein_ratio
        },
        "carbs": {
            "grams": (calories * carb_ratio) / 4,
            "calories": calories * carb_ratio
        },
        "fat": {
            "grams": (calories * fat_ratio) / 9,
            "calories": calories * fat_ratio
        }
    }

def format_date_jp(date) -> str:
    """日付を日本語形式でフォーマット"""
    return date.strftime("%Y年%m月%d日")

def get_bmi_category(bmi: float) -> tuple:
    """BMIカテゴリーを取得"""
    if bmi < 18.5:
        return "低体重", "🔵"  
    elif bmi < 25:
        return "標準", "🟢"
    elif bmi < 30:
        return "やや肥満", "🟡"
    else:
        return "肥満", "🔴"
      
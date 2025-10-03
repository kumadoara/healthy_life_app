def calculate_bmi(height: float, weight: float) -> float:
    """
    BMIを計算する関数。
    Args:
        height (float): 身長（cm単位）
        weight (float): 体重（kg単位）
    Returns:
        float: BMI値
    Raises:
        TypeError: height, weight が数値でない場合
        ZeroDivisionError: 身長が 0 または負数の場合
        OverflowError: 計算がオーバーフローした場合
    """

    # 型チェック
    if not isinstance(height, (int, float)) or not isinstance(weight, (int, float)):
        raise TypeError("身長と体重は数値で入力してください")

    # 身長が 0 または負数は無効
    if height <= 0:
        raise ZeroDivisionError("身長は正の数値で入力してください")

    try:
        height_m = height / 100
        bmi = weight / (height_m ** 2)
    except OverflowError:
        raise OverflowError("BMI計算で数値が大きすぎます")

    return bmi

def calculate_bmr(height: float, weight: float, age: int, gender: str) -> float:
    """
    基礎代謝量 (BMR) を計算する関数（Harris-Benedict方程式）
    Args:
        height (float): 身長（cm）
        weight (float): 体重（kg）
        age (int): 年齢
        gender (str): 性別 ("男性" または "女性")
    Returns:
        float: 基礎代謝量 (kcal)
    Raises:
        TypeError: 引数が数値でない場合
        ValueError: 性別が無効な場合
    """
    if not isinstance(height, (int, float)) or not isinstance(weight, (int, float)) or not isinstance(age, int):
        raise TypeError("身長・体重・年齢は数値で入力してください")

    if height <= 0 or weight <= 0 or age <= 0:
        raise ValueError("身長・体重・年齢は正の数値で入力してください")

    gender = str(gender)
    if gender not in ["男性", "女性"]:
        raise ValueError("性別は「男性」または「女性」を指定してください")

    try:
        if gender == "男性":
            # 男性: BMR = 88.362 + (13.397 × 体重kg) + (4.799 × 身長cm) - (5.677 × 年齢)
            return 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age)
        else:
            # 女性: BMR = 447.593 + (9.247 × 体重kg) + (3.098 × 身長cm) - (4.330 × 年齢)
            return 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age)
    except OverflowError:
        raise OverflowError("BMR計算で数値が大きすぎます")      

def calculate_tdee(bmr: float, activity_level: str) -> float:
    """
    TDEE（総消費エネルギー量）を計算する。

    Args:
        bmr (float): 基礎代謝量
        activity_level (str): 活動レベル（座りがち, 軽い運動, 適度な運動, 活発, 非常に活発）

    Returns:
        float: TDEE 値

    Raises:
        TypeError: BMR または 活動レベルの型が不正な場合
        ValueError: 値が不正な場合
        OverflowError: 計算オーバーフロー
    """
    # --- 型チェック ---
    if not isinstance(bmr, (int, float)):
        raise TypeError("BMRは数値で入力してください")

    if not isinstance(activity_level, str):
        raise TypeError("活動レベルは文字列で指定してください")

    if activity_level.strip() == "":
        raise ValueError("活動レベルは空文字では指定できません")

    # --- 値チェック ---
    if bmr < 0:
        raise ValueError("BMRは正の数値で入力してください")
    
    # --- 活動レベルごとの係数 ---
    multipliers = {
        "座りがち": 1.2,   # 運動しない（デスクワーク中心）
        "軽い運動": 1.375,     # 軽い運動（週1-3回）
        "適度な運動": 1.55,   # 適度な運動（週3-5回）
        "活発": 1.725,    # 活発（週6-7回）
        "非常に活発": 1.9, # 非常に活発（1日2回の運動、肉体労働） 
    }
    multiplier = multipliers.get(activity_level, 1.55)  # 未知ならデフォルト1.55
    # --- 計算 ---
    try:
        tdee = bmr * multiplier
    except OverflowError:
        raise OverflowError("TDEE計算で数値が大きすぎます")

    return tdee    

def calculate_macros(calories: float, goal: str) -> dict:
    """
    1日のカロリーと目標に基づきマクロ栄養素を計算する。

    Args:
        calories (float): 1日の総摂取カロリー
        goal (str): 目標（減量, 増量, 筋肉増強, 体重維持, 健康維持）

    Returns:
        dict: 各マクロ栄養素のカロリーとグラム数
    Raises:
        TypeError: 引数の型が不正な場合
        ValueError: 値が不正な場合
        OverflowError: 計算オーバーフロー
    """
    # --- 型チェック ---
    if not isinstance(calories, (int, float)):
        raise TypeError("カロリーは数値で入力してください")

    if not isinstance(goal, str):
        raise TypeError("目標は文字列で指定してください")

    if goal.strip() == "":
        raise ValueError("目標は空文字では指定できません")

    # --- 値チェック ---
    if calories < 0:
        raise ValueError("カロリーは正の数値で入力してください")

    # --- 目標ごとの比率設定 ---
    ratios = {
        "減量": {"protein": 0.30, "carbs": 0.35, "fat": 0.35},
        "増量": {"protein": 0.25, "carbs": 0.45, "fat": 0.30},
        "筋肉増強": {"protein": 0.25, "carbs": 0.45, "fat": 0.30},
        "体重維持": {"protein": 0.20, "carbs": 0.50, "fat": 0.30},
        "健康維持": {"protein": 0.20, "carbs": 0.50, "fat": 0.30},
    }

    if goal not in ratios:
        # 未知の目標は「体重維持」の比率を使用
        selected_ratios = ratios["体重維持"]
    else:
        selected_ratios = ratios[goal]

    # --- 計算 ---
    try:
        macros = {}
        for macro, ratio in selected_ratios.items():
            macro_calories = calories * ratio
            if macro == "protein" or macro == "carbs":
                grams = macro_calories / 4
            elif macro == "fat":
                grams = macro_calories / 9
            else:
                grams = 0.0
            macros[macro] = {"calories": macro_calories, "grams": grams}
    except OverflowError:
        raise OverflowError("マクロ計算で数値が大きすぎます")

    return macros

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
      
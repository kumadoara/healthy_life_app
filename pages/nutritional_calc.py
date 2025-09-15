"""栄養計算ページ"""

import streamlit as st
import plotly.graph_objects as go
from src.utils.helpers import calculate_bmi, calculate_bmr, calculate_tdee, calculate_macros

st.set_page_config(page_title="栄養計算機", page_icon="🧮", layout="wide")

# プロフィールチェック
if 'user_profile' not in st.session_state or st.session_state.user_profile is None:
    st.warning("⚠️  プロフィールを設定してください")
    st.stop()

st.title("🧮  栄養計算機")
st.markdown("あなたの目標に最適な栄養摂取量を計算します")

profile = st.session_state.user_profile

# 基本情報の表示
col1, col2, col3 = st.columns(3)

with col1:
    st.info(f"""
    **プロフィール**
    - 年齢: {profile.age}歳
    - 性別: {profile.gender}
    - 身長: {profile.height}cm
    - 体重: {profile.weight}kg
    """)

with col2:
    bmi = calculate_bmi(profile.height, profile.weight)
    from src.utils.helpers import get_bmi_category
    category, emoji = get_bmi_category(bmi)
    st.info(f"""
    **身体指標**
    - BMI: {bmi:.1f} {emoji} {category}
    - 理想体重: {22 * (profile.height/100)**2:.1f}kg
    - 活動レベル: {profile.activity_level}
    """)

with col3:
    st.info(f"""
    **目標設定**
    - 現在の目標: {profile.goal}
    - 推奨期間: {
        '3-6ヶ月' if profile.goal == '減量' else
        '6-12ヶ月' if profile.goal == '増量' else
        '継続的' if profile.goal == '健康維持' else
        '4-8ヶ月'
    }
    """)

st.markdown("---")

# カロリー計算
st.subheader("📊  カロリー計算")

bmr = calculate_bmr(profile.height, profile.weight, profile.age, profile.gender)
tdee = calculate_tdee(bmr, profile.activity_level)

# 目標別カロリー調整
if profile.goal == "減量":
    target_calories = tdee - 500
    adjustment_text = "1日500kcal削減（週0.5kg減量ペース）"
elif profile.goal == "増量" or profile.goal == "筋肉増強":
    target_calories = tdee + 500
    adjustment_text = "1日500kcal増加（週0.5kg増量ペース）"
else:
    target_calories = tdee
    adjustment_text = "カロリー維持"

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("基礎代謝量（BMR)", f"{bmr:.0f} kcal",
              help="安静時に消費されるカロリー")

with col2:
    st.metric("総消費カロリー（TDEE)", f"{tdee:.0f} kcal",
              help="活動を含めた1日の総消費カロリー")

with col3:
    st.metric("目標摂取カロリー", f"{target_calories:.0f} kcal",
              delta=adjustment_text)

# マクロ栄養素の計算
st.markdown("---")
st.subheader("🥗 マクロ栄養素の配分")

macros = calculate_macros(target_calories, profile.goal)

col1, col2 = st.columns([2, 1])

with col1:
    # ドーナツチャート
    fig = go.Figure(data=[go.Pie(
        labels=['タンパク質', '炭水化物', '脂質'],
        values=[
            macros['protein']['calories'],
            macros['carbs']['calories'],
            macros['fat']['calories']
        ],
        hole=0.3,
        marker_colors = ['#ff6b6b', '#4dabf7', '#51cf66']
    )])

    fig.update_layout(
        title = "カロリー配分",
        height=400,
        annotations = [dict(text=f'{target_calories:.0f}<br>kcal',
                            x=0.5, y=0.5, font_size=20, showarrow=False)]
    )

    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown("### 📋 推奨摂取量")

    st.markdown(f"""
    **タンパク質**🥩
    - {macros['protein']['grams']:.0f}g
    - {macros['protein']['calories']:.0f} kal
    -体重1kgあたり1:{macros['protein']['grams']/profile.weight:.1f}g
    
    **炭水化物**🍚
    - {macros['carbs']['grams']:.0f}g
    - {macros['carbs']['calories']:.0f} kcal

    **脂質**🥑
    - {macros['fat']['grams']:.0f}g
    - {macros['fat']['calories']:.0f} kcal
    """)

# 食事プランの提案
st.markdown("---")
st.subheader("🍽️ 1日の食事配分案")

meal_distribution = {
    "朝食": 0.25,
    "昼食": 0.35,
    "夕食": 0.30,
    "間食": 0.10
}

col1, col2, col3, col4 = st.columns(4)

with col1:
    breakfast_cal = target_calories * meal_distribution["朝食"]
    st.metric("🌅 朝食", f"{breakfast_cal:.0f} kcal")
    st.caption(f"タンパク質: {macros['protein']['grams']*0.25:.0f}g")

with col2:
    lunch_cal = target_calories * meal_distribution["昼食"]
    st.metric("☀️ 昼食", f"{lunch_cal:.0f} kcal")
    st.caption(f"タンパク質: {macros['protein']['grams']*0.35:.0f}g")

with col3:
    dinner_cal = target_calories * meal_distribution["夕食"]
    st.metric("🌙 夕食", f"{dinner_cal:.0f} kcal")
    st.caption(f"タンパク質: {macros['protein']['grams']*0.30:.0f}g")
   
with col4:
    snack_cal = target_calories * meal_distribution["間食"]
    st.metric("🍎 間食", f"{snack_cal:.0f} kcal")
    st.caption(f"タンパク質: {macros['protein']['grams']*0.10:.0f}g")

# 食品提案
st.markdown("---")
st.subheader("🥦 おすすめ食品")

tab1, tab2, tab3 = st.tabs(["高タンパク食品", "良質な炭水化物", "健康的な脂質"])

with tab1:
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        **動物性タンパク質**
        - 鶏胸肉（皮なし）: 23g/100g
        - 牛赤身肉: 22g/100g                
        - 卵: 13g/100g
        - サーモン: 20g/100g
        """)
    with col2:
        st.markdown("""
        **植物性タンパク質**
        - 豆腐: 8g/100g
        - 納豆: 17g/100g                
        - レンズ豆: 9g/100g
        - キヌア: 4g/100g
        """)
    with col3:
        st.markdown("""
        **プロテインサプリ**
        - ホエイプロテイン: 20-25g/スクープ
        - カゼインプロテイン              
        - ソイプロテイン: 20-25g/スクープ
        - 植物性プロテイン: 15-20g/スクープ
        """)

with tab2:
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        **全粒穀物**
        - 玄米: 低GI、食物繊維豊富
        - オートミール: β-グルカン含有          
        - 全粒粉パン: ビタミンB群
        - そば: ルチン含有
        """)
    with col2:
        st.markdown("""
        **野菜・果物**
        - さつまいも: ビタミンA豊富
        - バナナ: カリウム豊富           
        - ブロッコリー: ビタミンC
        - ほうれん草: 鉄分豊富
        """)
    with col3:
        st.markdown("""
        **豆類**
        - ひよこ豆: タンパク質も豊富
        - 黒豆: アントシアニン              
        - えんどう豆: 食物繊維
        - あずき: ポリフェノール
        """)

with tab3:
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        **不飽和脂肪酸**
        - アボカド: オレイン酸
        - オリーブオイル: 一価不飽和脂肪酸
        - アーモンド: ビタミンE
        - くるみ: オメガ3脂肪酸
        """)
    with col2:
        st.markdown("""
        **魚の脂質**
        - サーモン: DHA/EPA
        - サバ: オメガ3豊富           
        - マグロ: 良質な脂質
        - いわし: カルシウムも豊富
        """)
    with col3:
        st.markdown("""
        **種子類**
        - チアシード: オメガ3
        - フラックスシード: リグナン              
        - かぼちゃの種: 亜鉛
        - ひまわりの種: ビタミンE
        """)

# 水分摂取の推奨
st.markdown("---")
st.subheader("💧 水分摂取目標")

water_base = profile.weight * 35  #ml
if profile.activity_level in ["活発", "非常に活発"]:
    water_recommendation = water_base * 1.3
elif profile.activity_level in ["適度な運動"]:
    water_recommendation = water_base * 1.15
else:
    water_recommendation = water_base

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("基本必要量", f"{water_base:.0f} ml", help="体重×35ml")
with col2:
    st.metric("活動調整後", f"{water_recommendation:.0f} ml", help="活動レベルを考慮")
with col3:
    st.metric("コップ換算", f"{water_recommendation/200:.0f} 杯", help="200ml/杯として計算")

# アドバイスセクション
st.markdown("---")
st.subheader("💡 パーソナライズされたアドバイス")

if profile.goal == "減量":
    st.success("""
    ### 🎯 減量成功のポイント
    
    1. **カロリー管理**: 1日500kcalの削減で週0.5kgの健康的な減量ペース
    2. **タンパク質重視**: 筋肉量を維持しながら脂肪を減らすため、体重1kgあたり1.5-2gのタンパク質摂取
    3. **食事回数**: 3-4回に分けて食べることで血糖値を安定させる
    4. **運動との組み合わせ**: 有酸素運動と筋トレの組み合わせが効果的
    5. **水分摂取**: 代謝を活発にし、満腹感を得やすくする
    
    ⚠️ **注意点**: 極端な食事制限は避け、バランスの良い食事を心がけましょう           
    """)

elif profile.goal == "増量" or profile.goal == "筋肉増強":
    st.success("""
    ### 💪 増量・筋肉増強のポイント
    
    1. **カロリー摂取**: 消費カロリー+500kcalで健康的な増量
    2. **タンパク質**: 体重1kgあたり1.8-2.2gを目標に
    3. **トレーニング前後の栄養**: 運動前後の炭水化物とタンパク質摂取が重要
    4. **頻繁な食事**: 3時間おきに栄養補給することで筋肉合成を促進
    5. **良質な睡眠**: 成長ホルモンの分泌を促す7-9時間の睡眠
    
    📈 **プログレッシブオーバーロード**: 徐々に負荷を増やすトレーニングが必須
    """) 

else:
    st.success("""
    ### 🌟 健康維持のポイント
    
    1. **バランス**: 三大栄養素をバランスよく摂取
    2. **食事の質**: 加工食品を減らし、自然食品を増やす
    3. **規則正しい食事**: 同じ時間帯に食事を摂る習慣
    4. **適度な運動**: 週150分の中強度運動または75分の高強度運動
    5. **ストレス管理**: 過食や不規則な食事の原因となるストレスを管理
    
    ✨ **長期的視点**: 短期的な変化より持続可能な習慣づくりを重視
    """)

# サプリメント提案
with st.expander("💊 サプリメント提案（任意）"):
    st.markdown(f"""
    ### あなたの目標「{profile.goal}」に基づく提案

    **基本サプリメント**
    - マルチビタミン: 栄養バランスの基礎
    - オメガ3脂肪酸: 抗炎症作用、心血管健康
    - ビタミンD: {'特に重要' if profile.activity_level == '座りがち' else '免疫機能サポート'}

    **目標別サプリメント**
    {
    '''
    - プロテインパウダー: 手軽なタンパク質補給
    - BCAA: 筋肉の分解を防ぐ
    - L-カルニチン: 脂肪燃焼をサポート'''
        if profile.goal == '減量' else
    '''
    - クレアチン: 筋力・筋肉量の増加
    - プロテインパウダー: 必須のタンパク質補給
    - β-アラニン: 筋持久力の向上''' 
        if profile.goal in ['増量', '筋肉増強'] else
    '''
    - プロバイオティクス: 腸内環境の改善
    - マグネシウム: エネルギー代謝
    - ビタミンB群: 疲労回復'''
    }

    ⚠️ **注意**: サプリメントは食事の補助です。まずは食事から栄養を摂ることを優先してください。
    """)

# フッター情報
st.markdown("---")
st.info("""
📚 **参考情報**
- BMR計算: Harris-Benedict方程式（改訂版）を使用
- TDEE計算: 活動レベル別の標準的な係数を適用
- マクロ栄養素: 目標に応じた最適な配分を計算
- 水分摂取: 体重と活動レベルに基づく推奨量

💡 これらの数値は目安です。個人差があるため、実際の体の反応を見ながら調整してください。
""")

import streamlit as st
import json
from pathlib import Path
from datetime import datetime
from src.models.user_profile import UserProfile
from src.services.data_manager import DataManager
from src.utils.helpers import calculate_bmi, calculate_bmr
from dotenv import load_dotenv

import os

# 環境変数の読み込み
load_dotenv()

# ページ設定
st.set_page_config(
    page_title="ヘルシーライフ",
    page_icon="🏃",
    layout="wide",
    initial_sidebar_state="expanded"
)

# セッション初期化
if 'user_profile' not in st.session_state:
    st.session_state.user_profile = None
if 'data_manager' not in st.session_state:
    st.session_state.data_manager = DataManager()

# カスタムCSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding: 2rem 0;
    }
    .stat-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        color: #667eea;
    }
    .metric-label {
        color: #718096;
        font-size: 0.9rem;        
    }
</style>
""", unsafe_allow_html=True)

# ヘッダー
st.markdown('<h1 class="main-header">🏃 ヘルシーライフ</h1>', unsafe_allow_html=True)

# サイドバー - プロフィール設定
with st.sidebar:
    st.header("⚙️  プロフィール設定")

    with st.form("profile_form"):
        name = st.text_input(
            "🧕  名前", 
            value=st.session_state.user_profile.name if st.session_state.user_profile else ""
        )
        age = st.number_input(
            "🎂  年齢", 
            min_value=10, 
            max_value=100, 
            value=int(st.session_state.user_profile.age) if st.session_state.user_profile else 30,
            step=1
        )
        gender = st.selectbox(
            "⚧  性別", 
            ["男性", "女性"], 
            index=0 if not st.session_state.user_profile or st.session_state.user_profile.gender == "男性" else 1
        )
        height = st.number_input(
            "📏  身長（cm）", 
            min_value=100.0, 
            max_value=250.0, 
            value=float(st.session_state.user_profile.height) if st.session_state.user_profile else 175.0,
            step = 0.1,
            format="%.1f"
        )
        weight = st.number_input(
            "⚖️  体重（kg）", 
            min_value=30.0, 
            max_value=200.0, 
            value=float(st.session_state.user_profile.weight) if st.session_state.user_profile else 70.0,
            step = 0.1,
            format="%.1f"
        )

        activity_level = st.select_slider(
            "🏃  活動レベル",
            options=["座りがち", "軽い運動", "適度な運動", "活発", "非常に活発"],
            value=st.session_state.user_profile.activity_level if st.session_state.user_profile else "適度な運動"
        )

        goal = st.selectbox(
            "🚩  目標",
            ["体重維持", "減量", "増量", "筋肉増強", "健康維持"],
            index=0 if not st.session_state.user_profile else ["体重維持", "減量", "増量", "筋肉増強", "健康維持"].index(st.session_state.user_profile.goal)
        )

        submitted = st.form_submit_button("💾  保存", use_container_width=True)
    
        if submitted:
            profile = UserProfile(
                name=name,
                age=age,
                gender=gender,
                height=height,
                weight=weight,
                activity_level=activity_level,
                goal=goal
            )
            st.session_state.user_profile = profile
            st.session_state.data_manager.save_profile(profile)
            st.success("✅  プロフィールを保存しました！")
            st.rerun()

# メインコンテンツ
if st.session_state.user_profile:
    profile = st.session_state.user_profile

    # 統計情報の表示
    st.subheader("📊  あなたの健康統計")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
            bmi = calculate_bmi(profile.height, profile.weight)
            st.metric("BMI", f"{bmi:.1f}", delta=None)
            if bmi < 18.5:
                st.caption("🔵  低体重")
            elif bmi < 25:
                st.caption("🟢  標準")
            elif bmi < 30:
                st.caption("🟡  やや肥満")
            else:
                st.caption("🔴  肥満")
    with col2:
        bmr = calculate_bmr(profile.height, profile.weight, profile.age, profile.gender)
        st.metric("基礎代謝", f"{bmr:.0f} kcal", delta=None)
    
    with col3:
        activity_multiplier = {
            "座りがち": 1.2,   # 運動しない（デスクワーク中心）
            "軽い運動": 1.375,     # 軽い運動（週1-3回）
            "適度な運動": 1.55,   # 中程度の運動（週3-5回）
            "活発": 1.725,    # 活発な運動（週6-7回）
            "非常に活発": 1.9, # 非常に活発（1日2回の運動、肉体労働） 
        }
        tdee = bmr * activity_multiplier.get(profile.activity_level, 1.55)
        st.metric("1日の消費カロリー", f"{tdee:.0f} kcal", delta=None)

    with col4:
        ideal_weight = 22 * (profile.height/100) ** 2
        weight_diff = profile.weight - ideal_weight
        st.metric("理想体重との差", f"{abs(weight_diff):.1f} kg",
                  delta=f"{weight_diff:+.1f} kg" if weight_diff != 0 else "完璧！")

    # 機能紹介
    st.markdown("---")
    st.subheader("🚀  利用可能な機能")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        ### 🍎  栄養相談チャット
        - AIによるパーソナライズされた栄養アドバイス
        - ダイエット戦略の提案
        - カロリー計算のサポート
        
        ### 💪  トレーニングチャット
        - レベル別トレーニングメニュー
        - 正しいフォームの指導
        - 目標に応じたプログラム作成
        """)
        
    with col2:
        st.markdown("""
        ### 📊  トレーニング記録
        - 運動履歴の管理
        - 進捗の可視化
        - 目標達成度の追跡
        
        ### 🧮  栄養計算機
        - 必要カロリーの自動計算
        - 栄養素バランスの最適化
        - 食事プランの提案
        """)

        st.info("👈  左のサイドバーから各機能にアクセスできます")

else:
    st.warning("⚠️  まずは左のサイドバーでプロフィールを設定してください")
    st.markdown("""
        ### 🚩  このアプリで出来ること
                
        1. **パーソナライズされた健康管理** - あなたの体格と目標に合わせたアドバイス
        2. **AIチャットサポート** - ChatGPTによる24時間365日のサポート
        3. **包括的な記録管理** - 運動と栄養の履歴を一元管理
        4. **科学的な計算** - エビデンスに基づいた栄養計算
        
        始めるには、左のサイドバーでプロフィールを設定してください！
        """)
    
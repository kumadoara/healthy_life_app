"""トレーニングチャットページ"""

import streamlit as st
import os
from src.services.chat_service import HealthChatService
from datetime import datetime

st.set_page_config(page_title="トレーニング相談", page_icon="💪", layout="wide")

# プロフィールチェック
if 'user_profile' not in st.session_state or st.session_state.user_profile is None:
    st.warning("⚠️  プロフィールを設定してください")
    st.stop()

# チャットサービスの初期化
if 'training_chat' not in st.session_state:
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        st.error("🔑  OpenAI APIキーが設定されていません。.envファイルを確認してください。")
        st.stop()

    chat_service = HealthChatService(api_key)
    st.session_state.training_chain = chat_service.create_training_chain(st.session_state.user_profile)
    st.session_state.training_chat = chat_service
    st.session_state.training_messages = []

# ヘッダー
st.title("💪  トレーニング相談チャット")
st.markdown("あなたのレベルと目標に合わせたトレーニングプランを提案します")

# レイアウト
col1, col2 = st.columns([2, 1])

with col1:
    # チャット履歴の表示
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.training_messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
    
    # 入力フォーム
    user_input = st.chat_input("トレーニングに関する質問を入力してください...", key="training_chat_input")

    # クイック質問が選択された場合の処理
    if 'quick_question_selected' in st.session_state and st.session_state.quick_question_selected:
        user_input = st.session_state.quick_question_selected
        # 使用後にクリア
        del st.session_state.quick_question_selected

    if user_input:
        with st.chat_message("user"):
            st.markdown(user_input)

        # AIレスポンスを生成
        with st.chat_message("assistant"):
            message_placeholder = st.empty()

            try:
                # 通常のレスポンス取得
                response = st.session_state.training_chat.get_response(
                    st.session_state.training_chain, user_input
                )
                message_placeholder.markdown(response)

                # 成功した場合のみメッセージを追加
                st.session_state.training_messages.append({"role": "user", "content": user_input})
                st.session_state.training_messages.append({"role": "assistant", "content": response})

            except Exception as e:
                error_msg = str(e)
                if "insufficient_quota" in error_msg or "quota" in error_msg.lower():
                    message_placeholder.error("⚠️ APIクォータを超過しました。")
                    st.info("💡 https://platform.openai.com/account/billing")
                else:
                    message_placeholder.error(f"❌ エラーが発生しました: {error_msg}")
                # エラー時はメッセージを追加しない
    
with col2:
    st.subheader("🎯  クイックメニュー")

    # トレーニングカテゴリー
    training_category = st.selectbox(
        "トレーニング部位",
        ["全身", "上半身", "下半身", "体幹", "有酸素運動"]
    )

    # レベル別プロンプト
    st.markdown("###  💡  おすすめ質問")

    if training_category == "全身":
        prompts = [
            "初心者向けの全身トレーニングメニューを教えて",
            "自宅でできる全身運動は？",
            "週3回の全身トレーニングプラン"
        ]
    elif training_category == "上半身":
        prompts = [
            "腕立て伏せの正しいフォームは？",
            "肩を鍛えるトレーニング",
            "背中の筋肉を鍛える方法"
        ]
    elif training_category == "下半身":
        prompts = [
            "スクワットの正しいやり方",
            "太ももを引き締める運動",
            "ふくらはぎの筋トレ方法"
        ]
    elif training_category == "体幹":
        prompts = [
            "プランクの効果的なやり方",
            "腹筋を割るトレーニング",
            "体幹を鍛えるメリット"
        ]
    else:   # 有酸素運動
        prompts = [
            "効果的な有酸素運動の時間は？",
            "ランニングとウォーキングの違い",
            "HIITトレーニングについて教えて"
        ]
    
    # クイック質問ボタンの処理を修正
    for i, prompt in enumerate(prompts):
        if st.button(prompt, key=f"training_btn_{i}_{training_category}", use_container_width=True):
            # AI応答を生成
            try:
                response = st.session_state.training_chat.get_response(
                    st.session_state.training_chain, prompt
                )

                # 成功した場合のみメッセージを追加
                st.session_state.training_messages.append({"role": "user", "content": prompt})
                st.session_state.training_messages.append({"role": "assistant", "content": response})
                st.rerun()

            except Exception as e:
                error_msg = str(e)
                if "insufficient_quota" in error_msg or "quota" in error_msg.lower():
                    st.error("⚠️ APIクォータを超過しました。")
                    st.info("💡 https://platform.openai.com/account/billing")
                else:
                    st.error(f"❌ エラー: {error_msg}")
                # エラー時はメッセージを追加しない

    # トレーニング記録の追加
    st.markdown("---")
    st.markdown("###  📝 今日のトレーニング記録")

    with st.form("add_workout"):
        exercise = st.text_input("運動名")
        duration = st.number_input("時間（分）", min_value=1, max_value=300, value=30)
        intensity = st.select_slider(
            "強度",
            options=["低", "中", "高"],
            value="中"
        )
        calories = st.number_input("消費カロリー", min_value=0, max_value=2000, value=200)
        notes = st.text_area("メモ")

        if st.form_submit_button("記録を追加", use_container_width=True):
            # 入力バリデーション
            if not exercise or exercise.strip() == "":
                st.error("❌ 運動名を入力してください")
            elif duration <= 0:
                st.error("❌ 時間は1分以上で入力してください")
            elif calories < 0:
                st.error("❌ 消費カロリーは0以上で入力してください")
            else:
                try:
                    from src.models.user_profile import WorkoutRecord
                    record = WorkoutRecord(
                        date=datetime.now(),
                        exercise=exercise,
                        duration=duration,
                        calories=calories,
                        intensity=intensity,
                        notes=notes
                    )

                    # 保存処理
                    if st.session_state.data_manager.save_workout(record):
                        st.success("✅  トレーニング記録を追加しました！")
                        st.balloons()
                    else:
                        st.error("❌ 記録の保存に失敗しました")

                except Exception as e:
                    st.error(f"❌ エラーが発生しました: {str(e)}")
                    st.warning("記録は保存されませんでした")

# フッター
with st.sidebar:
    st.markdown("---")
    if st.button("🗑️  会話履歴をクリア", use_container_width=True):
        st.session_state.training_messages = []
        st.session_state.training_chat.clear_training_memory()
        st.rerun()
    
    st.info("""
    💪  **トレーニングのコツ**:
    - 正しいフォームを優先
    - 徐々に負荷を増やす
    - 十分な休息を取る 
    - 継続が最も重要
    """)

    # APIクォーターエラーが発生している場合の情報表示
    if 'api_quota_exceeded' in st.session_state:
        st.warning("""
        ⚠️ **AI機能制限中**
        OpenAI APIの使用制限に達しています。
        基本的なトレーニング記録機能は引き続き利用できます。
        """)

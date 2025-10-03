"""栄養相談ページ"""
import streamlit as st
import os
from src.services.chat_service import HealthChatService
from src.models.user_profile import UserProfile

st.set_page_config(page_title="栄養相談", page_icon="🍎", layout="wide")

# プロフィールチェック
if 'user_profile' not in st.session_state or st.session_state.user_profile is None:
    st.warning("⚠️  プロフィールを設定してください")
    st.stop()

# チャットサービスの初期化
if 'nutrition_chat' not in st.session_state:
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        st.error("🔑  OpenAI APIキーが設定されていません。.envファイルを確認してください。")
        st.stop()
    
    chat_service = HealthChatService(api_key)
    st.session_state.nutrition_chain = chat_service.create_nutrition_chain(st.session_state.user_profile)
    st.session_state.nutrition_chat = chat_service
    st.session_state.nutrition_messages = []

# ヘッダー
st.title("🍎  栄養相談チャット")
st.markdown("あなたの目標に合わせた栄養アドバイスを提供します")

# サイドバー - クイックプロンプト
with st.sidebar:
    st.subheader("💡  クイック質問")

    quick_prompts = [
        "今日の食事メニューを提案して",
        "ダイエットに効果的な食材は？",
        "腸活に良い食材は？",
        "プロテインの摂取タイミングは？",
        "間食でおすすめの食べ物は？",
        "水分補給のポイントを教えて",
        "糖質制限について教えて",
        "カロリー計算の方法は？",
        "筋肉をつける食事法は？"
    ]

    # クイック質問ボタンの処理
    for i, prompt in enumerate(quick_prompts):
        button_key = f"nutrition_quick_{i}"
        if st.button(prompt, use_container_width=True, key=button_key):
            # AI応答を生成
            try:
                response = st.session_state.nutrition_chat.get_response(
                    st.session_state.nutrition_chain, prompt
                )

                # 成功した場合のみメッセージを追加
                st.session_state.nutrition_messages.append({"role": "user", "content": prompt})
                st.session_state.nutrition_messages.append({"role": "assistant", "content": response})
                st.rerun()

            except Exception as e:
                error_msg = str(e)
                if "insufficient_quota" in error_msg or "quota" in error_msg.lower():
                    st.error("⚠️ APIクォータを超過しました。")
                    st.info("💡 https://platform.openai.com/account/billing")
                else:
                    st.error(f"❌ エラーが発生しました: {error_msg}")
                # エラー時はメッセージを追加しない

# チャット履歴の表示
chat_container = st.container()
with chat_container:
    for message in st.session_state.nutrition_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# 入力フォーム
if "nutrition_input" not in st.session_state:
    st.session_state.nutrition_input = ""

user_input = st.chat_input("栄養に関する質問を入力してください...", key="nutrition_chat_input")

if user_input:
    with st.chat_message("user"):
        st.markdown(user_input)

    # AIレスポンスを生成
    with st.chat_message("assistant"):
        message_placeholder = st.empty()

        try:
            # 通常のレスポンス取得
            response = st.session_state.nutrition_chat.get_response(
                st.session_state.nutrition_chain, user_input
            )
            message_placeholder.markdown(response)

            # 成功した場合のみメッセージを追加
            st.session_state.nutrition_messages.append({"role": "user", "content": user_input})
            st.session_state.nutrition_messages.append({"role": "assistant", "content": response})

        except Exception as e:
            error_msg = str(e)
            if "insufficient_quota" in error_msg or "quota" in error_msg.lower():
                message_placeholder.error("⚠️ APIクォータを超過しました。")
                st.info("💡 https://platform.openai.com/account/billing")
            else:
                message_placeholder.error(f"❌ エラーが発生しました: {error_msg}")
            # エラー時はメッセージを追加しない

# フッター
with st.sidebar:
    st.markdown("---")
    if st.button("🗑️  会話履歴をクリア", use_container_width=True):
        st.session_state.nutrition_messages = []
        st.session_state.nutrition_chat.clear_nutrition_memory()
        st.rerun()
    
    st.info("""
    💡  **ヒント**:
    - 具体的な質問をすると、より詳細なアドバイスが得られます
    - あなたのプロフィールに基づいてパーソナライズされています
    """)

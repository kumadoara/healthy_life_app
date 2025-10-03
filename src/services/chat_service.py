from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
from langchain.prompts import PromptTemplate
from typing import Optional
import streamlit as st


class HealthChatService:
    def __init__(self, api_key: str):
        """ChatGPTサービスの初期化"""
        print(f"HealthChatServiceを開始しています...")

        # APIキーのバリデーション
        if api_key is None:
            raise ValueError("APIキーが設定されていません")

        if not isinstance(api_key, str):
            raise ValueError("APIキーは文字列で入力してください")

        if api_key.strip() == "":
            raise ValueError("APIキーが空です")

        if len(api_key) < 10:  # OpenAI APIキーは通常長い
            raise ValueError("APIキーが短すぎます")

        # 無効な文字のチェック（スペースなど）
        if " " in api_key or "\t" in api_key or "\n" in api_key:
            raise ValueError("APIキーに無効な文字が含まれています")

        # 環境変数にAPIキーを設定
        import os
        os.environ["OPENAI_API_KEY"] = api_key

        try:
            # LLMの初期化
            self.llm = ChatOpenAI(
                model="gpt-4o",  # 最新の安定したモデルを使用
                temperature=0.7
            )
        except Exception as e:
            raise RuntimeError(f"LLMの初期化に失敗しました: {str(e)}")
        
        # 栄養相談用のメモリ
        self.nutrition_memory = ConversationBufferMemory(
            memory_key="history",
            return_messages=False
        )
        print("✓ 栄養メモリが初期化されました")
        
        # トレーニング相談用のメモリ
        self.training_memory = ConversationBufferMemory(
            memory_key="history",
            return_messages=False
        )
        print("✓ トレーニングメモリが初期化されました")
        
    def create_nutrition_chain(self, user_profile):
        """栄養相談用のチェーンを作成"""
        try:
            # user_profileのバリデーション
            if user_profile is None:
                raise ValueError("ユーザープロフィールが指定されていません")

            # 必要な属性の存在確認
            required_attrs = ['height', 'weight', 'age', 'gender', 'name', 'activity_level', 'goal']
            for attr in required_attrs:
                if not hasattr(user_profile, attr):
                    raise AttributeError(f"ユーザープロフィールに'{attr}'属性が存在しません")

            # 値のバリデーション
            self._validate_user_profile_values(user_profile)

            from src.utils.helpers import calculate_bmi, calculate_bmr

            # プロフィール情報を計算
            try:
                bmi = calculate_bmi(user_profile.height, user_profile.weight)
                bmr = calculate_bmr(user_profile.height, user_profile.weight,
                                  user_profile.age, user_profile.gender)
            except (TypeError, ValueError, ZeroDivisionError, OverflowError) as e:
                raise ValueError(f"ユーザープロフィールの値が不正です: {str(e)}")
            
            # テンプレートにプロフィール情報を埋め込み
            template = f"""あなたは優秀な栄養士です。以下のユーザープロフィールに基づいて、
パーソナライズされた栄養アドバイスを提供してください。

ユーザープロフィール:
- 名前: {user_profile.name if user_profile.name else 'ユーザー'}
- 年齢: {user_profile.age}歳
- 性別: {user_profile.gender}
- 身長: {user_profile.height:.1f}cm
- 体重: {user_profile.weight:.1f}kg
- 活動レベル: {user_profile.activity_level}
- 目標: {user_profile.goal}
- BMI: {bmi:.1f}
- 基礎代謝: {bmr:.0f}kcal

会話履歴:
{{history}}

ユーザー: {{input}}
栄養士:"""
            
            # プロンプトテンプレートを作成
            prompt = PromptTemplate(
                input_variables=["history", "input"],
                template=template
            )
            
            # チェーンを作成
            chain = ConversationChain(
                llm=self.llm,
                prompt=prompt,
                memory=self.nutrition_memory,
                verbose=False
            )
            
            print("✓ 栄養チェーンの作成に成功しました")
            return chain

        except ValueError as e:
            # バリデーションエラーはそのまま再スロー
            raise e
        except Exception as e:
            error_msg = f"チェーン作成中にエラーが発生しました: {str(e)}"
            print(error_msg)
            import streamlit as st
            st.error(error_msg)
            return None
    
    def create_training_chain(self, user_profile):
        """トレーニング相談用のチェーンを作成"""
        try:
            # user_profileのバリデーション
            if user_profile is None:
                raise ValueError("ユーザープロフィールが指定されていません")

            # 必要な属性の存在確認
            required_attrs = ['height', 'weight', 'age', 'gender', 'name', 'activity_level', 'goal']
            for attr in required_attrs:
                if not hasattr(user_profile, attr):
                    raise AttributeError(f"ユーザープロフィールに'{attr}'属性が存在しません")

            # 値のバリデーション
            self._validate_user_profile_values(user_profile)

            # メモリの存在を確認
            if not hasattr(self, 'training_memory'):
                print("Warning: training_memory not found, creating new one")
                self.training_memory = ConversationBufferMemory(
                    memory_key="history",
                    return_messages=False
                )
            
            # テンプレートにプロフィール情報を埋め込み
            template = f"""あなたは経験豊富なパーソナルトレーナーです。以下のユーザープロフィールに基づいて、
安全で効果的なトレーニングアドバイスを提供してください。

ユーザープロフィール:
- 名前: {user_profile.name if user_profile.name else 'ユーザー'}
- 年齢: {user_profile.age}歳
- 性別: {user_profile.gender}
- 身長: {user_profile.height:.1f}cm
- 体重: {user_profile.weight:.1f}kg
- 活動レベル: {user_profile.activity_level}
- 目標: {user_profile.goal}

会話履歴:
{{history}}

ユーザー: {{input}}
トレーナー:"""
            
            # プロンプトテンプレートを作成
            prompt = PromptTemplate(
                input_variables=["history", "input"],
                template=template
            )
            
            # チェーンを作成
            chain = ConversationChain(
                llm=self.llm,
                prompt=prompt,
                memory=self.training_memory,
                verbose=False
            )
            
            print("✓ トレーニングチェーンの作成に成功しました")
            return chain

        except ValueError as e:
            # バリデーションエラーはそのまま再スロー
            raise e
        except Exception as e:
            error_msg = f"チェーン作成中にエラーが発生しました: {str(e)}"
            print(error_msg)
            import streamlit as st
            st.error(error_msg)
            return None
    
    def get_response(self, chain, user_input: str) -> str:
        """チャットレスポンスを取得"""
        # 入力の検証
        if not user_input or user_input.strip() == "":
            return "入力が無効です。質問を入力してください。"

        try:
            print(f"レスポンスを取得しました: {user_input[:50]}...")

            # invokeメソッドを使用
            response = chain.invoke({"input": user_input})
            
            # レスポンスの処理
            if isinstance(response, dict):
                if "response" in response:
                    return response["response"]
                elif "text" in response:
                    return response["text"]
                elif "output" in response:
                    return response["output"]
                elif "content" in response:
                    return response["content"]
                else:
                    # 辞書のキーを確認
                    print(f"Response keys: {response.keys()}")
                    # 最初の文字列値を返す
                    for key, value in response.items():
                        if isinstance(value, str) and len(value) > 10:
                            return value
                    # 空の辞書または短い値しかない場合
                    return "回答が生成されませんでした"
            elif isinstance(response, str):
                return response
            elif response is None:
                # Noneの場合はエラーとして処理
                import streamlit as st
                error_msg = "レスポンスが不正です（None）"
                st.error(error_msg)
                return "予期しないレスポンス形式です（エラー）: NoneType"
            else:
                # その他の予期しないレスポンス形式の場合
                return f"予期しないレスポンス形式です: {type(response).__name__}"
                
        except Exception as e:
            print(f"レスポンスの取得中にエラーが発生しました: {e}")
            
            # predictメソッドを試す
            try:
                response = chain.predict(input=user_input)
                return response
            except Exception as e2:
                print(f"予測失敗: {e2}")
                
                # runメソッドを試す
                try:
                    response = chain.run(input=user_input)
                    return response
                except Exception as e3:
                    print(f"実行失敗: {e3}")
                    return "申し訳ございません。レスポンスの生成中にエラーが発生しました。もう一度お試しください。"
    
    def get_streaming_response(self, chain, user_input: str):
        """ストリーミングレスポンスを取得"""
        try:
            # ストリーミングが問題を起こす場合は通常のレスポンスを使用
            response = self.get_response(chain, user_input)
            # エラーレスポンスの場合は、ストリーミング固有のエラーメッセージに変換
            if response.startswith("申し訳ございません"):
                import streamlit as st
                st.error("ストリーミングレスポンスの取得に失敗しました")
                yield "エラー: ストリーミングレスポンスの取得に失敗しました"
            else:
                yield response
        except Exception as e:
            import streamlit as st
            st.error(f"ストリーミングエラー: {str(e)}")
            yield "エラー: ストリーミングレスポンスの取得に失敗しました"
    
    def clear_nutrition_memory(self):
        """栄養相談の会話履歴をクリア"""
        if hasattr(self, 'nutrition_memory') and self.nutrition_memory is not None:
            self.nutrition_memory.clear()
            print("✓ 栄養相談メモリをクリアしました。")
    
    def clear_training_memory(self):
        """トレーニング相談の会話履歴をクリア"""
        if hasattr(self, 'training_memory') and self.training_memory is not None:
            self.training_memory.clear()
            print("✓ トレーニング相談メモリをクリアしました。")
    
    def clear_memory(self):
        """すべての会話履歴をクリア（後方互換性のため）"""
        try:
            self.clear_nutrition_memory()
            self.clear_training_memory()
        except Exception as e:
            import streamlit as st
            st.error(f"メモリクリア中にエラーが発生しました: {str(e)}")

    def _validate_user_profile_values(self, user_profile):
        """ユーザープロフィールの値をバリデーション"""
        # 年齢の検証
        if user_profile.age <= 0:
            raise ValueError("年齢は正の整数で入力してください")

        # 身長の検証
        if user_profile.height < 100 or user_profile.height > 250:
            raise ValueError("身長は100cm以上250cm以下で入力してください")

        # 体重の検証
        if user_profile.weight <= 0:
            raise ValueError("体重は1kg以上で入力してください")

        # 性別の検証
        if not user_profile.gender or user_profile.gender.strip() == "":
            raise ValueError("性別を入力してください")

        # 目標の検証
        if not user_profile.goal or user_profile.goal.strip() == "":
            raise ValueError("目標を入力してください")

        # 活動レベルの検証
        if not user_profile.activity_level or user_profile.activity_level.strip() == "":
            raise ValueError("活動レベルを入力してください")
        
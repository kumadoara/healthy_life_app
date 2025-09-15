from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
from langchain.prompts import PromptTemplate
from typing import Optional
import streamlit as st


class HealthChatService:
    def __init__(self, api_key: str):
        """ChatGPTサービスの初期化"""
        print(f"Initializing HealthChatService...")
        
        # 環境変数にAPIキーを設定
        import os
        os.environ["OPENAI_API_KEY"] = api_key

        # LLMの初期化
        self.llm = ChatOpenAI(
            model="gpt-4-vision-preview",  # 安定したモデルを使用
            temperature=0.7
        )
        
        # 栄養相談用のメモリ
        self.nutrition_memory = ConversationBufferMemory(
            memory_key="history",
            return_messages=False
        )
        print("✓ nutrition_memory initialized")
        
        # トレーニング相談用のメモリ
        self.training_memory = ConversationBufferMemory(
            memory_key="history",
            return_messages=False
        )
        print("✓ training_memory initialized")
        
    def create_nutrition_chain(self, user_profile):
        """栄養相談用のチェーンを作成"""
        try:
            from src.utils.helpers import calculate_bmi, calculate_bmr
            
            # プロフィール情報を計算
            bmi = calculate_bmi(user_profile.height, user_profile.weight)
            bmr = calculate_bmr(user_profile.height, user_profile.weight, 
                              user_profile.age, user_profile.gender)
            
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
            
            print("✓ Nutrition chain created successfully")
            return chain
            
        except Exception as e:
            print(f"Error in create_nutrition_chain: {e}")
            raise
    
    def create_training_chain(self, user_profile):
        """トレーニング相談用のチェーンを作成"""
        try:
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
            
            print("✓ Training chain created successfully")
            return chain
            
        except Exception as e:
            print(f"Error in create_training_chain: {e}")
            raise
    
    def get_response(self, chain, user_input: str) -> str:
        """チャットレスポンスを取得"""
        try:
            print(f"Getting response for: {user_input[:50]}...")
            
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
                else:
                    # 辞書のキーを確認
                    print(f"Response keys: {response.keys()}")
                    # 最初の文字列値を返す
                    for key, value in response.items():
                        if isinstance(value, str) and len(value) > 10:
                            return value
                    return str(response)
            else:
                return str(response)
                
        except Exception as e:
            print(f"Error in get_response: {e}")
            
            # predictメソッドを試す
            try:
                response = chain.predict(input=user_input)
                return response
            except Exception as e2:
                print(f"Predict also failed: {e2}")
                
                # runメソッドを試す
                try:
                    response = chain.run(input=user_input)
                    return response
                except Exception as e3:
                    print(f"Run also failed: {e3}")
                    return "申し訳ございません。エラーが発生しました。もう一度お試しください。"
    
    def get_streaming_response(self, chain, user_input: str):
        """ストリーミングレスポンスを取得"""
        # ストリーミングが問題を起こす場合は通常のレスポンスを使用
        response = self.get_response(chain, user_input)
        yield response
    
    def clear_nutrition_memory(self):
        """栄養相談の会話履歴をクリア"""
        if hasattr(self, 'nutrition_memory'):
            self.nutrition_memory.clear()
            print("✓ Nutrition memory cleared")
    
    def clear_training_memory(self):
        """トレーニング相談の会話履歴をクリア"""
        if hasattr(self, 'training_memory'):
            self.training_memory.clear()
            print("✓ Training memory cleared")
    
    def clear_memory(self):
        """すべての会話履歴をクリア（後方互換性のため）"""
        self.clear_nutrition_memory()
        self.clear_training_memory()
        
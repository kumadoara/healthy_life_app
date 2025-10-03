"""記録管理ページ"""

import streamlit as st
import pandas as pd
import os
import plotly.express as px
import plotly.graph_objects as go
from src.models.user_profile import WorkoutRecord, NutritionRecord
from datetime import datetime, timedelta

st.set_page_config(page_title="記録管理", page_icon="📊", layout="wide")

# プロフィールチェック
if 'user_profile' not in st.session_state or st.session_state.user_profile is None:
    st.warning("⚠️  プロフィールを設定してください")
    st.stop()

st.title("📊  トレーニング・栄養記録")

# タブの作成
tab1, tab2, tab3 = st.tabs(["📈 ダッシュボード", "💪 トレーニング記録", "🍎 栄養記録"])

with tab1:
    st.subheader("週間サマリー")

    # データの読み込み
    workouts = st.session_state.data_manager.load_workouts()
    nutrition_records = st.session_state.data_manager.load_nutrition()

    if workouts and len(workouts) > 0:
        # 週間データの集計
        df_workouts = pd.DataFrame([w.model_dump() for w in workouts])
        df_workouts['date'] = pd.to_datetime(df_workouts['date'])

        # 過去7日間のデータ
        last_week = datetime.now() - timedelta(days=7)
        df_week = df_workouts[df_workouts['date'] >= last_week]

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            total_workouts = len(df_week)
            st.metric("トレーニング回数", f"{total_workouts}回", delta="週間")
        
        with col2:
            total_duration = df_week['duration'].sum() if not df_week.empty else 0  
            st.metric("総運動時間", f"{total_duration}分", delta=f"{total_duration//60}時間{total_duration%60}分")
        
        with col3:
            total_calories = df_week['calories'].sum() if not df_week.empty else 0  
            st.metric("消費カロリー", f"{total_calories:,.0f} kcal", delta="週間合計")
        
        with col4:
            avg_intensity = df_week['intensity'].mode()[0] if not df_week.empty else "なし"  
            st.metric("平均強度", avg_intensity, delta="最頻値")

        # グラフ表示
        st.markdown("---")

        graph_col1, graph_col2 = st.columns(2)

        with graph_col1:
            # 日別カロリー消費グラフ
            if not df_week.empty:
                try:
                    daily_calories = df_week.groupby(df_week['date'].dt.date)['calories'].sum().reset_index()
                    if not daily_calories.empty:
                        fig = px.bar(
                            daily_calories,
                            x='date',
                            y='calories',
                            title='日別消費カロリー',
                            labels={'calories': 'カロリー（kcal）', 'date': '日付'},
                            color_discrete_sequence=['#667eea']
                        )
                        fig.update_layout(height=400)
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("期間中のデータがありません")
                except Exception as e:
                    st.error(f"グラフ作成エラー: {str(e)}")
            else:
                st.info("まだデータがありません。")

        with graph_col2:
            # 運動種目別の分布
            if not df_week.empty and 'exercise' in df_week.columns:
                try:
                    exercise_dist = df_week['exercise'].value_counts().reset_index()
                    exercise_dist.columns = ['exercise', 'count']
                    if not exercise_dist.empty:
                        fig = px.pie(
                            exercise_dist, 
                            values='count', 
                            names='exercise',
                            title='運動種目の分布',
                            color_discrete_sequence=px.colors.sequential.Viridis
                        )
                        fig.update_layout(height=400)
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("データがありません")
                except Exception as e:
                    st.error(f"グラフ作成エラー: {str(e)}")
            else:
                st.info("まだデータがありません")

        # 週間トレンド
        st.markdown("### 📈  週間トレンド")

        try:
            # 週番号と年を追加
            df_workouts['week'] = df_workouts['date'].dt.isocalendar().week
            df_workouts['year'] = df_workouts['date'].dt.year

            # 年と週でグループ化
            weekly_stats = df_workouts.groupby(['year', 'week']).agg({
                'duration': 'sum',
                'calories': 'sum',
                'exercise': 'count'
            }).tail(4).reset_index()

            if not weekly_stats.empty:
                # 週の表示用ラベルを作成
                weekly_stats['week_label'] = 'w' + weekly_stats['week'].astype(str)

                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=weekly_stats['week_label'],
                    y=weekly_stats['duration'],
                    mode='lines+markers',
                    name='運動時間（分）',
                    yaxis='y'
                ))
                fig.add_trace(go.Scatter(
                    x=weekly_stats['week_label'],
                    y=weekly_stats['calories'],
                    mode='lines+markers',
                    name='消費カロリー',
                    yaxis='y2'
                ))

                fig.update_layout(
                    title='週間トレーニングトレンド',
                    xaxis_title='週',
                    yaxis=dict(title='運動時間（分）', side='left'),
                    yaxis2=dict(title='消費カロリー', overlaying='y', side='right'),
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("トレンドを表示するには、もう少しデータが必要です")
        except Exception as e:
            st.error(f"トレンド作成エラー: {str(e)}")
    
    else:
        # workoutが空の場合
        st.info("📝 トレーニング記録を始めましょう！")
        st.markdown("""
        トレーニングチャットページから記録を追加するか、
        「トレーニング記録」タブから手動で追加できます。
        """)

with tab2:
    st.subheader("💪 トレーニング履歴")
    
    # トレーニング記録の追加フォーム
    with st.expander("➕ 新しいトレーニング記録を追加", expanded=False):

        # メイン入力フォーム
        with st.form("add_workout_form"):
            form_col1, form_col2 = st.columns(2)
            
            with form_col1:
                exercise = st.text_input("運動名", placeholder="例: ランニング")
                duration = st.number_input("時間（分）", min_value=1, max_value=300, value=30)
                intensity = st.select_slider(
                    "強度",
                    options=["低", "中", "高"],
                    value="中"
                )
            
            with form_col2:
                calories = st.number_input("消費カロリー", min_value=0, max_value=2000, value=200)
                workout_date = st.date_input("日付", value=datetime.now())
                notes = st.text_area("メモ", placeholder="任意")

            # AI分析を有効にするチェックボックス
            enable_ai_feedback = st.checkbox(
                "🤖 AIフィードバックを有効にする",
                value=True,
                help="トレーニング内容をAIが分析してアドバイスを提供します"
            )
            
            submitted = st.form_submit_button("記録を追加", use_container_width=True)
            
            if submitted and exercise:
                record = WorkoutRecord(
                    date=datetime.combine(workout_date, datetime.now().time()),
                    exercise=exercise,
                    duration=duration,
                    calories=calories,
                    intensity=intensity,
                    notes=notes if notes else None
                )
                try:
                    if st.session_state.data_manager.save_workout(record):
                        st.success("✅ トレーニング記録を追加しました！")

                        # AI分析が有効な場合、結果をセッション状態に保存
                        if enable_ai_feedback:
                            st.session_state.pending_workout_analysis = {
                                'record': record.model_dump(),
                                'analyze': True
                            }

                        st.rerun()
                except Exception as e:
                            st.error(f"保存エラー: {str(e)}")
            elif submitted:
                st.error("運動名を入力してください")
        
    # AI分析結果の表示（フォーム外）
    if st.session_state.get('pending_workout_analysis', {}).get('analyze', False):
        with st.spinner("AIがトレーニングを分析中..."):
            try:
                api_key = os.getenv('OPENAI_API_KEY')
                if api_key:
                    from src.services.workout_feedback_service import WorkoutFeedbackService

                    feedback_service = WorkoutFeedbackService(api_key)

                    # 最近のワークアウト履歴を取得
                    recent_workouts = st.session_state.data_manager.load_workouts()
                    recent_data = []
                    if recent_workouts:
                        # 過去1週間のデータ
                        week_ago = datetime.now() - timedelta(days=7)
                        for w in recent_workouts[-10:]:  # 最新10件
                            if w.date >= week_ago:
                                recent_data.append(w.model_dump())

                    # ユーザープロフィール
                    profile_dict = st.session_state.user_profile.model_dump()

                    # 今回のワークアウト分析
                    workout_dict = st.session_state.pending_workout_analysis['record']
                    feedback = feedback_service.analyze_workout(
                        workout_dict, profile_dict, recent_data
                    )

                    if feedback:
                        st.markdown("### 🎯 AIトレーニングフィードバック")

                        # スコア表示
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            score = feedback.get('performance_score', 0)
                            st.metric("パフォーマンス", f"{score}/10")

                        with col2:
                            if feedback.get('intensity_assessment'):
                                st.info(f"**強度評価**: {feedback['intensity_assessment']}")
                        with col3:
                            if feedback.get('goal_alignment'):
                                st.success(f"**目標整合性**: {feedback['goal_alignment']}")
                        
                        # フィードバック詳細
                        feedback_col1, feedback_col2 = st.columns(2)

                        with feedback_col1:
                            if feedback.get('duration_feedback'):
                                st.markdown(f"**⏱️ 運動時間**: {feedback['duration_feedback']}")
                            
                            if feedback.get('calorie_assessment'):
                                st.markdown(f"**🔥 カロリー**: {feedback['calorie_assessment']}")
                            
                            if feedback.get('form_tips'):
                                st.markdown(f"**📋 フォームのコツ**:")
                                for tip in feedback['form_tips']:
                                    st.write(f"• {tip}")

                        with feedback_col2:
                            if feedback.get('progression_advice'):
                                st.markdown(f"**📈 次回への改善**: {feedback['progression_advice']}")
                            
                            if feedback.get('recovery_recommendation'):
                                st.markdown(f"**💤 回復アドバイス**: {feedback['recovery_recommendation']}")
                            
                            if feedback.get('next_workout_suggestions'):
                                st.markdown(f"**🎯 次回推奨メニュー**:")
                                for suggestion in feedback['next_workout_suggestions']:
                                    st.write(f"• {suggestion}")
                        
                        # 警告がある場合
                        if feedback.get('warning_flags'):
                            st.warning("⚠️ **注意点**:")
                            for warning in feedback['warning_flags']:
                                st.write(f"• {warning}")
                else:
                    st.info("OpenAI APIキーが設定されていないため、AI分析をスキップしました。")
            
            except Exception as e:
                st.error(f"AI分析エラー: {str(e)}")
            
            finally:
                # 安全にセッション状態をクリア
                if 'pending_workout_analysis' in st.session_state:
                    del st.session_state.pending_workout_analysis

    # 週間進捗分析ボタン（フォーム外）
    if st.button("📊 週間進捗分析", key="weekly_analysis"):
        with st.spinner("週間データを分析中..."):
            try:
                api_key = os.getenv('OPENAI_API_KEY')
                if api_key:
                    from src.services.workout_feedback_service import WorkoutFeedbackService
                    
                    feedback_service = WorkoutFeedbackService(api_key)
                    
                    # 過去1週間のワークアウト取得
                    all_workouts = st.session_state.data_manager.load_workouts()
                    week_ago = datetime.now() - timedelta(days=7)
                    weekly_workouts = []
                    
                    for workout in all_workouts:
                        if workout.date >= week_ago:
                            weekly_workouts.append(workout.model_dump())
                    
                    if weekly_workouts:
                        profile_dict = st.session_state.user_profile.model_dump()
                        analysis = feedback_service.analyze_weekly_progress(weekly_workouts, profile_dict)
                        
                        if analysis:
                            st.markdown("### 📈 週間進捗分析結果")
                            
                            # 週間スコア
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                weekly_score = analysis.get('weekly_score', 0)
                                st.metric("週間スコア", f"{weekly_score}/10")
                            
                            with col2:
                                variety_score = analysis.get('variety_score', 0)
                                st.metric("種目多様性", f"{variety_score}/5")
                            
                            with col3:
                                frequency = analysis.get('frequency_assessment', 'N/A')
                                st.info(f"**頻度評価**: {frequency}")
                            
                            # 詳細分析
                            analysis_col1, analysis_col2 = st.columns(2)
                            
                            with analysis_col1:
                                if analysis.get('strengths'):
                                    st.success("**✅ 良かった点**:")
                                    for strength in analysis['strengths']:
                                        st.write(f"• {strength}")
                                
                                if analysis.get('goal_progress'):
                                    st.info(f"**🎯 目標進捗**: {analysis['goal_progress']}")
                            
                            with analysis_col2:
                                if analysis.get('areas_for_improvement'):
                                    st.warning("**📈 改善点**:")
                                    for improvement in analysis['areas_for_improvement']:
                                        st.write(f"• {improvement}")
                                
                                if analysis.get('next_week_plan'):
                                    st.markdown(f"**📅 来週の推奨プラン**: {analysis['next_week_plan']}")
                            
                            # モチベーションメッセージ
                            if analysis.get('motivation_message'):
                                st.balloons()
                                st.success(f"💪 **{analysis['motivation_message']}**")
                    else:
                        st.info("過去1週間のトレーニングデータがありません。")
                else:
                    st.error("OpenAI APIキーが設定されていません。")
            except Exception as e:
                st.error(f"週間分析エラー: {str(e)}")
                
    # 既存の記録を表示
    workouts_tab2 = st.session_state.data_manager.load_workouts()
    
    if workouts_tab2 and len(workouts_tab2) > 0:

        # フィルター
        filter_col1, filter_col2, filter_col3 = st.columns(3)
        
        with filter_col1:
            date_filter = st.date_input(
                "期間",
                value=(datetime.now() - timedelta(days=30), datetime.now()),
                format="YYYY-MM-DD",
                key="workout_date_filter"
            )
        
        with filter_col2:
            exercise_list = list(set([w.exercise for w in workouts_tab2]))
            exercise_filter = st.multiselect("運動種目", exercise_list, key="exercise_filter")
        
        with filter_col3:
            intensity_filter = st.multiselect("強度", ["低", "中", "高"], key="intensity_filter")
        
        # データフレームの作成とフィルタリング
        df_tab2 = pd.DataFrame([w.model_dump() for w in workouts_tab2])
        df_tab2['date'] = pd.to_datetime(df_tab2['date'])
        
        # フィルター適用
        if len(date_filter) == 2:
            mask = (df_tab2['date'].dt.date >= date_filter[0]) & (df_tab2['date'].dt.date <= date_filter[1])
            df_tab2 = df_tab2[mask]
        
        if exercise_filter:
            df_tab2 = df_tab2[df_tab2['exercise'].isin(exercise_filter)]
        
        if intensity_filter:
            df_tab2 = df_tab2[df_tab2['intensity'].isin(intensity_filter)]
        
        # 表示
        if not df_tab2.empty:
            df_display = df_tab2.sort_values('date', ascending=False).copy()
            df_display['date'] = df_display['date'].dt.strftime('%Y-%m-%d %H:%M')
            
            # notesがNoneの場合を処理
            if 'notes' in df_display.columns:
                df_display['notes'] = df_display['notes'].fillna('')

            st.markdown("### 📋 トレーニング履歴")

            # 全てのレコードを表示            
            # 削除機能付きの表示
            for display_idx, row in df_display.iterrows():
                with st.expander(f"{row['date']} - {row['exercise']} ({row['duration']}分, {row['calories']} kcal)"):

                    # 詳細情報と削除ボタンを配置
                    info_col, delete_col = st.columns([4, 1])

                    with info_col:
                        st.write(f"**運動**: {row['exercise']}")
                        st.write(f"**時間**: {row['duration']}分")
                        st.write(f"**カロリー**: {row['calories']}kcal")
                        st.write(f"**強度**: {row['intensity']}")
                        if row['notes']:
                            st.write(f"**メモ**: {row['notes']}")

                    with delete_col:
                        # 削除ボタン
                        delete_key = f"delete_workout_{display_idx}"

                        if st.button("削除", key=delete_key, type="secondary"):
                            # 元のワークアウトデータから削除対象を特定
                            all_workouts = st.session_state.data_manager.load_workouts()
                  
                            # 削除対象のインデックス特定
                            target_index = None
                            for i, workout in enumerate(all_workouts):
                                workout_date_str = workout.date.strftime('%Y-%m-%d %H:%M')
                                if (workout_date_str == row['date'] and
                                    workout.exercise == row['exercise'] and
                                    workout.duration == row['duration'] and
                                    workout.calories == row['calories']):
                                    target_index = i
                                    break

                            # 削除実行
                            if target_index is not None:
                                if st.session_state.data_manager.delete_workout(target_index):
                                    st.success(f"「{row['exercise']}」の記録を削除しました")
                                    st.rerun()
                                else:
                                    st.error("削除に失敗しました")
                            else:
                                st.error("削除対象の記録が見つかりませんでした")                                        
            
            # エクスポート機能
            csv = df_display.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="📥 CSVダウンロード",
                data=csv,
                file_name=f"workout_history_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        

with tab3:
    st.subheader("🍎 栄養記録")
    
    # 栄養記録の追加フォーム
    with st.expander("➕ 新しい食事記録を追加", expanded=False):
        # 画像アップロード機能（フォーム外）
        st.markdown("### 📸 食事画像で栄養バランス分析")
        uploaded_image = st.file_uploader(
            "食事の写真をアップロード（任意）",
            type=['jpg', 'jpeg', 'png'],
            help="食事の写真をアップロードすると、AIが栄養バランスを分析します"
        )

        if uploaded_image is not None:
            st.image(uploaded_image, caption="アップロードされた食事画像", width=300)

            if st.button("🔍 画像を分析", key="analyze_meal_image"):
                with st.spinner("AIが画像を分析中..."):
                    try:
                        # 食品栄養素サービスの初期化
                        api_key = os.getenv('OPENAI_API_KEY')
                        if api_key:
                            from src.services.food_nutrition_service import FoodNutritionService
                            nutrition_service = FoodNutritionService(api_key)

                            # 画像を分析
                            image_data = uploaded_image.read()
                            analysis = nutrition_service.analyze_meal_image(image_data)

                            if analysis:
                                st.success("✅ 分析完了！")

                                # 分析結果を表示
                                col1, col2 = st.columns(2)

                                with col1:
                                    st.markdown("**🍽️ 検出された食品**")
                                    for food in analysis.get('detected_foods', []):
                                        st.write(f"• {food}")

                                    st.markdown("**⭐ 総合評価**")
                                    score = analysis.get('overall_score', 0)
                                    st.metric("栄養バランス", f"{score}/5")
                            
                                with col2:
                                    st.markdown("**📊 栄養素バランス**")
                                    nutrition_balance = analysis.get('nutrition_balance', {})

                                    for nutrient, score in nutrition_balance.items():
                                        nutrient_names = {
                                            'carbs': '炭水化物',
                                            'protein': 'タンパク質', 
                                            'fat': '脂質',
                                            'vitamins': 'ビタミン',
                                            'minerals': 'ミネラル'
                                        }
                                        name = nutrient_names.get(nutrient, nutrient)
                                        st.metric(name, f"{score}/5")

                                # アドバイス表示
                                if analysis.get('advice'):
                                    st.info(f"💡 **アドバイス**: {analysis['advice']}")

                                if analysis.get('missing_nutrients'):
                                    st.warning(f"⚠️ **不足栄養素**: {', '.join(analysis['missing_nutrients'])}")
                                
                                if analysis.get('recommendations'):
                                    st.success("🥗 **おすすめ追加食品**:")
                                    for rec in analysis['recommendations']:
                                        st.write(f"• {rec}")
                            else:
                                st.error("OpenAI APIキーが設定されていません")
                    except Exception as e:
                        st.error(f"画像分析エラー: {str(e)}")

        st.markdown("---") 

        # AI自動入力機能（フォーム外）
        st.markdown("### 🤖 食品栄養素の自動取得")

        col1, col2 = st.columns([3, 1])
        with col1:
            auto_food_name = st.text_input(
                "食品名を入力してAI分析",
                placeholder="例: 鶏胸肉 100g",
                key="auto_food_input"
            )
        
        with col2:
            if st.button("🤖 栄養素取得", key="get_nutrition_info", disabled=not auto_food_name):
                if auto_food_name:
                    with st.spinner("栄養情報を取得中..."):
                        try:
                            api_key = os.getenv('OPENAI_API_KEY')
                            if api_key:
                                from src.services.food_nutrition_service import FoodNutritionService
                                nutrition_service = FoodNutritionService(api_key)

                                nutrition_info = nutrition_service.get_nutrition_info(auto_food_name)

                                if nutrition_info and nutrition_info.get('confidence', 0) > 0.5:
                                    # セッション状態に保存
                                    st.session_state.auto_food_name = nutrition_info.get('food_name', auto_food_name)
                                    st.session_state.auto_calories = nutrition_info.get('calories', 0)
                                    st.session_state.auto_protein = nutrition_info.get('protein', 0)
                                    st.session_state.auto_carbs = nutrition_info.get('carbs', 0)
                                    st.session_state.auto_fat = nutrition_info.get('fat', 0)

                                    st.success(f"✅  「{nutrition_info['food_name']}」の栄養情報を取得しました！")
                                    st.json(nutrition_info)
                                else:
                                    st.warning("その食品の栄養情報が見つからないか、信頼度が低いです。")
                            else:
                                st.error("OpenAI APIキーが設定されていません")
                        except Exception as e:
                            st.error(f"栄養情報取得エラー: {str(e)}")
        
        st.markdown("---")

        # メイン入力フォーム
        with st.form("add_nutrition_form"):
            nutrition_col1, nutrition_col2 = st.columns(2)
            
            with nutrition_col1:
                meal_type = st.selectbox("食事タイプ", ["朝食", "昼食", "夕食", "間食"])
                meal_date = st.date_input("日付", value=datetime.now(), key="meal_date")
                meal_time = st.time_input("時間", value=datetime.now().time())
            
            with nutrition_col2:
                st.markdown("### 食品情報")

                # 自動取得された値があれば使用、なければ空

                food_name = st.text_input(
                    "食品名", 
                    placeholder="例: 鶏胸肉",
                    value=st.session_state.get('auto_food_name', '')
                    )
                                   
                calories = st.number_input(
                    "カロリー (kcal)", 
                    min_value=0, 
                    value=int(st.session_state.get('auto_calories', 0))
                )
                protein = st.number_input(
                    "タンパク質 (g)", 
                    min_value=0.0, 
                    value=float(st.session_state.get('auto_protein', 0.0))
                )
                carbs = st.number_input(
                    "炭水化物 (g)",
                    min_value=0.0, 
                    value=float(st.session_state.get('auto_carbs', 0.0))
                )
                fat = st.number_input(
                    "脂質 (g)", 
                    min_value=0.0, 
                    value=float(st.session_state.get('auto_fat', 0.0))
                )
            
            nutrition_notes = st.text_area("メモ（任意）", key="nutrition_notes")
            
            # フォーム送信ボタン
            nutrition_submitted = st.form_submit_button("記録を保存", use_container_width=True)
            
            if nutrition_submitted:
                # 入力バリデーション
                if not food_name or food_name.strip() == "":
                    st.error("❌ 食品名を入力してください")
                elif calories <= 0:
                    st.error("❌ カロリーは0より大きい値を入力してください")
                else:
                    try:
                        record = NutritionRecord(
                            date=datetime.combine(meal_date, meal_time),
                            meal_type=meal_type,
                            foods=[{
                                "name": str(food_name),
                                "calories": float(calories),
                                "protein": float(protein),
                                "carbs": float(carbs),
                                "fat": float(fat)
                            }],
                            total_calories=float(calories),
                            notes=nutrition_notes if nutrition_notes else None
                        )

                        # 保存処理
                        if st.session_state.data_manager.save_nutrition(record):
                            st.success("✅ 栄養記録を保存しました！")
                            # 自動入力値をクリア
                            for key in ['auto_food_name','auto_calories', 'auto_protein', 'auto_carbs', 'auto_fat']:
                                if key in st.session_state:
                                    del st.session_state[key]
                            st.rerun()
                        else:
                            st.error("❌ 記録の保存に失敗しました")
                            st.warning("記録は保存されませんでした")

                    except Exception as e:
                        st.error(f"❌ エラーが発生しました: {str(e)}")
                        st.warning("記録は保存されませんでした")
    
    # 栄養記録の表示
    nutrition_records_tab3 = st.session_state.data_manager.load_nutrition()
    
    if nutrition_records_tab3 and len(nutrition_records_tab3) > 0:
        df_nutrition = pd.DataFrame([n.model_dump() for n in nutrition_records_tab3])
        df_nutrition['date'] = pd.to_datetime(df_nutrition['date'])
        
        # 今日の栄養摂取
        today = datetime.now().date()
        today_records = df_nutrition[df_nutrition['date'].dt.date == today]
        
        if not today_records.empty:
            st.markdown("### 📅 今日の栄養摂取")
            
            today_col1, today_col2, today_col3, today_col4 = st.columns(4)
            
            total_calories_today = today_records['total_calories'].sum()
            
            # 目標カロリーの計算
            from src.utils.helpers import calculate_bmr, calculate_tdee
            
            try:
                bmr = calculate_bmr(
                    st.session_state.user_profile.height,
                    st.session_state.user_profile.weight,
                    st.session_state.user_profile.age,
                    st.session_state.user_profile.gender
                )
                tdee = calculate_tdee(bmr, st.session_state.user_profile.activity_level)
                
                if st.session_state.user_profile.goal == "減量":
                    target_calories = tdee - 500
                elif st.session_state.user_profile.goal == "増量":
                    target_calories = tdee + 500
                else:
                    target_calories = tdee
                
                with today_col1:
                    st.metric("摂取カロリー", f"{total_calories_today:.0f} kcal")
                with today_col2:
                    st.metric("目標カロリー", f"{target_calories:.0f} kcal")
                with today_col3:
                    remaining = target_calories - total_calories_today
                    st.metric("残りカロリー", f"{remaining:.0f} kcal", 
                             delta=f"{remaining/target_calories*100:.1f}%" if target_calories > 0 else "0%")
                with today_col4:
                    achievement = (total_calories_today / target_calories) * 100 if target_calories > 0 else 0
                    st.metric("達成率", f"{achievement:.1f}%")
            except Exception as e:
                st.error(f"カロリー計算エラー: {str(e)}")
            
        if not df_nutrition.empty:
            df_display = df_nutrition.sort_values('date', ascending=False).copy()
            df_display['date_str'] = df_display['date'].dt.strftime('%Y-%m-%d %H:%M')
            
            # 履歴表示
            st.markdown("### 📋 食事履歴")
        
            # 削除機能付きの表示（最新10件）
            for display_idx, row in df_display.head(10).iterrows():
                with st.expander(f"{row['date_str']} - {row['meal_type']} ({row['total_calories']:.0f} kcal)"):
                    
                    info_col, delete_col = st.columns([4, 1])
                    
                    with info_col:
                        # 食品情報の表示
                        if isinstance(row['foods'], list):
                            for food in row['foods']:
                                if isinstance(food, dict):
                                    st.write(f"**{food.get('name', '不明')}**")
                                    food_info_col1, food_info_col2, food_info_col3, food_info_col4 = st.columns(4)
                                    with food_info_col1:
                                        st.write(f"カロリー: {food.get('calories', 0):.0f} kcal")
                                    with food_info_col2:
                                        st.write(f"タンパク質: {food.get('protein', 0):.1f}g")
                                    with food_info_col3:
                                        st.write(f"炭水化物: {food.get('carbs', 0):.1f}g")
                                    with food_info_col4:
                                        st.write(f"脂質: {food.get('fat', 0):.1f}g")
                        if row.get('notes'):
                            st.write(f"📝 メモ: {row['notes']}")

                    with delete_col:
                        # 削除ボタン
                        delete_key= f"delete_nutrition_{display_idx}"

                        if st.button("削除", key=delete_key, type="secondary"):
                            # 元の栄養データから削除対象を特定
                            all_nutrition = st.session_state.data_manager.load_nutrition()

                            # 削除対象のインデックスを見つける
                            target_index = None
                            for i, nutrition in enumerate(all_nutrition):
                                nutrition_date_str = nutrition.date.strftime('%Y-%m-%d %H:%M')
                                if (nutrition_date_str == row['date_str'] and 
                                    nutrition.meal_type == row['meal_type'] and
                                    abs(nutrition.total_calories - row['total_calories']) < 1.0):
                                    target_index = i
                                    break
                    
                            # 削除実行
                            if target_index is not None:
                                if st.session_state.data_manager.delete_nutrition(target_index):
                                    st.success(f"「{row['meal_type']}」の記録を削除しました")
                                    st.rerun()
                                else:
                                    st.error("削除に失敗しました")
                            else:
                                st.error("削除対象の記録が見つかりませんでした")  
        else:
            st.info("栄養記録がありません")
    else:
        st.info("まだ栄養記録がありません。上のフォームから記録を追加してください。")

"""
データ永続化 
栄養、トレーニング記録の管理
"""

import json
from pathlib import Path
from datetime import datetime
from typing import List, Optional
from src.models.user_profile import UserProfile, WorkoutRecord, NutritionRecord

class DataManager:
    def __init__(self, data_dir: str= "data/users"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.current_user_file = self.data_dir / "current_user.json"

        # JSONファイルの初期化・修復
        self._ensure_json_files()
    
    def _ensure_json_files(self):
        """JSONファイルが正しい形式で存在することを確認"""
        files_to_check = [
            (self.data_dir / "workouts.json", []),
            (self.data_dir / "nutrition.json", []),
        ]
        
        for file_path, default_content in files_to_check:
            if not file_path.exists():
                # ファイルが存在しない場合は作成
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(default_content, f, ensure_ascii=False)
                print(f"Created: {file_path}")
            else:
                # ファイルが存在する場合は検証
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        json.load(f)
                except (json.JSONDecodeError, ValueError) as e:
                    print(f"Repairing corrupted file: {file_path}")
                    print(f"Error: {e}")
                    
                    # バックアップを作成
                    backup_path = file_path.with_suffix('.backup')
                    try:
                        file_path.rename(backup_path)
                        print(f"Backup created: {backup_path}")
                    except:
                        pass
                    
                    # 新しいファイルを作成
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(default_content, f, ensure_ascii=False)
                    print(f"File repaired: {file_path}")
    
    def save_profile(self, profile: UserProfile) -> bool:
        """プロフィールを保存"""
        try:
            profile_data = profile.model_dump()
            profile_data['updated_at'] = datetime.now().isoformat()

            with open(self.current_user_file, 'w', encoding='utf-8') as f:
                json.dump(profile_data, f, ensure_ascii=False, indent=2, default=str)
            return True
        except Exception as e:
            print(f"Error saving profile: {e}")
            return False
        
    def load_profile(self) -> Optional[UserProfile]:
        """プロフィールを読み込み"""
        try:
            if self.current_user_file.exists():
                with open(self.current_user_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                return UserProfile(**data)
        except Exception as e:
            print(f"Error loading profile: {e}")
        return None

    def save_workout(self, record: WorkoutRecord) -> bool:
        """トレーニング記録を保存"""
        workout_file = self.data_dir / "workouts.json"
        try:
            # 既存のデータを読み込み
            workouts = self._load_json_safely(workout_file, [])
            
            # 新しい記録を追加
            record_data = record.model_dump()
            
            # datetimeをISO形式に変換
            if isinstance(record_data.get('date'), datetime):
                record_data['date'] = record_data['date'].isoformat()
            
            workouts.append(record_data)
            
            # ファイルに保存
            with open(workout_file, 'w', encoding='utf-8') as f:
                json.dump(workouts, f, ensure_ascii=False, indent=2, default=str)
            return True
        except Exception as e:
            print(f"Error saving workout: {e}")
            return False
    
    def load_workouts(self) -> List[WorkoutRecord]:
        """トレーニング記録を読み込み"""
        workout_file = self.data_dir / "workouts.json"
        try:
            workouts_data = self._load_json_safely(workout_file, [])
            return [WorkoutRecord(**record) for record in workouts_data]
        except Exception as e:
            print(f"Error loading workouts: {e}")
            return []
        
    def delete_workout(self, index: int) -> bool:
        """トレーニング記録を削除"""
        workout_file = self.data_dir / "workouts.json"
        try:
            workouts = self._load_json_safely(workout_file, [])

            if 0 <= index < len(workouts):
                # 指定されたインデックスの記録を削除
                deleted_record = workouts.pop(index)

                # ファイルに保存
                with open(workout_file, 'w', encoding='utf-8') as f:
                    json.dump(workouts, f, ensure_ascii=False, indent=2, default=str)
                
                print(f"Deleted workout: {deleted_record.get('exercise', 'Unknown')} at index {index}")
                return True
            else:
                print(f"Invalid index: {index}")
                return False
        except Exception as e:
            print(f"Error deleting workout: {e}")
            return False

    def save_nutrition(self, record: NutritionRecord) -> bool:
        """栄養記録を保存"""
        nutrition_file = self.data_dir / "nutrition.json"
        try:
            # 既存のデータを読み込み
            records = self._load_json_safely(nutrition_file, [])
            
            # 新しい記録を追加
            record_data = record.model_dump()
            
            # datetimeをISO形式に変換
            if isinstance(record_data.get('date'), datetime):
                record_data['date'] = record_data['date'].isoformat()
            
            records.append(record_data)
            
            # ファイルに保存
            with open(nutrition_file, 'w', encoding='utf-8') as f:
                json.dump(records, f, ensure_ascii=False, indent=2, default=str)
            return True
        except Exception as e:
            print(f"Error saving nutrition: {e}")
            return False
            
    def load_nutrition(self) -> List[NutritionRecord]:
        """栄養記録を読み込み"""
        nutrition_file = self.data_dir / "nutrition.json"
        try:
            nutrition_data = self._load_json_safely(nutrition_file, [])
            return [NutritionRecord(**record) for record in nutrition_data]
        except Exception as e:
            print(f"Error loading nutrition: {e}")
            return []
        
    def delete_nutrition(self, index: int) -> bool:
        """栄養記録を削除"""
        nutrition_file = self.data_dir / "nutrition.json"
        try:
            records = self._load_json_safely(nutrition_file, [])

            if 0 <= index < len(records):
                # 指定されたインデックスの記録を削除
                deleted_record = records.pop(index)

                # ファイルに保存
                with open(nutrition_file, 'w', encoding='utf-8') as f:
                    json.dump(records, f, ensure_ascii=False, indent=2, default=str)
                
                print(f"Deleted nutrition record: {deleted_record.get('meal_type', 'Unknown')} at index {index}")
                return True
            else:
                print(f"Invalid index: {index}")
                return False
        except Exception as e:
            print(f"Error deleting nutrition: {e}")
            return False 
    
    def _load_json_safely(self, file_path: Path, default_value):
        """JSONファイルを安全に読み込み"""
        if not file_path.exists():
            return default_value
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # 空ファイルの場合
                if not content.strip():
                    return default_value
                
                # JSONをパース
                return json.loads(content)
                
        except json.JSONDecodeError as e:
            print(f"JSON decode error in {file_path}: {e}")
            print(f"Resetting file to default value")
            
            # 破損したファイルをバックアップ
            backup_path = file_path.with_suffix('.corrupt')
            try:
                file_path.rename(backup_path)
                print(f"Corrupted file backed up to: {backup_path}")
            except:
                pass
            
            # デフォルト値で初期化
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(default_value, f, ensure_ascii=False, indent=2)
            
            return default_value
        except Exception as e:
            print(f"Unexpected error loading {file_path}: {e}")
            return default_value
    
    def clear_all_data(self):
        """すべてのデータをクリア（デバッグ用）"""
        files = [
            self.data_dir / "workouts.json",
            self.data_dir / "nutrition.json"
        ]
        
        for file_path in files:
            if file_path.exists():
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump([], f)
                print(f"Cleared: {file_path}")
                
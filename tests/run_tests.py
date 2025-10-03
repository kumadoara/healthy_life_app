"""
ヘルシーライフアプリのテストランナー
"""

import sys
import subprocess
from pathlib import Path
import argparse
import shutil

# -------------------------
# ユーティリティ関数
# -------------------------
def run_command(cmd: list[str], description: str = "") -> bool:
    """サブプロセス実行の共通関数"""
    if description:
        print(f"▶ {description}")
    try:
        subprocess.run(cmd, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} で失敗しました: {e}")
        return False
    except FileNotFoundError as e:
        print(f"⚠️ コマンドが見つかりません: {e}")
        return False

# -------------------------
# 個別処理関数
# -------------------------
def install_test_dependencies(requirements_file: str = "test_requirements.txt") -> bool:
    """テスト用依存関係のインストール"""
    if not Path(requirements_file).exists():
        print(f"⚠️ {requirements_file} が見つかりません。スキップします")
        return True
    return run_command(
        [sys.executable, "-m", "pip", "install", "-r", requirements_file],
        "テスト依存関係のインストール"
    )

def run_tests(test_type: str = "all", coverage: bool = True, verbose: bool = True) -> bool:
    """pytest によるテスト実行"""
    cmd = [sys.executable, "-m", "pytest"]
    # テストタイプごとのマーカー
    markers = {
        "unit": "unit",
        "integration": "integration",
        "api": "api",
        "fast": "not slow",
    }
    if test_type in markers:
        cmd.extend(["-m", markers[test_type]])
    if coverage:
        cmd.extend(["--cov=src", "--cov-report=html", "--cov-report=term"])
    if verbose:
        cmd.append("-v")
    cmd.append("tests/")
    return run_command(cmd, f"{test_type} テスト実行")

def run_specific_test_file(test_file: str) -> bool:
    """特定のテストファイルを実行"""
    path = Path(test_file)
    if not path.exists():
        path = Path("tests") / test_file
    return run_command([sys.executable, "-m", "pytest", "-v", str(path)], f"{path} の実行")

def run_linting() -> bool:
    """flake8 による静的解析"""
    return run_command(
        [sys.executable, "-m", "flake8", "src/"],
        "コードの静的解析 (flake8)"
    )

def generate_test_report() -> bool:
    """pytest-html によるテストレポート生成"""
    return run_command(
        [sys.executable, "-m", "pytest", "--html=test_report.html", "--self-contained-html", "tests/"],
        "テストレポート生成"
    )

def setup_test_environment():
    """テスト環境のセットアップ"""
    print("🔧 テスト環境のセットアップ中...")
    for d in ["tests", "tests/data", "htmlcov"]:
        Path(d).mkdir(parents=True, exist_ok=True)

    init_file = Path("tests/__init__.py")
    if not init_file.exists():
        init_file.write_text('"""テストパッケージ"""')

    print("✅ セットアップ完了")

def clean_test_artifacts():
    """テストアーティファクトのクリーンアップ"""
    print("🧹 テストアーティファクトのクリーンアップ中...")
    artifacts = [".pytest_cache", "htmlcov", ".coverage", "test_report.html"]
    for artifact in artifacts:
        path = Path(artifact)
        if path.exists():
            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink()

    # 再帰的に __pycache__ 削除
    for pycache in Path(".").rglob("__pycache__"):
        shutil.rmtree(pycache)
    print("✅ クリーンアップ完了")

# -------------------------
# メイン処理
# -------------------------
def main() -> int:
    parser = argparse.ArgumentParser(description="ヘルシーライフアプリのテストランナー")
    parser.add_argument("--type", choices=["all", "unit", "integration", "api", "fast"], default="all")
    parser.add_argument("--file", help="特定のテストファイルを実行")
    parser.add_argument("--no-coverage", action="store_true", help="カバレッジレポートを無効化")
    parser.add_argument("--install-deps", action="store_true", help="依存関係をインストール")
    parser.add_argument("--setup", action="store_true", help="テスト環境をセットアップ")
    parser.add_argument("--lint", action="store_true", help="Lintingを実行")
    parser.add_argument("--report", action="store_true", help="HTMLテストレポートを生成")
    parser.add_argument("--clean", action="store_true", help="テストアーティファクトをクリーンアップ")
    parser.add_argument("--quiet", action="store_true", help="詳細出力を無効化")

    args = parser.parse_args()

    print("=" * 50)
    print("🏃 ヘルシーライフアプリ テストランナー")
    print("=" * 50)

    if args.clean:
        clean_test_artifacts()
        return 0
    if args.setup:
        setup_test_environment()
    if args.install_deps and not install_test_dependencies():
        return 1
    success = True
    if args.lint and not run_linting():
        success = False
    if args.file:
        if not run_specific_test_file(args.file):
            success = False
    else:
        if not run_tests(test_type=args.type, coverage=not args.no_coverage, verbose=not args.quiet):
            success = False
    if args.report:
        generate_test_report()
    print("\n" + "=" * 50)
    if success:
        print("🎉 すべての処理が正常に完了しました！")
        print("=" * 50)
        return 0
    else:
        print("❌ 一部の処理が失敗しました")
        print("=" * 50)
        return 1

if __name__ == "__main__":
    sys.exit(main())

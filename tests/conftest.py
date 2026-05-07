"""
pytest 설정 및 공통 fixtures
"""
import pytest
import sys
import os
from pathlib import Path
import tempfile
import shutil

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Windows Mock 패치 적용
from tests.mock_windows import patch_windows_modules
patch_windows_modules()


@pytest.fixture
def temp_dir():
    """임시 디렉토리 생성"""
    tmp = tempfile.mkdtemp()
    yield tmp
    shutil.rmtree(tmp, ignore_errors=True)


@pytest.fixture
def sample_files(temp_dir):
    """테스트용 샘플 파일 생성"""
    files = []

    # 한셀 파일 Mock (실제로는 빈 파일)
    extensions = ['.cell', '.nxl', '.xls', '.xlsx']

    for i, ext in enumerate(extensions):
        file_path = Path(temp_dir) / f"test_{i}{ext}"
        file_path.write_text(f"Mock content for test_{i}{ext}")
        files.append(str(file_path))

    return files


@pytest.fixture
def sample_folder(temp_dir):
    """테스트용 샘플 폴더 구조 생성"""
    base = Path(temp_dir) / "sample_folder"
    base.mkdir()

    # 루트 레벨 파일
    (base / "file1.cell").write_text("content1")
    (base / "file2.xlsx").write_text("content2")

    # 하위 폴더
    sub = base / "subfolder"
    sub.mkdir()
    (sub / "file3.cell").write_text("content3")
    (sub / "file4.xls").write_text("content4")

    return str(base)


@pytest.fixture
def output_dir(temp_dir):
    """테스트용 출력 디렉토리"""
    output = Path(temp_dir) / "output"
    output.mkdir()
    return str(output)


@pytest.fixture
def log_dir(temp_dir):
    """테스트용 로그 디렉토리"""
    logs = Path(temp_dir) / "logs"
    logs.mkdir()
    return str(logs)

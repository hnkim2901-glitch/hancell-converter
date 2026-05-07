# 테스트 가이드

Mac에서 Windows 전용 애플리케이션의 로직을 테스트하기 위한 가이드입니다.

## 테스트 구조

```
tests/
├── __init__.py              # 테스트 모듈 초기화
├── conftest.py              # pytest fixtures 정의
├── mock_windows.py          # Windows API Mock
├── test_file_queue.py       # FileQueue 단위 테스트
├── test_logger.py           # ConversionLogger 단위 테스트
├── test_process_manager.py  # ProcessManager Mock 테스트
├── test_worker.py           # HancellWorker Mock 테스트
└── test_integration.py      # 통합 테스트
```

## Mac에서 테스트 실행

### 방법 1: 스크립트 사용 (권장)

```bash
./run_tests.sh
```

이 스크립트는 자동으로:
- Python 버전 확인
- 가상 환경 생성/활성화
- 테스트 의존성 설치
- pytest 실행
- 커버리지 리포트 생성 (선택)

### 방법 2: 수동 실행

```bash
# 1. 가상 환경 생성
python3 -m venv venv

# 2. 가상 환경 활성화
source venv/bin/activate

# 3. 테스트 의존성 설치
pip install -r requirements-test.txt

# 4. 테스트 실행
pytest tests/ -v
```

## 테스트 커버리지

커버리지 리포트 생성:

```bash
pytest tests/ --cov=converter --cov=utils --cov-report=html --cov-report=term
```

결과 확인:

```bash
open htmlcov/index.html  # macOS
```

## Mock 시스템

### Windows API Mock

`tests/mock_windows.py`에서 Windows 전용 모듈을 Mock으로 대체:

- **psutil**: 프로세스 관리
- **pywinauto**: UI 자동화
- **win32com**: COM 인터페이스
- **PIL.ImageGrab**: 스크린샷
- **subprocess.Popen**: 프로세스 실행

### Mock 동작 방식

1. **자동 패치**: `conftest.py`에서 테스트 시작 시 자동으로 Mock 패치
2. **투명한 대체**: 실제 코드는 수정하지 않고 import만 Mock으로 대체
3. **로직 테스트**: Windows API 호출은 Mock이지만 비즈니스 로직은 실제로 실행

## 테스트 범위

### ✅ 테스트 가능 (Mock 없이)

- **FileQueue**: 파일 큐 관리 로직
  - 파일 추가/제거
  - 상태 관리
  - 통계 계산
  - 실패 재시도

- **ConversionLogger**: CSV 로깅
  - 로그 기록
  - 실패 파일 추출
  - 통계 요약

### ⚠️ 테스트 가능 (Mock 사용)

- **ProcessManager**: 프로세스 관리
  - 한셀 경로 찾기 로직
  - 프로세스 상태 확인 로직
  - 재시작 로직

- **HancellWorker**: 변환 워커
  - 작업 처리 흐름
  - 재시작 간격 로직
  - 콜백 호출

### ❌ 테스트 불가능

- **실제 한셀 자동화**: pywinauto 키 입력
- **실제 파일 변환**: 한셀 프로그램 필요
- **UI 테스트**: PySide6 윈도우 (별도 환경 필요)

## 테스트 예시

### 단위 테스트

```python
def test_add_files(sample_files, output_dir):
    """파일 추가 테스트"""
    queue = FileQueue()
    queue.add_files(sample_files, ['PDF'], output_dir)

    assert len(queue.tasks) == 4
    for task in queue.tasks:
        assert task.status == ConversionStatus.PENDING
```

### Mock 테스트

```python
@patch('converter.hancell_worker.HancellWorker._convert_with_pywinauto')
def test_convert_task(mock_convert, worker, sample_task):
    """Mock을 사용한 변환 테스트"""
    mock_convert.return_value = True

    result = worker.convert_task(sample_task)

    assert result is True
    assert worker.conversion_count == 1
```

### 통합 테스트

```python
def test_complete_workflow(sample_files, output_dir, log_dir):
    """완전한 워크플로우 테스트"""
    queue = FileQueue()
    logger = ConversionLogger(log_dir)

    queue.add_files(sample_files, ['PDF'], output_dir)

    for task in queue.tasks:
        logger.log_conversion(
            task.source_file, 'PDF',
            task.get_output_path('PDF'), 'SUCCESS'
        )

    summary = logger.get_log_summary()
    assert summary['SUCCESS'] == len(sample_files)
```

## pytest Fixtures

### 제공되는 Fixtures

- `temp_dir`: 임시 디렉토리
- `sample_files`: 테스트용 샘플 파일 (4개)
- `sample_folder`: 테스트용 폴더 구조 (하위 폴더 포함)
- `output_dir`: 출력 디렉토리
- `log_dir`: 로그 디렉토리

### 사용 예시

```python
def test_example(sample_files, output_dir):
    # sample_files와 output_dir이 자동으로 생성됨
    queue = FileQueue()
    queue.add_files(sample_files, ['PDF'], output_dir)
    # 테스트 종료 후 자동으로 정리됨
```

## 테스트 실행 옵션

### 특정 파일만 테스트

```bash
pytest tests/test_file_queue.py -v
```

### 특정 테스트 함수만 실행

```bash
pytest tests/test_file_queue.py::TestFileQueue::test_add_files -v
```

### 키워드로 필터링

```bash
pytest tests/ -k "queue" -v  # 'queue'가 포함된 테스트만
```

### 실패 시 즉시 중단

```bash
pytest tests/ -x
```

### 실패한 테스트만 재실행

```bash
pytest tests/ --lf  # last failed
```

### 상세 출력

```bash
pytest tests/ -vv --tb=long
```

## CI/CD 통합

### GitHub Actions 예시

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: macos-latest

    steps:
    - uses: actions/checkout@v2

    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.11'

    - name: Install dependencies
      run: |
        pip install -r requirements-test.txt

    - name: Run tests
      run: |
        pytest tests/ --cov=converter --cov=utils
```

## 주의사항

### Mac에서의 제약사항

1. **Windows API 미지원**: Mock으로 대체되므로 실제 동작과 다를 수 있음
2. **UI 테스트 불가**: PySide6 윈도우는 실제 Windows에서만 테스트 가능
3. **한셀 프로그램 없음**: 실제 변환은 테스트 불가

### Windows에서 실제 테스트

Mac에서 로직을 검증한 후, Windows 환경에서 다음을 테스트해야 합니다:

1. 한셀 자동화 (pywinauto 키 입력)
2. 실제 파일 변환
3. UI 동작
4. 프로세스 관리

### 테스트 데이터

- 샘플 파일은 빈 텍스트 파일로 생성됨
- 실제 한셀 파일 형식이 아니므로 변환은 불가능
- 로직 검증 목적으로만 사용

## 트러블슈팅

### import 에러

```bash
# 프로젝트 루트를 PYTHONPATH에 추가
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
pytest tests/
```

### Mock 패치 실패

`conftest.py`에서 자동 패치되므로 수동으로 패치할 필요 없음.
만약 문제가 생기면:

```python
from tests.mock_windows import patch_windows_modules
patch_windows_modules()
```

### 임시 파일 정리 안됨

pytest는 자동으로 임시 파일을 정리하지만, 수동으로 정리하려면:

```bash
rm -rf /tmp/pytest-*
```

## 다음 단계

1. **Mac에서 로직 검증**: 이 테스트로 비즈니스 로직 검증
2. **Windows에서 통합 테스트**: 실제 환경에서 E2E 테스트
3. **CI/CD 설정**: 자동화된 테스트 파이프라인 구축

## 참고

- pytest 문서: https://docs.pytest.org/
- pytest-cov: https://pytest-cov.readthedocs.io/
- unittest.mock: https://docs.python.org/3/library/unittest.mock.html

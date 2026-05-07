# 한셀 파일 일괄 변환기

Windows 로컬 데스크톱 애플리케이션으로, 한셀 파일(.cell, .nxl, .xls, .xlsx)을 드래그앤드롭하면 로컬에 설치된 한컴오피스 한셀을 자동으로 실행하여 PDF, HTML, XLS, XLSX로 일괄 변환합니다.

## 주요 기능

- **드래그앤드롭 지원**: 파일 또는 폴더를 드래그앤드롭으로 간편하게 추가
- **다중 형식 변환**: PDF, HTML, XLS, XLSX 중 원하는 형식 선택
- **대량 파일 처리**: 수백 개의 파일도 안정적으로 처리
- **진행 상태 표시**: 파일별 변환 상태를 실시간으로 테이블에 표시
- **실패 복구**: 실패한 파일만 선택하여 재시도 가능
- **CSV 로그**: 모든 변환 결과를 CSV 파일로 저장
- **프로세스 관리**: 설정된 개수마다 한셀 프로세스를 재시작하여 안정성 향상
- **스크린샷 자동 저장**: 오류 발생 시 화면을 자동으로 캡처하여 디버깅 지원

## 시스템 요구사항

- **OS**: Windows 10/11
- **소프트웨어**: 한컴오피스 한셀 (2018, 2020, 2022, NEO 등)
- **Python**: 3.8 이상 (exe 파일 사용 시 불필요)

## 설치 및 실행

### 방법 1: Python 환경에서 실행

1. 저장소 클론 또는 다운로드
```bash
git clone <repository-url>
cd hancell-converter
```

2. 의존성 설치
```bash
pip install -r requirements.txt
```

3. 애플리케이션 실행
```bash
python app.py
```

### 방법 2: 실행 파일(.exe)로 패키징

1. PyInstaller로 exe 파일 생성
```bash
pyinstaller --onefile --windowed --name "한셀변환기" app.py
```

2. `dist/한셀변환기.exe` 실행

## 사용 방법

1. **파일 추가**
   - 변환할 한셀 파일 또는 폴더를 드래그앤드롭 영역에 드롭
   - 폴더 드롭 시 "하위 폴더 포함" 옵션으로 재귀 탐색 가능

2. **변환 설정**
   - 변환할 형식 선택 (PDF, HTML, XLS, XLSX)
   - 출력 폴더 지정
   - 옵션 설정:
     - **하위 폴더 포함**: 폴더 내 모든 하위 폴더의 파일도 처리
     - **기존 파일 스킵**: 이미 변환된 파일은 건너뛰기
     - **프로세스 재시작 간격**: N개 파일마다 한셀 재시작 (0이면 사용 안함)

3. **변환 시작**
   - "변환 시작" 버튼 클릭
   - 테이블에서 실시간으로 진행 상황 확인

4. **결과 확인**
   - 변환 완료 후 출력 폴더에서 결과 파일 확인
   - `logs/` 폴더에서 CSV 로그 확인
   - `screenshots/` 폴더에서 오류 발생 시 캡처된 화면 확인

5. **실패한 파일 재시도**
   - 변환 완료 후 "실패한 파일만 재시도" 버튼으로 재시도

## 프로젝트 구조

```
hancell-converter/
├── app.py                      # 메인 애플리케이션
├── requirements.txt            # Python 의존성
├── README.md                   # 이 파일
├── ui/
│   ├── __init__.py
│   └── main_window.py          # PySide6 기반 메인 윈도우
├── converter/
│   ├── __init__.py
│   ├── file_queue.py           # 파일 큐 관리
│   ├── hancell_worker.py       # 한셀 자동화 워커
│   └── logger.py               # CSV 로깅
├── utils/
│   ├── __init__.py
│   └── process.py              # 프로세스 관리
├── logs/                       # CSV 로그 저장 (자동 생성)
├── screenshots/                # 오류 스크린샷 (자동 생성)
└── output/                     # 변환된 파일 (기본 출력 폴더)
```

## 주요 클래스 및 모듈

### converter/file_queue.py
- `FileQueue`: 변환 작업 큐 관리
- `ConversionTask`: 개별 변환 작업 데이터
- `ConversionStatus`: 작업 상태 열거형 (PENDING, PROCESSING, SUCCESS, FAILED, SKIPPED)

### converter/hancell_worker.py
- `HancellWorker`: 한셀 자동화 실행
  - pywinauto 기반으로 한셀 UI를 제어하여 파일 열기, 저장, 변환 수행
  - 팝업 감지 및 스크린샷 자동 저장
- `HancellWorkerThread`: Qt 스레드 환경에서 워커 실행

### converter/logger.py
- `ConversionLogger`: CSV 로깅
  - 변환 결과를 타임스탬프와 함께 CSV로 기록
  - 실패한 파일 목록 추출 기능

### utils/process.py
- `ProcessManager`: 한셀 프로세스 관리
  - 한셀 경로 자동 탐지
  - 프로세스 시작/중지/재시작
  - 시스템에서 실행 중인 한셀 프로세스 관리

### ui/main_window.py
- `MainWindow`: 메인 UI 윈도우
  - 드래그앤드롭 영역
  - 변환 설정 (형식, 출력 폴더, 옵션)
  - 작업 테이블 (파일명, 경로, 변환 형식, 상태, 오류 메시지)
  - 진행률 표시 및 버튼 (시작, 재시도, 초기화, 중지)

## 변환 로직 상세

### pywinauto 기반 자동화
1. 한셀 프로세스가 실행 중이 아니면 시작
2. `Ctrl+O`로 파일 열기 대화상자 열기
3. 파일 경로 입력 후 `Enter`로 파일 열기
4. 매크로 경고, 읽기 전용 등 팝업 체크
   - 팝업 발견 시 스크린샷 저장 후 실패 처리
5. `F12`로 다른 이름으로 저장 대화상자 열기
6. 출력 경로 및 형식 지정 후 저장
7. `Ctrl+W`로 파일 닫기
8. 다음 파일로 반복

### win32com 기반 자동화 (참고용)
- 한셀의 COM 인터페이스가 제한적이거나 문서화되지 않았을 수 있음
- `hancell_worker.py`의 `_convert_with_win32com` 메서드에 스켈레톤 코드 포함
- 실제 구현은 한셀 버전 및 API 문서에 따라 조정 필요

## 로그 및 출력

### CSV 로그
- 위치: `logs/conversion_log_YYYYMMDD_HHMMSS.csv`
- 형식:
  ```
  Timestamp,Source File,Target Format,Output File,Status,Error Message
  2024-05-07 10:30:15,C:\Files\test.cell,PDF,C:\Output\test.pdf,SUCCESS,
  2024-05-07 10:30:20,C:\Files\test2.cell,PDF,C:\Output\test2.pdf,FAILED,팝업 발견
  ```

### 스크린샷
- 위치: `screenshots/`
- 파일명: `{파일명}_{이유}_{타임스탬프}.png`
- 예: `test_popup_detected_20240507_103020.png`

## 문제 해결

### 한셀을 찾을 수 없음
- `utils/process.py`의 `_find_hancell_path` 메서드에서 검색하는 경로 확인
- 한셀 설치 경로가 다르면 수동으로 경로 지정:
  ```python
  process_manager = ProcessManager(hancell_path=r"C:\Your\Path\HCell.exe")
  ```

### 변환이 실패함
- `screenshots/` 폴더에서 캡처된 화면 확인
- `logs/` 폴더에서 CSV 로그의 Error Message 열 확인
- 한셀 UI 구조가 버전마다 다를 수 있으므로 `hancell_worker.py`의 키 입력 순서 조정 필요

### 프로세스가 종료되지 않음
- 작업 관리자에서 한셀 프로세스를 수동으로 종료
- 애플리케이션 종료 시 `closeEvent`에서 자동으로 정리하지만, 비정상 종료 시 수동 정리 필요

## 라이선스

이 프로젝트는 교육 및 개인 사용 목적으로 제작되었습니다.

## 기여

버그 리포트 및 기능 제안은 이슈로 등록해 주세요.

## 주의사항

- **로컬 변환만 지원**: 외부 API나 원격 서버를 사용하지 않으며, 모든 변환은 로컬 한셀에서 수행됩니다.
- **대량 파일 처리**: 수백 개의 파일을 처리할 때는 프로세스 재시작 간격을 적절히 설정하여 안정성을 확보하세요.
- **백업 권장**: 변환 전 원본 파일을 백업하는 것을 권장합니다.

"""
애플리케이션 설정
필요에 따라 이 파일을 수정하여 기본값을 변경할 수 있습니다.
"""

# 지원되는 파일 확장자
SUPPORTED_EXTENSIONS = ['.cell', '.nxl', '.xls', '.xlsx']

# 변환 가능한 형식
AVAILABLE_FORMATS = ['PDF', 'HTML', 'XLS', 'XLSX']

# 기본 출력 디렉토리
DEFAULT_OUTPUT_DIR = 'output'

# 기본 로그 디렉토리
DEFAULT_LOG_DIR = 'logs'

# 기본 스크린샷 디렉토리
DEFAULT_SCREENSHOT_DIR = 'screenshots'

# 프로세스 재시작 기본 간격 (0이면 재시작 안함)
DEFAULT_RESTART_INTERVAL = 50

# 한셀 실행 파일명
HANCELL_PROCESS_NAMES = ['HCell.exe', 'HncCell.exe', 'Hcell.exe']

# 한셀 일반 설치 경로 (자동 검색 순서)
HANCELL_COMMON_PATHS = [
    r"C:\Program Files\Hancom\Office 2022\HCell.exe",
    r"C:\Program Files\Hancom\Office 2020\HCell.exe",
    r"C:\Program Files\Hancom\Office 2018\HCell.exe",
    r"C:\Program Files\Hancom\Office NEO\HCell.exe",
    r"C:\Program Files (x86)\Hancom\Office 2022\HCell.exe",
    r"C:\Program Files (x86)\Hancom\Office 2020\HCell.exe",
    r"C:\Program Files (x86)\Hancom\Office 2018\HCell.exe",
    r"C:\Program Files (x86)\Hancom\Office NEO\HCell.exe",
]

# 변환 타임아웃 (초)
CONVERSION_TIMEOUT = 60

# 팝업 감지 키워드
POPUP_KEYWORDS = [
    '경고', '오류', 'Error', 'Warning',
    '읽기 전용', '매크로', '보안',
    'Read-Only', 'Macro', 'Security'
]

# UI 설정
UI_WINDOW_TITLE = "한셀 파일 일괄 변환기"
UI_WINDOW_WIDTH = 1000
UI_WINDOW_HEIGHT = 700
UI_DROP_ZONE_MIN_HEIGHT = 150

"""
한셀 파일 일괄 변환기
Windows 로컬 데스크톱 애플리케이션

드래그앤드롭으로 한셀 파일을 PDF, HTML, XLS, XLSX로 일괄 변환합니다.
"""
import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from PySide6.QtWidgets import QApplication
from ui.main_window import MainWindow


def main():
    """메인 함수"""
    app = QApplication(sys.argv)

    # 애플리케이션 정보 설정
    app.setApplicationName("한셀 파일 일괄 변환기")
    app.setOrganizationName("HancellConverter")
    app.setApplicationVersion("1.0.0")

    # 메인 윈도우 생성 및 표시
    window = MainWindow()
    window.show()

    # 이벤트 루프 실행
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

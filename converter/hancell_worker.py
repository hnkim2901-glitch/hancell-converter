"""
한셀 자동화 워커 모듈
pywinauto를 사용하여 한셀에서 파일 변환을 자동화합니다.
"""
import os
import time
from pathlib import Path
from typing import Optional, Callable
from datetime import datetime

try:
    from pywinauto import Desktop, Application
    from pywinauto.keyboard import send_keys
    from pywinauto.timings import TimeoutError as PywinautoTimeoutError
    PYWINAUTO_AVAILABLE = True
except ImportError:
    PYWINAUTO_AVAILABLE = False

try:
    import win32com.client
    WIN32COM_AVAILABLE = True
except ImportError:
    WIN32COM_AVAILABLE = False

from PIL import ImageGrab
from .file_queue import ConversionTask, ConversionStatus
from .logger import ConversionLogger
from utils.process import ProcessManager


class HancellWorker:
    """한셀 자동화 워커 클래스"""

    # 변환 형식별 확장자 매핑
    FORMAT_EXTENSIONS = {
        'PDF': '.pdf',
        'HTML': '.html',
        'XLS': '.xls',
        'XLSX': '.xlsx'
    }

    def __init__(self,
                 logger: ConversionLogger,
                 process_manager: ProcessManager,
                 restart_interval: int = 50):
        """
        Args:
            logger: 로거 인스턴스
            process_manager: 프로세스 관리자
            restart_interval: 몇 개 파일마다 프로세스를 재시작할지 (0이면 재시작 안함)
        """
        self.logger = logger
        self.process_manager = process_manager
        self.restart_interval = restart_interval
        self.conversion_count = 0

        self.screenshot_dir = Path("screenshots")
        self.screenshot_dir.mkdir(exist_ok=True)

    def convert_task(self,
                    task: ConversionTask,
                    progress_callback: Optional[Callable] = None) -> bool:
        """
        작업 변환 실행

        Args:
            task: 변환 작업
            progress_callback: 진행 상황 콜백 함수

        Returns:
            성공 여부
        """
        # 프로세스 재시작 체크
        if self.restart_interval > 0 and self.conversion_count >= self.restart_interval:
            if progress_callback:
                progress_callback(f"프로세스 재시작 중... ({self.conversion_count}개 변환 완료)")

            self.process_manager.restart_hancell()
            self.conversion_count = 0

        success = True

        for target_format in task.target_formats:
            output_path = task.get_output_path(target_format)

            if progress_callback:
                progress_callback(f"{Path(task.source_file).name} → {target_format} 변환 중...")

            # pywinauto 방식으로 변환 시도
            result = self._convert_with_pywinauto(
                task.source_file,
                target_format,
                output_path
            )

            # 로깅
            if result:
                self.logger.log_conversion(
                    task.source_file,
                    target_format,
                    output_path,
                    "SUCCESS"
                )
            else:
                self.logger.log_conversion(
                    task.source_file,
                    target_format,
                    output_path,
                    "FAILED",
                    task.error_message
                )
                success = False

        self.conversion_count += 1
        return success

    def _convert_with_pywinauto(self,
                               source_file: str,
                               target_format: str,
                               output_path: str) -> bool:
        """
        pywinauto를 사용한 변환

        Args:
            source_file: 원본 파일 경로
            target_format: 변환 형식
            output_path: 출력 파일 경로

        Returns:
            성공 여부
        """
        if not PYWINAUTO_AVAILABLE:
            return False

        try:
            # 한셀이 실행 중이 아니면 시작
            if not self.process_manager.is_hancell_running():
                self.process_manager.start_hancell()
                time.sleep(3)

            # 데스크톱에서 한셀 윈도우 찾기
            desktop = Desktop(backend="uia")
            app = None

            # 한셀 윈도우 찾기 (여러 가능한 이름 시도)
            for window_name in ['한셀', 'HCell', 'Hancom Cell']:
                try:
                    app = Application(backend="uia").connect(title_re=f".*{window_name}.*", timeout=5)
                    break
                except:
                    continue

            if not app:
                # 프로세스 이름으로 연결 시도
                try:
                    app = Application(backend="uia").connect(path=self.process_manager.hancell_path, timeout=5)
                except:
                    return False

            # 파일 열기: Ctrl+O
            send_keys('^o')
            time.sleep(1)

            # 파일 경로 입력
            send_keys(source_file)
            time.sleep(0.5)

            # 엔터로 열기
            send_keys('{ENTER}')
            time.sleep(2)

            # 팝업 체크 (예: 매크로 경고, 읽기 전용 등)
            if self._check_popup():
                self._save_screenshot(source_file, "popup_detected")
                return False

            # 다른 이름으로 저장: F12 또는 Ctrl+Shift+S
            send_keys('{F12}')
            time.sleep(1)

            # 출력 경로 입력
            send_keys(output_path)
            time.sleep(0.5)

            # 형식별 처리
            if target_format in ['PDF', 'HTML']:
                # PDF/HTML은 별도 대화상자에서 저장
                send_keys('{ENTER}')
                time.sleep(1)

                # 추가 옵션 대화상자가 나올 수 있음
                send_keys('{ENTER}')
                time.sleep(2)

            else:
                # XLS, XLSX는 파일 형식 선택 필요
                # (실제 구현에서는 한셀 UI 구조에 맞게 조정 필요)
                send_keys('{ENTER}')
                time.sleep(2)

            # 저장 완료 확인
            if not Path(output_path).exists():
                return False

            # 파일 닫기: Ctrl+W
            send_keys('^w')
            time.sleep(0.5)

            return True

        except Exception as e:
            print(f"변환 실패: {e}")
            self._save_screenshot(source_file, f"error_{target_format}")
            return False

    def _convert_with_win32com(self,
                              source_file: str,
                              target_format: str,
                              output_path: str) -> bool:
        """
        win32com을 사용한 변환 (참고용 스켈레톤)

        Args:
            source_file: 원본 파일 경로
            target_format: 변환 형식
            output_path: 출력 파일 경로

        Returns:
            성공 여부
        """
        if not WIN32COM_AVAILABLE:
            return False

        try:
            # 한셀의 COM 인터페이스가 공개되어 있다면 사용 가능
            # 예: Excel과 유사한 방식
            # hancell = win32com.client.Dispatch("HCell.Application")
            # hancell.Visible = False
            # workbook = hancell.Workbooks.Open(source_file)
            # workbook.SaveAs(output_path, FileFormat=...)
            # workbook.Close()

            # 한셀의 COM 인터페이스는 제한적이거나 문서화되지 않았을 수 있음
            # 실제 구현은 한셀 버전 및 API 문서에 따라 조정 필요

            return False

        except Exception as e:
            print(f"COM 변환 실패: {e}")
            return False

    def _check_popup(self) -> bool:
        """
        예상치 못한 팝업 확인

        Returns:
            팝업이 있으면 True
        """
        try:
            desktop = Desktop(backend="uia")

            # 일반적인 대화상자 타이틀들
            popup_keywords = [
                '경고', '오류', 'Error', 'Warning',
                '읽기 전용', '매크로', '보안',
                'Read-Only', 'Macro', 'Security'
            ]

            for window in desktop.windows():
                try:
                    title = window.window_text()
                    if any(keyword in title for keyword in popup_keywords):
                        return True
                except:
                    pass

            return False

        except:
            return False

    def _save_screenshot(self, source_file: str, reason: str):
        """
        스크린샷 저장

        Args:
            source_file: 원본 파일 경로
            reason: 스크린샷 이유 (파일명에 포함)
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_name = Path(source_file).stem
            screenshot_path = self.screenshot_dir / f"{file_name}_{reason}_{timestamp}.png"

            # 전체 화면 캡처
            screenshot = ImageGrab.grab()
            screenshot.save(screenshot_path)

        except Exception as e:
            print(f"스크린샷 저장 실패: {e}")


class HancellWorkerThread:
    """
    별도 스레드에서 실행되는 워커 래퍼
    Qt 환경에서 사용하기 위한 클래스
    """

    def __init__(self, worker: HancellWorker):
        self.worker = worker
        self.is_running = False

    def start(self):
        """워커 시작"""
        self.is_running = True

    def stop(self):
        """워커 중지"""
        self.is_running = False

    def process_queue(self, queue, progress_callback=None, completion_callback=None):
        """
        큐의 작업들을 순차적으로 처리

        Args:
            queue: FileQueue 인스턴스
            progress_callback: 진행 상황 콜백
            completion_callback: 완료 콜백
        """
        while self.is_running:
            task = queue.get_next_task()

            if not task:
                break

            queue.mark_task_status(task, ConversionStatus.PROCESSING)

            success = self.worker.convert_task(task, progress_callback)

            if success:
                queue.mark_task_status(task, ConversionStatus.SUCCESS)
            else:
                queue.mark_task_status(task, ConversionStatus.FAILED,
                                      "변환 실패")

        if completion_callback:
            completion_callback()

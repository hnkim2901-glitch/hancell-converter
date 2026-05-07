"""
프로세스 관리 유틸리티
한셀 프로세스의 시작/종료/재시작을 관리합니다.
"""
import subprocess
import time
import psutil
from typing import Optional, List


class ProcessManager:
    """한셀 프로세스 관리 클래스"""

    HANCELL_PROCESS_NAMES = ['HCell.exe', 'HncCell.exe', 'Hcell.exe']

    def __init__(self, hancell_path: Optional[str] = None):
        """
        Args:
            hancell_path: 한셀 실행 파일 경로 (None이면 자동 검색)
        """
        self.hancell_path = hancell_path
        self.process: Optional[subprocess.Popen] = None

        if not self.hancell_path:
            self.hancell_path = self._find_hancell_path()

    def start_hancell(self) -> bool:
        """
        한셀 프로세스 시작

        Returns:
            성공 여부
        """
        if not self.hancell_path:
            return False

        try:
            # 한셀 실행
            self.process = subprocess.Popen(
                [self.hancell_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            # 프로세스가 시작될 때까지 대기
            time.sleep(3)

            return self.is_hancell_running()

        except Exception as e:
            print(f"한셀 시작 실패: {e}")
            return False

    def stop_hancell(self):
        """모든 한셀 프로세스 종료"""
        # 실행한 프로세스가 있으면 종료
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=5)
            except:
                self.process.kill()
            finally:
                self.process = None

        # 시스템에 남아있는 한셀 프로세스 종료
        self._kill_all_hancell_processes()

    def restart_hancell(self) -> bool:
        """
        한셀 프로세스 재시작

        Returns:
            성공 여부
        """
        self.stop_hancell()
        time.sleep(2)
        return self.start_hancell()

    def is_hancell_running(self) -> bool:
        """한셀이 실행 중인지 확인"""
        for proc in psutil.process_iter(['name']):
            try:
                if proc.info['name'] in self.HANCELL_PROCESS_NAMES:
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        return False

    def _find_hancell_path(self) -> Optional[str]:
        """
        시스템에서 한셀 실행 파일 경로 찾기

        Returns:
            한셀 실행 파일 경로 또는 None
        """
        # 일반적인 설치 경로들
        common_paths = [
            r"C:\Program Files\Hancom\Office 2022\HCell.exe",
            r"C:\Program Files\Hancom\Office 2020\HCell.exe",
            r"C:\Program Files\Hancom\Office 2018\HCell.exe",
            r"C:\Program Files\Hancom\Office NEO\HCell.exe",
            r"C:\Program Files (x86)\Hancom\Office 2022\HCell.exe",
            r"C:\Program Files (x86)\Hancom\Office 2020\HCell.exe",
            r"C:\Program Files (x86)\Hancom\Office 2018\HCell.exe",
            r"C:\Program Files (x86)\Hancom\Office NEO\HCell.exe",
        ]

        import os
        for path in common_paths:
            if os.path.exists(path):
                return path

        # 실행 중인 한셀 프로세스에서 경로 찾기
        for proc in psutil.process_iter(['name', 'exe']):
            try:
                if proc.info['name'] in self.HANCELL_PROCESS_NAMES:
                    return proc.info['exe']
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        return None

    def _kill_all_hancell_processes(self):
        """시스템의 모든 한셀 프로세스 강제 종료"""
        for proc in psutil.process_iter(['name']):
            try:
                if proc.info['name'] in self.HANCELL_PROCESS_NAMES:
                    proc.kill()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        time.sleep(1)

    def get_hancell_windows(self) -> List:
        """
        실행 중인 한셀 윈도우 목록 반환 (pywinauto용)

        Returns:
            윈도우 핸들 리스트
        """
        try:
            from pywinauto import Desktop

            desktop = Desktop(backend="uia")
            windows = []

            for window in desktop.windows():
                try:
                    # 한셀 윈도우 찾기
                    if any(name.lower() in window.window_text().lower()
                          for name in ['cell', '한셀', 'hancell']):
                        windows.append(window)
                except:
                    pass

            return windows

        except ImportError:
            return []

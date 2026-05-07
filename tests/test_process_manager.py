"""
ProcessManager 테스트
Mock을 사용하여 프로세스 관리 로직 테스트
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path


class TestProcessManager:
    """ProcessManager 테스트 (Mock 사용)"""

    def test_create_process_manager(self):
        """프로세스 매니저 생성 테스트"""
        from utils.process import ProcessManager

        manager = ProcessManager()
        assert manager is not None

    def test_find_hancell_path(self):
        """한셀 경로 찾기 테스트 (Mock)"""
        from utils.process import ProcessManager

        # 실제 파일이 없어도 로직은 동작해야 함
        manager = ProcessManager()

        # Mac에서는 한셀을 찾을 수 없지만, 에러가 발생하지 않아야 함
        assert manager.hancell_path is None or isinstance(manager.hancell_path, str)

    def test_is_hancell_running(self):
        """한셀 실행 확인 테스트 (Mock)"""
        from utils.process import ProcessManager

        manager = ProcessManager()
        running = manager.is_hancell_running()

        # Mock 환경에서는 항상 True 반환 (mock_windows.py에서 설정)
        assert isinstance(running, bool)
        assert running is True  # MockPsutil이 HCell.exe를 반환하므로

    @patch('subprocess.Popen')
    def test_start_hancell_mock(self, mock_popen):
        """한셀 시작 테스트 (Mock)"""
        from utils.process import ProcessManager

        # Mock 설정
        mock_popen.return_value = Mock()

        manager = ProcessManager(hancell_path=r"C:\fake\path\HCell.exe")
        result = manager.start_hancell()

        # 경로가 설정되어 있으면 시작 시도
        if manager.hancell_path:
            assert result is True

    def test_stop_hancell(self):
        """한셀 중지 테스트 (Mock)"""
        from utils.process import ProcessManager

        manager = ProcessManager()
        manager.process = Mock()

        # 중지 시 에러가 발생하지 않아야 함
        manager.stop_hancell()

        # 프로세스가 None으로 설정되어야 함
        assert manager.process is None

    def test_restart_hancell(self):
        """한셀 재시작 테스트 (Mock)"""
        from utils.process import ProcessManager

        manager = ProcessManager(hancell_path=r"C:\fake\path\HCell.exe")

        # 재시작이 에러 없이 실행되어야 함
        # (실제 프로세스는 시작되지 않지만 로직은 테스트됨)
        result = manager.restart_hancell()

        assert isinstance(result, bool)

    def test_get_hancell_windows(self):
        """한셀 윈도우 목록 테스트 (Mock)"""
        from utils.process import ProcessManager

        manager = ProcessManager()
        windows = manager.get_hancell_windows()

        # Mock 환경에서는 윈도우 목록 반환
        assert isinstance(windows, list)
        # mock_windows.py에서 한셀 윈도우 1개 반환
        assert len(windows) >= 1

    def test_process_names_defined(self):
        """한셀 프로세스 이름 정의 확인"""
        from utils.process import ProcessManager

        assert hasattr(ProcessManager, 'HANCELL_PROCESS_NAMES')
        assert isinstance(ProcessManager.HANCELL_PROCESS_NAMES, list)
        assert len(ProcessManager.HANCELL_PROCESS_NAMES) > 0
        assert 'HCell.exe' in ProcessManager.HANCELL_PROCESS_NAMES

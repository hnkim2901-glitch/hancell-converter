"""
HancellWorker 테스트
Mock을 사용하여 변환 워커 로직 테스트
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
from converter.file_queue import ConversionTask
from converter.logger import ConversionLogger
from utils.process import ProcessManager


class TestHancellWorker:
    """HancellWorker 테스트 (Mock 사용)"""

    @pytest.fixture
    def mock_logger(self, log_dir):
        """Mock 로거"""
        return ConversionLogger(log_dir)

    @pytest.fixture
    def mock_process_manager(self):
        """Mock 프로세스 매니저"""
        return ProcessManager()

    @pytest.fixture
    def worker(self, mock_logger, mock_process_manager):
        """워커 인스턴스"""
        from converter.hancell_worker import HancellWorker

        return HancellWorker(
            logger=mock_logger,
            process_manager=mock_process_manager,
            restart_interval=50
        )

    @pytest.fixture
    def sample_task(self, temp_dir, output_dir):
        """샘플 변환 작업"""
        source = Path(temp_dir) / "test.cell"
        source.write_text("mock content")

        return ConversionTask(
            source_file=str(source),
            target_formats=['PDF', 'HTML'],
            output_dir=output_dir
        )

    def test_create_worker(self, worker):
        """워커 생성 테스트"""
        assert worker is not None
        assert worker.restart_interval == 50
        assert worker.conversion_count == 0
        assert worker.screenshot_dir.exists()

    def test_format_extensions_defined(self, worker):
        """변환 형식 확장자 매핑 확인"""
        assert hasattr(worker, 'FORMAT_EXTENSIONS')
        assert worker.FORMAT_EXTENSIONS['PDF'] == '.pdf'
        assert worker.FORMAT_EXTENSIONS['HTML'] == '.html'
        assert worker.FORMAT_EXTENSIONS['XLS'] == '.xls'
        assert worker.FORMAT_EXTENSIONS['XLSX'] == '.xlsx'

    @patch('converter.hancell_worker.HancellWorker._convert_with_pywinauto')
    def test_convert_task_success(self, mock_convert, worker, sample_task):
        """작업 변환 성공 테스트"""
        # Mock 설정: 변환 성공
        mock_convert.return_value = True

        result = worker.convert_task(sample_task)

        # 성공 반환
        assert result is True

        # 변환 횟수 증가
        assert worker.conversion_count == 1

        # 각 형식마다 변환 호출됨
        assert mock_convert.call_count == len(sample_task.target_formats)

    @patch('converter.hancell_worker.HancellWorker._convert_with_pywinauto')
    def test_convert_task_failure(self, mock_convert, worker, sample_task):
        """작업 변환 실패 테스트"""
        # Mock 설정: 변환 실패
        mock_convert.return_value = False

        result = worker.convert_task(sample_task)

        # 실패 반환
        assert result is False

    @patch('converter.hancell_worker.HancellWorker._convert_with_pywinauto')
    def test_restart_interval(self, mock_convert, worker, sample_task):
        """프로세스 재시작 간격 테스트"""
        mock_convert.return_value = True
        worker.restart_interval = 2  # 2개마다 재시작

        # 첫 번째 변환
        worker.convert_task(sample_task)
        assert worker.conversion_count == 1

        # 두 번째 변환
        worker.convert_task(sample_task)
        assert worker.conversion_count == 2

        # 세 번째 변환 (재시작 트리거: count=2 >= 2)
        worker.convert_task(sample_task)
        # 재시작 후 카운트 리셋되고 다시 증가
        assert worker.conversion_count == 1

    def test_convert_with_pywinauto_mock(self, worker, sample_task, output_dir):
        """pywinauto 변환 Mock 테스트"""
        # Mock 환경에서는 실제 변환이 불가능하므로 False 반환
        result = worker._convert_with_pywinauto(
            sample_task.source_file,
            'PDF',
            str(Path(output_dir) / 'test.pdf')
        )

        # Mock 환경이므로 실패 (실제 한셀이 없음)
        # 하지만 에러는 발생하지 않아야 함
        assert isinstance(result, bool)

    def test_check_popup(self, worker):
        """팝업 체크 테스트 (Mock)"""
        # Mock 환경에서 팝업 체크 실행
        has_popup = worker._check_popup()

        # Mock 환경에서는 False 반환 (팝업 없음)
        assert isinstance(has_popup, bool)
        assert has_popup is False

    def test_save_screenshot(self, worker, temp_dir):
        """스크린샷 저장 테스트 (Mock)"""
        source_file = str(Path(temp_dir) / "test.cell")

        # 스크린샷 저장 (Mock 환경에서는 빈 파일 생성)
        worker._save_screenshot(source_file, "test_reason")

        # screenshot 폴더에 파일이 생성되어야 함
        screenshots = list(worker.screenshot_dir.glob("*.png"))
        assert len(screenshots) >= 1

    def test_progress_callback(self, worker, sample_task):
        """진행 상황 콜백 테스트"""
        messages = []

        def callback(msg):
            messages.append(msg)

        # pywinauto 변환이 실패하지만 콜백은 호출되어야 함
        worker.convert_task(sample_task, progress_callback=callback)

        # 콜백이 호출됨
        assert len(messages) > 0

    def test_multiple_formats(self, worker, sample_task):
        """여러 형식 동시 변환 테스트"""
        sample_task.target_formats = ['PDF', 'HTML', 'XLS', 'XLSX']

        with patch('converter.hancell_worker.HancellWorker._convert_with_pywinauto') as mock_convert:
            mock_convert.return_value = True
            worker.convert_task(sample_task)

            # 4개 형식 모두 변환 시도
            assert mock_convert.call_count == 4


class TestHancellWorkerThread:
    """HancellWorkerThread 테스트"""

    def test_create_thread(self, log_dir):
        """워커 스레드 생성 테스트"""
        from converter.hancell_worker import HancellWorker, HancellWorkerThread
        from converter.file_queue import FileQueue

        logger = ConversionLogger(log_dir)
        process_manager = ProcessManager()
        worker = HancellWorker(logger, process_manager)

        thread = HancellWorkerThread(worker)

        assert thread is not None
        assert thread.worker == worker
        assert thread.is_running is False

    def test_start_stop_thread(self, log_dir):
        """워커 스레드 시작/중지 테스트"""
        from converter.hancell_worker import HancellWorker, HancellWorkerThread

        logger = ConversionLogger(log_dir)
        process_manager = ProcessManager()
        worker = HancellWorker(logger, process_manager)

        thread = HancellWorkerThread(worker)

        thread.start()
        assert thread.is_running is True

        thread.stop()
        assert thread.is_running is False

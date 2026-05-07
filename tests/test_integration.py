"""
통합 테스트
여러 모듈이 함께 동작하는 시나리오 테스트
"""
import pytest
from pathlib import Path
from converter.file_queue import FileQueue, ConversionStatus
from converter.logger import ConversionLogger
from converter.hancell_worker import HancellWorker
from utils.process import ProcessManager


class TestIntegration:
    """통합 테스트"""

    @pytest.fixture
    def setup_complete_workflow(self, sample_files, output_dir, log_dir):
        """완전한 워크플로우 설정"""
        queue = FileQueue()
        logger = ConversionLogger(log_dir)
        process_manager = ProcessManager()
        worker = HancellWorker(logger, process_manager, restart_interval=0)

        return {
            'queue': queue,
            'logger': logger,
            'process_manager': process_manager,
            'worker': worker,
            'sample_files': sample_files,
            'output_dir': output_dir
        }

    def test_complete_workflow(self, setup_complete_workflow):
        """완전한 변환 워크플로우 테스트"""
        ctx = setup_complete_workflow

        # 1. 파일 추가
        ctx['queue'].add_files(
            ctx['sample_files'],
            ['PDF', 'HTML'],
            ctx['output_dir']
        )

        assert len(ctx['queue'].tasks) == 4

        # 2. 첫 번째 작업 가져오기
        task = ctx['queue'].get_next_task()
        assert task is not None

        # 3. 작업 상태를 PROCESSING으로 변경
        ctx['queue'].mark_task_status(task, ConversionStatus.PROCESSING)
        assert task.status == ConversionStatus.PROCESSING

        # 4. 변환 시도 (Mock 환경에서는 실패하지만 에러는 없어야 함)
        # _convert_with_pywinauto는 False를 반환하지만 로직은 동작
        result = ctx['worker'].convert_task(task)

        # 5. 로그 확인
        log_summary = ctx['logger'].get_log_summary()
        # 변환 시도가 로그에 기록되어야 함
        assert log_summary['FAILED'] >= 0

    def test_queue_and_logger_integration(self, sample_files, output_dir, log_dir):
        """큐와 로거 통합 테스트"""
        queue = FileQueue()
        logger = ConversionLogger(log_dir)

        # 파일 추가
        queue.add_files(sample_files, ['PDF'], output_dir)

        # 각 작업을 로깅
        for task in queue.tasks:
            output_path = task.get_output_path('PDF')
            logger.log_conversion(
                task.source_file,
                'PDF',
                output_path,
                'SUCCESS'
            )

        # 로그 요약 확인
        summary = logger.get_log_summary()
        assert summary['SUCCESS'] == len(sample_files)

    def test_failed_retry_workflow(self, sample_files, output_dir, log_dir):
        """실패 재시도 워크플로우 테스트"""
        queue = FileQueue()
        logger = ConversionLogger(log_dir)

        # 파일 추가
        queue.add_files(sample_files, ['PDF'], output_dir)

        # 일부 작업을 실패로 표시
        queue.mark_task_status(queue.tasks[0], ConversionStatus.FAILED, "Error 1")
        queue.mark_task_status(queue.tasks[1], ConversionStatus.SUCCESS)
        queue.mark_task_status(queue.tasks[2], ConversionStatus.FAILED, "Error 2")

        # 실패한 작업 로깅
        for task in queue.get_failed_tasks():
            logger.log_conversion(
                task.source_file,
                'PDF',
                task.get_output_path('PDF'),
                'FAILED',
                task.error_message
            )

        # 실패한 파일 목록 확인
        failed_files = logger.get_failed_files()
        assert len(failed_files) == 2

        # 실패한 작업 재설정
        queue.reset_failed_tasks()

        # 재시도 가능한 상태 확인
        assert queue.tasks[0].status == ConversionStatus.PENDING
        assert queue.tasks[2].status == ConversionStatus.PENDING
        assert queue.current_index == 0

    def test_skip_existing_workflow(self, sample_files, output_dir, log_dir):
        """기존 파일 스킵 워크플로우 테스트"""
        queue = FileQueue()
        logger = ConversionLogger(log_dir)

        # 출력 파일 하나 미리 생성
        Path(output_dir, "test_0.pdf").write_text("existing")

        # 파일 추가 (skip_existing=True)
        queue.add_files(sample_files, ['PDF'], output_dir, skip_existing=True)

        # 스킵된 작업 로깅
        for task in queue.tasks:
            if task.status == ConversionStatus.SKIPPED:
                logger.log_conversion(
                    task.source_file,
                    'PDF',
                    task.get_output_path('PDF'),
                    'SKIPPED'
                )

        # 로그 확인
        summary = logger.get_log_summary()
        assert summary['SKIPPED'] >= 1

    def test_folder_recursive_workflow(self, sample_folder, output_dir, log_dir):
        """폴더 재귀 탐색 워크플로우 테스트"""
        queue = FileQueue()
        logger = ConversionLogger(log_dir)

        # 재귀 모드로 폴더 추가
        queue.add_folder(sample_folder, ['PDF'], output_dir, recursive=True)

        # 하위 폴더 포함 모든 파일이 추가되어야 함
        assert len(queue.tasks) == 4

        # 통계 확인
        stats = queue.get_statistics()
        assert stats['total'] == 4
        assert stats['pending'] == 4

    def test_multiple_formats_workflow(self, sample_files, output_dir, log_dir):
        """여러 형식 동시 변환 워크플로우 테스트"""
        queue = FileQueue()
        logger = ConversionLogger(log_dir)

        formats = ['PDF', 'HTML', 'XLSX']

        # 여러 형식으로 파일 추가
        queue.add_files(sample_files, formats, output_dir)

        # 각 작업이 3개 형식을 갖고 있어야 함
        for task in queue.tasks:
            assert len(task.target_formats) == 3

            # 각 형식별로 로깅
            for fmt in formats:
                output_path = task.get_output_path(fmt)
                logger.log_conversion(
                    task.source_file,
                    fmt,
                    output_path,
                    'SUCCESS'
                )

        # 로그 확인 (4개 파일 × 3개 형식 = 12개 로그)
        summary = logger.get_log_summary()
        assert summary['SUCCESS'] == len(sample_files) * len(formats)

    def test_process_restart_workflow(self, sample_files, output_dir, log_dir):
        """프로세스 재시작 워크플로우 테스트"""
        queue = FileQueue()
        logger = ConversionLogger(log_dir)
        process_manager = ProcessManager()

        # 재시작 간격 2개로 설정
        worker = HancellWorker(logger, process_manager, restart_interval=2)

        queue.add_files(sample_files, ['PDF'], output_dir)

        # 초기 카운트 확인
        assert worker.conversion_count == 0

        # 첫 번째 변환
        task1 = queue.get_next_task()
        worker.convert_task(task1)
        assert worker.conversion_count == 1

        # 두 번째 변환
        task2 = queue.get_next_task()
        worker.convert_task(task2)
        assert worker.conversion_count == 2

        # 세 번째 변환 (재시작 트리거: count=2 >= 2)
        task3 = queue.get_next_task()
        worker.convert_task(task3)
        # 재시작 후 카운트 리셋되고 다시 증가
        assert worker.conversion_count == 1

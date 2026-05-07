"""
FileQueue 테스트
Windows 의존성 없이 파일 큐 로직을 테스트
"""
import pytest
from pathlib import Path
from converter.file_queue import FileQueue, ConversionTask, ConversionStatus


class TestConversionTask:
    """ConversionTask 테스트"""

    def test_create_task(self, temp_dir):
        """작업 생성 테스트"""
        task = ConversionTask(
            source_file="/path/to/test.cell",
            target_formats=['PDF', 'HTML'],
            output_dir=temp_dir
        )

        assert task.source_file == "/path/to/test.cell"
        assert task.target_formats == ['PDF', 'HTML']
        assert task.output_dir == temp_dir
        assert task.status == ConversionStatus.PENDING
        assert task.error_message == ""

    def test_get_output_path(self, temp_dir):
        """출력 경로 생성 테스트"""
        task = ConversionTask(
            source_file="/path/to/test.cell",
            target_formats=['PDF'],
            output_dir=temp_dir
        )

        pdf_path = task.get_output_path('PDF')
        assert pdf_path == str(Path(temp_dir) / "test.pdf")

        html_path = task.get_output_path('HTML')
        assert html_path == str(Path(temp_dir) / "test.html")


class TestFileQueue:
    """FileQueue 테스트"""

    def test_create_queue(self):
        """큐 생성 테스트"""
        queue = FileQueue()

        assert len(queue.tasks) == 0
        assert queue.current_index == 0

    def test_add_files(self, sample_files, output_dir):
        """파일 추가 테스트"""
        queue = FileQueue()
        queue.add_files(sample_files, ['PDF'], output_dir)

        assert len(queue.tasks) == 4  # .cell, .nxl, .xls, .xlsx

        for task in queue.tasks:
            assert task.status == ConversionStatus.PENDING
            assert 'PDF' in task.target_formats

    def test_add_files_with_skip_existing(self, sample_files, output_dir):
        """기존 파일 스킵 테스트"""
        # 출력 파일 하나 생성
        Path(output_dir, "test_0.pdf").write_text("existing")

        queue = FileQueue()
        queue.add_files(sample_files, ['PDF'], output_dir, skip_existing=True)

        # test_0.cell은 스킵되어야 함
        skipped_task = queue.tasks[0]
        assert skipped_task.status == ConversionStatus.SKIPPED
        assert len(skipped_task.target_formats) == 0

        # 나머지는 PENDING
        for task in queue.tasks[1:]:
            assert task.status == ConversionStatus.PENDING

    def test_add_folder_non_recursive(self, sample_folder, output_dir):
        """폴더 추가 (재귀 없음) 테스트"""
        queue = FileQueue()
        queue.add_folder(sample_folder, ['PDF'], output_dir, recursive=False)

        # 루트 레벨 파일만 추가되어야 함 (file1.cell, file2.xlsx)
        assert len(queue.tasks) == 2

    def test_add_folder_recursive(self, sample_folder, output_dir):
        """폴더 추가 (재귀) 테스트"""
        queue = FileQueue()
        queue.add_folder(sample_folder, ['PDF'], output_dir, recursive=True)

        # 모든 파일이 추가되어야 함 (file1.cell, file2.xlsx, file3.cell, file4.xls)
        assert len(queue.tasks) == 4

    def test_get_next_task(self, sample_files, output_dir):
        """다음 작업 가져오기 테스트"""
        queue = FileQueue()
        queue.add_files(sample_files, ['PDF'], output_dir)

        # 첫 번째 작업
        task1 = queue.get_next_task()
        assert task1 is not None
        assert task1.status == ConversionStatus.PENDING

        # 작업 완료 처리
        queue.mark_task_status(task1, ConversionStatus.SUCCESS)

        # 두 번째 작업
        task2 = queue.get_next_task()
        assert task2 is not None
        assert task2 != task1

    def test_mark_task_status(self, sample_files, output_dir):
        """작업 상태 변경 테스트"""
        queue = FileQueue()
        queue.add_files(sample_files, ['PDF'], output_dir)

        task = queue.tasks[0]
        queue.mark_task_status(task, ConversionStatus.PROCESSING)

        assert task.status == ConversionStatus.PROCESSING

        queue.mark_task_status(task, ConversionStatus.SUCCESS)
        assert task.status == ConversionStatus.SUCCESS
        assert queue.current_index == 1

    def test_get_failed_tasks(self, sample_files, output_dir):
        """실패한 작업 목록 테스트"""
        queue = FileQueue()
        queue.add_files(sample_files, ['PDF'], output_dir)

        # 일부 작업을 실패로 표시
        queue.mark_task_status(queue.tasks[0], ConversionStatus.FAILED, "Error 1")
        queue.mark_task_status(queue.tasks[1], ConversionStatus.SUCCESS)
        queue.mark_task_status(queue.tasks[2], ConversionStatus.FAILED, "Error 2")

        failed = queue.get_failed_tasks()
        assert len(failed) == 2
        assert failed[0].error_message == "Error 1"
        assert failed[1].error_message == "Error 2"

    def test_reset_failed_tasks(self, sample_files, output_dir):
        """실패한 작업 재설정 테스트"""
        queue = FileQueue()
        queue.add_files(sample_files, ['PDF'], output_dir)

        # 일부 작업을 실패로 표시
        queue.mark_task_status(queue.tasks[0], ConversionStatus.FAILED, "Error")
        queue.mark_task_status(queue.tasks[1], ConversionStatus.SUCCESS)

        queue.reset_failed_tasks()

        # 실패한 작업이 PENDING으로 재설정되어야 함
        assert queue.tasks[0].status == ConversionStatus.PENDING
        assert queue.tasks[0].error_message == ""

        # 성공한 작업은 그대로
        assert queue.tasks[1].status == ConversionStatus.SUCCESS

        # current_index가 0으로 재설정되어야 함
        assert queue.current_index == 0

    def test_get_statistics(self, sample_files, output_dir):
        """통계 정보 테스트"""
        queue = FileQueue()
        queue.add_files(sample_files, ['PDF'], output_dir)

        # 다양한 상태로 설정
        queue.mark_task_status(queue.tasks[0], ConversionStatus.SUCCESS)
        queue.mark_task_status(queue.tasks[1], ConversionStatus.FAILED)
        # tasks[2], tasks[3]는 PENDING

        stats = queue.get_statistics()

        assert stats['total'] == 4
        assert stats['success'] == 1
        assert stats['failed'] == 1
        assert stats['pending'] == 2

    def test_clear(self, sample_files, output_dir):
        """큐 초기화 테스트"""
        queue = FileQueue()
        queue.add_files(sample_files, ['PDF'], output_dir)

        assert len(queue.tasks) > 0

        queue.clear()

        assert len(queue.tasks) == 0
        assert queue.current_index == 0

    def test_multiple_formats(self, sample_files, output_dir):
        """여러 형식 동시 변환 테스트"""
        queue = FileQueue()
        formats = ['PDF', 'HTML', 'XLSX']
        queue.add_files(sample_files, formats, output_dir)

        for task in queue.tasks:
            assert task.target_formats == formats

    def test_unsupported_file_extension(self, temp_dir, output_dir):
        """지원하지 않는 파일 확장자 테스트"""
        # .txt 파일 생성 (지원하지 않음)
        txt_file = Path(temp_dir) / "test.txt"
        txt_file.write_text("text content")

        queue = FileQueue()
        queue.add_files([str(txt_file)], ['PDF'], output_dir)

        # 지원하지 않는 파일은 추가되지 않아야 함
        assert len(queue.tasks) == 0

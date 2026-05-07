"""
파일 큐 관리 모듈
변환할 파일 목록과 상태를 관리합니다.
"""
import os
from pathlib import Path
from typing import List, Set, Dict
from dataclasses import dataclass
from enum import Enum


class ConversionStatus(Enum):
    """변환 상태"""
    PENDING = "대기 중"
    PROCESSING = "변환 중"
    SUCCESS = "성공"
    FAILED = "실패"
    SKIPPED = "스킵됨"


@dataclass
class ConversionTask:
    """변환 작업 항목"""
    source_file: str
    target_formats: List[str]  # ['PDF', 'HTML', 'XLS', 'XLSX']
    output_dir: str
    status: ConversionStatus = ConversionStatus.PENDING
    error_message: str = ""

    def get_output_path(self, target_format: str) -> str:
        """
        출력 파일 경로 생성

        Args:
            target_format: 대상 형식 (PDF, HTML, XLS, XLSX)

        Returns:
            출력 파일 전체 경로
        """
        source_path = Path(self.source_file)
        file_name = source_path.stem
        ext = target_format.lower()

        return str(Path(self.output_dir) / f"{file_name}.{ext}")


class FileQueue:
    """파일 변환 큐 관리"""

    SUPPORTED_EXTENSIONS = {'.cell', '.nxl', '.xls', '.xlsx'}

    def __init__(self):
        self.tasks: List[ConversionTask] = []
        self.current_index: int = 0

    def add_files(self,
                  file_paths: List[str],
                  target_formats: List[str],
                  output_dir: str,
                  skip_existing: bool = True):
        """
        파일 목록을 큐에 추가

        Args:
            file_paths: 원본 파일 경로 리스트
            target_formats: 변환할 형식 리스트
            output_dir: 출력 디렉토리
            skip_existing: 기존 파일이 있으면 스킵할지 여부
        """
        for file_path in file_paths:
            if not self._is_supported_file(file_path):
                continue

            # 기존 파일 체크
            formats_to_convert = target_formats.copy()

            if skip_existing:
                formats_to_convert = [
                    fmt for fmt in target_formats
                    if not self._output_exists(file_path, fmt, output_dir)
                ]

            # 변환할 형식이 없으면 스킵 상태로 추가
            if not formats_to_convert:
                task = ConversionTask(
                    source_file=file_path,
                    target_formats=[],
                    output_dir=output_dir,
                    status=ConversionStatus.SKIPPED
                )
            else:
                task = ConversionTask(
                    source_file=file_path,
                    target_formats=formats_to_convert,
                    output_dir=output_dir
                )

            self.tasks.append(task)

    def add_folder(self,
                   folder_path: str,
                   target_formats: List[str],
                   output_dir: str,
                   recursive: bool = False,
                   skip_existing: bool = True):
        """
        폴더 내 파일들을 큐에 추가

        Args:
            folder_path: 폴더 경로
            target_formats: 변환할 형식 리스트
            output_dir: 출력 디렉토리
            recursive: 하위 폴더 포함 여부
            skip_existing: 기존 파일이 있으면 스킵할지 여부
        """
        folder = Path(folder_path)

        if recursive:
            pattern = "**/*"
        else:
            pattern = "*"

        file_paths = [
            str(f) for f in folder.glob(pattern)
            if f.is_file() and self._is_supported_file(str(f))
        ]

        self.add_files(file_paths, target_formats, output_dir, skip_existing)

    def get_next_task(self) -> ConversionTask:
        """
        다음 처리할 작업 반환

        Returns:
            다음 ConversionTask 또는 None
        """
        while self.current_index < len(self.tasks):
            task = self.tasks[self.current_index]

            # 이미 처리된 작업은 스킵
            if task.status in [ConversionStatus.SUCCESS,
                              ConversionStatus.SKIPPED]:
                self.current_index += 1
                continue

            return task

        return None

    def mark_task_status(self, task: ConversionTask, status: ConversionStatus, error_msg: str = ""):
        """작업 상태 업데이트"""
        task.status = status
        task.error_message = error_msg

        if status in [ConversionStatus.SUCCESS, ConversionStatus.FAILED, ConversionStatus.SKIPPED]:
            self.current_index += 1

    def get_failed_tasks(self) -> List[ConversionTask]:
        """실패한 작업 목록 반환"""
        return [t for t in self.tasks if t.status == ConversionStatus.FAILED]

    def reset_failed_tasks(self):
        """실패한 작업들을 PENDING 상태로 재설정"""
        for task in self.tasks:
            if task.status == ConversionStatus.FAILED:
                task.status = ConversionStatus.PENDING
                task.error_message = ""

        self.current_index = 0

    def get_statistics(self) -> Dict[str, int]:
        """통계 정보 반환"""
        stats = {
            'total': len(self.tasks),
            'pending': 0,
            'processing': 0,
            'success': 0,
            'failed': 0,
            'skipped': 0
        }

        for task in self.tasks:
            if task.status == ConversionStatus.PENDING:
                stats['pending'] += 1
            elif task.status == ConversionStatus.PROCESSING:
                stats['processing'] += 1
            elif task.status == ConversionStatus.SUCCESS:
                stats['success'] += 1
            elif task.status == ConversionStatus.FAILED:
                stats['failed'] += 1
            elif task.status == ConversionStatus.SKIPPED:
                stats['skipped'] += 1

        return stats

    def clear(self):
        """큐 초기화"""
        self.tasks.clear()
        self.current_index = 0

    def _is_supported_file(self, file_path: str) -> bool:
        """지원되는 파일 형식인지 확인"""
        ext = Path(file_path).suffix.lower()
        return ext in self.SUPPORTED_EXTENSIONS

    def _output_exists(self, source_file: str, target_format: str, output_dir: str) -> bool:
        """출력 파일이 이미 존재하는지 확인"""
        source_path = Path(source_file)
        file_name = source_path.stem
        ext = target_format.lower()
        output_path = Path(output_dir) / f"{file_name}.{ext}"

        return output_path.exists()

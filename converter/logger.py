"""
CSV 로깅 모듈
변환 작업의 성공/실패/스킵 상태를 CSV로 기록합니다.
"""
import csv
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict


class ConversionLogger:
    """변환 로그 관리 클래스"""

    def __init__(self, log_dir: str = "logs"):
        """
        Args:
            log_dir: 로그 파일을 저장할 디렉토리
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = self.log_dir / f"conversion_log_{timestamp}.csv"

        # CSV 헤더 작성
        self._init_csv()

    def _init_csv(self):
        """CSV 파일 초기화 및 헤더 작성"""
        with open(self.log_file, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerow([
                'Timestamp',
                'Source File',
                'Target Format',
                'Output File',
                'Status',
                'Error Message'
            ])

    def log_conversion(self,
                      source_file: str,
                      target_format: str,
                      output_file: str,
                      status: str,
                      error_msg: str = ""):
        """
        변환 결과 로깅

        Args:
            source_file: 원본 파일 경로
            target_format: 변환 대상 형식 (PDF, HTML, XLS, XLSX)
            output_file: 출력 파일 경로
            status: 상태 (SUCCESS, FAILED, SKIPPED)
            error_msg: 에러 메시지 (선택)
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with open(self.log_file, 'a', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerow([
                timestamp,
                source_file,
                target_format,
                output_file,
                status,
                error_msg
            ])

    def get_failed_files(self) -> List[Dict[str, str]]:
        """
        실패한 파일 목록 반환

        Returns:
            실패한 파일 정보 리스트 [{'source': ..., 'format': ...}, ...]
        """
        failed = []

        if not self.log_file.exists():
            return failed

        with open(self.log_file, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['Status'] == 'FAILED':
                    failed.append({
                        'source': row['Source File'],
                        'format': row['Target Format']
                    })

        return failed

    def get_log_summary(self) -> Dict[str, int]:
        """
        로그 요약 통계 반환

        Returns:
            {'SUCCESS': count, 'FAILED': count, 'SKIPPED': count}
        """
        summary = {'SUCCESS': 0, 'FAILED': 0, 'SKIPPED': 0}

        if not self.log_file.exists():
            return summary

        with open(self.log_file, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                status = row['Status']
                if status in summary:
                    summary[status] += 1

        return summary

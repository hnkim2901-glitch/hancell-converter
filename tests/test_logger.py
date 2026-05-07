"""
ConversionLogger 테스트
CSV 로깅 기능을 테스트
"""
import pytest
import csv
from pathlib import Path
from converter.logger import ConversionLogger


class TestConversionLogger:
    """ConversionLogger 테스트"""

    def test_create_logger(self, log_dir):
        """로거 생성 테스트"""
        logger = ConversionLogger(log_dir)

        assert logger.log_dir == Path(log_dir)
        assert logger.log_file.exists()
        assert logger.log_file.suffix == '.csv'

    def test_csv_header(self, log_dir):
        """CSV 헤더 테스트"""
        logger = ConversionLogger(log_dir)

        with open(logger.log_file, 'r', encoding='utf-8-sig') as f:
            reader = csv.reader(f)
            header = next(reader)

        expected = [
            'Timestamp',
            'Source File',
            'Target Format',
            'Output File',
            'Status',
            'Error Message'
        ]

        assert header == expected

    def test_log_conversion_success(self, log_dir):
        """성공 로그 테스트"""
        logger = ConversionLogger(log_dir)

        logger.log_conversion(
            source_file="/path/to/test.cell",
            target_format="PDF",
            output_file="/path/to/test.pdf",
            status="SUCCESS"
        )

        with open(logger.log_file, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        assert len(rows) == 1
        assert rows[0]['Source File'] == "/path/to/test.cell"
        assert rows[0]['Target Format'] == "PDF"
        assert rows[0]['Output File'] == "/path/to/test.pdf"
        assert rows[0]['Status'] == "SUCCESS"
        assert rows[0]['Error Message'] == ""

    def test_log_conversion_failed(self, log_dir):
        """실패 로그 테스트"""
        logger = ConversionLogger(log_dir)

        logger.log_conversion(
            source_file="/path/to/test.cell",
            target_format="PDF",
            output_file="/path/to/test.pdf",
            status="FAILED",
            error_msg="팝업 발견"
        )

        with open(logger.log_file, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        assert len(rows) == 1
        assert rows[0]['Status'] == "FAILED"
        assert rows[0]['Error Message'] == "팝업 발견"

    def test_log_multiple_conversions(self, log_dir):
        """여러 변환 로그 테스트"""
        logger = ConversionLogger(log_dir)

        conversions = [
            ("test1.cell", "PDF", "test1.pdf", "SUCCESS", ""),
            ("test2.cell", "HTML", "test2.html", "FAILED", "오류"),
            ("test3.cell", "XLSX", "test3.xlsx", "SKIPPED", ""),
        ]

        for conv in conversions:
            logger.log_conversion(*conv)

        with open(logger.log_file, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        assert len(rows) == 3

    def test_get_failed_files(self, log_dir):
        """실패한 파일 목록 테스트"""
        logger = ConversionLogger(log_dir)

        # 다양한 상태로 로그 추가
        logger.log_conversion("test1.cell", "PDF", "test1.pdf", "SUCCESS")
        logger.log_conversion("test2.cell", "PDF", "test2.pdf", "FAILED", "Error 1")
        logger.log_conversion("test3.cell", "HTML", "test3.html", "FAILED", "Error 2")
        logger.log_conversion("test4.cell", "XLSX", "test4.xlsx", "SKIPPED")

        failed = logger.get_failed_files()

        assert len(failed) == 2
        assert failed[0]['source'] == "test2.cell"
        assert failed[0]['format'] == "PDF"
        assert failed[1]['source'] == "test3.cell"
        assert failed[1]['format'] == "HTML"

    def test_get_log_summary(self, log_dir):
        """로그 요약 통계 테스트"""
        logger = ConversionLogger(log_dir)

        # 다양한 상태로 로그 추가
        logger.log_conversion("test1.cell", "PDF", "test1.pdf", "SUCCESS")
        logger.log_conversion("test2.cell", "PDF", "test2.pdf", "SUCCESS")
        logger.log_conversion("test3.cell", "HTML", "test3.html", "FAILED", "Error")
        logger.log_conversion("test4.cell", "XLSX", "test4.xlsx", "SKIPPED")

        summary = logger.get_log_summary()

        assert summary['SUCCESS'] == 2
        assert summary['FAILED'] == 1
        assert summary['SKIPPED'] == 1

    def test_get_log_summary_empty(self, log_dir):
        """빈 로그 요약 테스트"""
        logger = ConversionLogger(log_dir)

        summary = logger.get_log_summary()

        assert summary['SUCCESS'] == 0
        assert summary['FAILED'] == 0
        assert summary['SKIPPED'] == 0

    def test_timestamp_format(self, log_dir):
        """타임스탬프 형식 테스트"""
        logger = ConversionLogger(log_dir)

        logger.log_conversion("test.cell", "PDF", "test.pdf", "SUCCESS")

        with open(logger.log_file, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            row = next(reader)

        timestamp = row['Timestamp']
        # 형식: YYYY-MM-DD HH:MM:SS
        assert len(timestamp) == 19
        assert timestamp[4] == '-'
        assert timestamp[7] == '-'
        assert timestamp[10] == ' '
        assert timestamp[13] == ':'
        assert timestamp[16] == ':'

    def test_utf8_encoding(self, log_dir):
        """UTF-8 인코딩 테스트 (한글)"""
        logger = ConversionLogger(log_dir)

        logger.log_conversion(
            source_file="테스트.cell",
            target_format="PDF",
            output_file="테스트.pdf",
            status="FAILED",
            error_msg="한글 에러 메시지"
        )

        with open(logger.log_file, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            row = next(reader)

        assert row['Source File'] == "테스트.cell"
        assert row['Error Message'] == "한글 에러 메시지"

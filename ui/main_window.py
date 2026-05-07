"""
메인 윈도우 UI
PySide6 기반 드래그앤드롭 UI
"""
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QCheckBox, QLabel, QTableWidget,
    QTableWidgetItem, QFileDialog, QLineEdit,
    QGroupBox, QSpinBox, QProgressBar, QMessageBox,
    QHeaderView
)
from PySide6.QtCore import Qt, QThread, Signal, QMimeData
from PySide6.QtGui import QDragEnterEvent, QDropEvent
from pathlib import Path
from typing import List

from converter.file_queue import FileQueue, ConversionStatus
from converter.logger import ConversionLogger
from converter.hancell_worker import HancellWorker, HancellWorkerThread
from utils.process import ProcessManager


class DropZone(QWidget):
    """드래그앤드롭 영역"""

    files_dropped = Signal(list)  # 드롭된 파일/폴더 경로 리스트

    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        self.setMinimumHeight(150)
        self.setStyleSheet("""
            DropZone {
                border: 2px dashed #aaa;
                border-radius: 8px;
                background-color: #f5f5f5;
            }
            DropZone:hover {
                background-color: #e8e8e8;
            }
        """)

        layout = QVBoxLayout()
        label = QLabel("파일 또는 폴더를 여기에 드래그하세요\n(.cell, .nxl, .xls, .xlsx)")
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("color: #666; font-size: 14px;")
        layout.addWidget(label)
        self.setLayout(layout)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        paths = []
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if path:
                paths.append(path)

        if paths:
            self.files_dropped.emit(paths)


class WorkerThread(QThread):
    """변환 작업 스레드"""

    progress = Signal(str)
    finished = Signal()
    task_updated = Signal(int, str)  # row, status

    def __init__(self, worker: HancellWorker, queue: FileQueue):
        super().__init__()
        self.worker = worker
        self.queue = queue
        self.is_running = True

    def run(self):
        """스레드 실행"""
        task_index = 0

        while self.is_running:
            task = self.queue.get_next_task()

            if not task:
                break

            self.queue.mark_task_status(task, ConversionStatus.PROCESSING)
            self.task_updated.emit(task_index, ConversionStatus.PROCESSING.value)

            def progress_callback(msg):
                self.progress.emit(msg)

            success = self.worker.convert_task(task, progress_callback)

            if success:
                self.queue.mark_task_status(task, ConversionStatus.SUCCESS)
                self.task_updated.emit(task_index, ConversionStatus.SUCCESS.value)
            else:
                self.queue.mark_task_status(task, ConversionStatus.FAILED, "변환 실패")
                self.task_updated.emit(task_index, ConversionStatus.FAILED.value)

            task_index += 1

        self.finished.emit()

    def stop(self):
        """스레드 중지"""
        self.is_running = False


class MainWindow(QMainWindow):
    """메인 윈도우"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("한셀 파일 일괄 변환기")
        self.setGeometry(100, 100, 1000, 700)

        # 모델 초기화
        self.queue = FileQueue()
        self.logger = ConversionLogger()
        self.process_manager = ProcessManager()
        self.worker = None
        self.worker_thread = None

        # UI 구성
        self.init_ui()

    def init_ui(self):
        """UI 초기화"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        # 1. 드롭 영역
        self.drop_zone = DropZone()
        self.drop_zone.files_dropped.connect(self.on_files_dropped)
        main_layout.addWidget(self.drop_zone)

        # 2. 설정 영역
        settings_group = QGroupBox("변환 설정")
        settings_layout = QVBoxLayout()

        # 2-1. 변환 형식 선택
        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel("변환 형식:"))

        self.check_pdf = QCheckBox("PDF")
        self.check_pdf.setChecked(True)
        self.check_html = QCheckBox("HTML")
        self.check_xls = QCheckBox("XLS")
        self.check_xlsx = QCheckBox("XLSX")

        format_layout.addWidget(self.check_pdf)
        format_layout.addWidget(self.check_html)
        format_layout.addWidget(self.check_xls)
        format_layout.addWidget(self.check_xlsx)
        format_layout.addStretch()

        settings_layout.addLayout(format_layout)

        # 2-2. 출력 폴더 선택
        output_layout = QHBoxLayout()
        output_layout.addWidget(QLabel("출력 폴더:"))

        self.output_path_edit = QLineEdit()
        self.output_path_edit.setText(str(Path.cwd() / "output"))
        output_layout.addWidget(self.output_path_edit)

        self.btn_browse_output = QPushButton("찾아보기")
        self.btn_browse_output.clicked.connect(self.browse_output_folder)
        output_layout.addWidget(self.btn_browse_output)

        settings_layout.addLayout(output_layout)

        # 2-3. 옵션
        options_layout = QHBoxLayout()

        self.check_recursive = QCheckBox("하위 폴더 포함")
        self.check_recursive.setChecked(True)
        options_layout.addWidget(self.check_recursive)

        self.check_skip_existing = QCheckBox("기존 파일 스킵")
        self.check_skip_existing.setChecked(True)
        options_layout.addWidget(self.check_skip_existing)

        options_layout.addWidget(QLabel("프로세스 재시작 간격:"))
        self.spin_restart = QSpinBox()
        self.spin_restart.setRange(0, 500)
        self.spin_restart.setValue(50)
        self.spin_restart.setSuffix("개")
        self.spin_restart.setSpecialValueText("사용 안함")
        options_layout.addWidget(self.spin_restart)

        options_layout.addStretch()
        settings_layout.addLayout(options_layout)

        settings_group.setLayout(settings_layout)
        main_layout.addWidget(settings_group)

        # 3. 작업 테이블
        table_group = QGroupBox("변환 작업 목록")
        table_layout = QVBoxLayout()

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "파일명", "경로", "변환 형식", "상태", "오류 메시지"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)

        table_layout.addWidget(self.table)
        table_group.setLayout(table_layout)
        main_layout.addWidget(table_group)

        # 4. 진행률 표시
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)

        self.status_label = QLabel("")
        main_layout.addWidget(self.status_label)

        # 5. 버튼 영역
        button_layout = QHBoxLayout()

        self.btn_start = QPushButton("변환 시작")
        self.btn_start.clicked.connect(self.start_conversion)
        button_layout.addWidget(self.btn_start)

        self.btn_retry_failed = QPushButton("실패한 파일만 재시도")
        self.btn_retry_failed.clicked.connect(self.retry_failed)
        self.btn_retry_failed.setEnabled(False)
        button_layout.addWidget(self.btn_retry_failed)

        self.btn_clear = QPushButton("목록 초기화")
        self.btn_clear.clicked.connect(self.clear_queue)
        button_layout.addWidget(self.btn_clear)

        self.btn_stop = QPushButton("중지")
        self.btn_stop.clicked.connect(self.stop_conversion)
        self.btn_stop.setEnabled(False)
        button_layout.addWidget(self.btn_stop)

        button_layout.addStretch()
        main_layout.addLayout(button_layout)

    def on_files_dropped(self, paths: List[str]):
        """드롭된 파일/폴더 처리"""
        target_formats = self.get_selected_formats()
        if not target_formats:
            QMessageBox.warning(self, "경고", "최소 하나의 변환 형식을 선택하세요.")
            return

        output_dir = self.output_path_edit.text()
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        recursive = self.check_recursive.isChecked()
        skip_existing = self.check_skip_existing.isChecked()

        for path in paths:
            path_obj = Path(path)

            if path_obj.is_file():
                self.queue.add_files([path], target_formats, output_dir, skip_existing)
            elif path_obj.is_dir():
                self.queue.add_folder(path, target_formats, output_dir, recursive, skip_existing)

        self.update_table()
        self.update_status()

    def get_selected_formats(self) -> List[str]:
        """선택된 변환 형식 반환"""
        formats = []
        if self.check_pdf.isChecked():
            formats.append('PDF')
        if self.check_html.isChecked():
            formats.append('HTML')
        if self.check_xls.isChecked():
            formats.append('XLS')
        if self.check_xlsx.isChecked():
            formats.append('XLSX')
        return formats

    def update_table(self):
        """테이블 업데이트"""
        self.table.setRowCount(len(self.queue.tasks))

        for row, task in enumerate(self.queue.tasks):
            # 파일명
            file_name = Path(task.source_file).name
            self.table.setItem(row, 0, QTableWidgetItem(file_name))

            # 경로
            self.table.setItem(row, 1, QTableWidgetItem(task.source_file))

            # 변환 형식
            formats = ", ".join(task.target_formats) if task.target_formats else "없음"
            self.table.setItem(row, 2, QTableWidgetItem(formats))

            # 상태
            self.table.setItem(row, 3, QTableWidgetItem(task.status.value))

            # 오류 메시지
            self.table.setItem(row, 4, QTableWidgetItem(task.error_message))

    def update_status(self):
        """상태 레이블 업데이트"""
        stats = self.queue.get_statistics()
        self.status_label.setText(
            f"전체: {stats['total']} | "
            f"대기: {stats['pending']} | "
            f"성공: {stats['success']} | "
            f"실패: {stats['failed']} | "
            f"스킵: {stats['skipped']}"
        )

    def browse_output_folder(self):
        """출력 폴더 선택 대화상자"""
        folder = QFileDialog.getExistingDirectory(self, "출력 폴더 선택")
        if folder:
            self.output_path_edit.setText(folder)

    def start_conversion(self):
        """변환 시작"""
        if not self.queue.tasks:
            QMessageBox.warning(self, "경고", "변환할 파일이 없습니다.")
            return

        # UI 상태 변경
        self.btn_start.setEnabled(False)
        self.btn_stop.setEnabled(True)
        self.btn_clear.setEnabled(False)
        self.progress_bar.setVisible(True)

        # 워커 생성
        restart_interval = self.spin_restart.value()
        self.worker = HancellWorker(self.logger, self.process_manager, restart_interval)

        # 워커 스레드 생성 및 시작
        self.worker_thread = WorkerThread(self.worker, self.queue)
        self.worker_thread.progress.connect(self.on_progress)
        self.worker_thread.task_updated.connect(self.on_task_updated)
        self.worker_thread.finished.connect(self.on_conversion_finished)
        self.worker_thread.start()

    def stop_conversion(self):
        """변환 중지"""
        if self.worker_thread:
            self.worker_thread.stop()
            self.worker_thread.wait()

        self.on_conversion_finished()

    def on_progress(self, message: str):
        """진행 상황 업데이트"""
        self.status_label.setText(message)

    def on_task_updated(self, row: int, status: str):
        """작업 상태 업데이트"""
        if row < self.table.rowCount():
            self.table.setItem(row, 3, QTableWidgetItem(status))
        self.update_status()

    def on_conversion_finished(self):
        """변환 완료"""
        self.btn_start.setEnabled(True)
        self.btn_stop.setEnabled(False)
        self.btn_clear.setEnabled(True)
        self.progress_bar.setVisible(False)

        # 실패한 작업이 있으면 재시도 버튼 활성화
        failed_tasks = self.queue.get_failed_tasks()
        self.btn_retry_failed.setEnabled(len(failed_tasks) > 0)

        # 최종 통계 표시
        self.update_status()
        stats = self.queue.get_statistics()

        QMessageBox.information(
            self,
            "변환 완료",
            f"변환이 완료되었습니다.\n\n"
            f"성공: {stats['success']}\n"
            f"실패: {stats['failed']}\n"
            f"스킵: {stats['skipped']}"
        )

    def retry_failed(self):
        """실패한 파일만 재시도"""
        self.queue.reset_failed_tasks()
        self.update_table()
        self.start_conversion()

    def clear_queue(self):
        """큐 초기화"""
        self.queue.clear()
        self.table.setRowCount(0)
        self.update_status()
        self.btn_retry_failed.setEnabled(False)

    def closeEvent(self, event):
        """윈도우 종료 시"""
        # 프로세스 정리
        self.process_manager.stop_hancell()
        event.accept()

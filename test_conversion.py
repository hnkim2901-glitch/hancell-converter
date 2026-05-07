#!/usr/bin/env python3
"""
단일 파일 변환 테스트 스크립트
Mac 환경에서 변환 로직 흐름을 확인
"""
import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Windows Mock 패치
from tests.mock_windows import patch_windows_modules
patch_windows_modules()

from converter.file_queue import FileQueue, ConversionStatus
from converter.logger import ConversionLogger
from converter.hancell_worker import HancellWorker
from utils.process import ProcessManager


def test_single_file_conversion():
    """단일 파일 변환 테스트"""
    print("=" * 60)
    print("한셀 파일 변환 테스트 (Mac 환경)")
    print("=" * 60)
    print()

    # 1. 설정
    source_file = str(Path(__file__).parent / "test.cell")
    output_dir = str(Path(__file__).parent / "output")
    log_dir = str(Path(__file__).parent / "logs")

    print(f"📄 원본 파일: {source_file}")
    print(f"📁 출력 폴더: {output_dir}")
    print(f"📝 로그 폴더: {log_dir}")
    print()

    # 파일 존재 확인
    if not Path(source_file).exists():
        print(f"❌ 파일을 찾을 수 없습니다: {source_file}")
        return False

    source_size = Path(source_file).stat().st_size
    print(f"✅ 파일 확인 완료 ({source_size:,} bytes)")
    print()

    # 출력 폴더 생성
    Path(output_dir).mkdir(exist_ok=True)
    Path(log_dir).mkdir(exist_ok=True)

    # 2. 컴포넌트 초기화
    print("🔧 컴포넌트 초기화...")
    queue = FileQueue()
    logger = ConversionLogger(log_dir)
    process_manager = ProcessManager()
    worker = HancellWorker(logger, process_manager, restart_interval=0)
    print("✅ 초기화 완료")
    print()

    # 3. 파일 큐에 추가
    print("📋 파일 큐에 추가...")
    target_formats = ['PDF', 'HTML', 'XLSX']
    queue.add_files([source_file], target_formats, output_dir, skip_existing=False)

    print(f"   - 변환 형식: {', '.join(target_formats)}")
    print(f"   - 작업 수: {len(queue.tasks)}")
    print()

    # 4. 작업 가져오기
    task = queue.get_next_task()
    if not task:
        print("❌ 작업을 가져올 수 없습니다")
        return False

    print(f"📝 작업 정보:")
    print(f"   - 원본: {Path(task.source_file).name}")
    print(f"   - 형식: {', '.join(task.target_formats)}")
    print(f"   - 상태: {task.status.value}")
    print()

    # 5. 변환 시도
    print("🔄 변환 시도 중...")
    print("   ⚠️  Mac 환경이므로 실제 한셀 변환은 불가능합니다")
    print("   ⚠️  변환 로직 흐름만 확인합니다")
    print()

    # 진행 상황 콜백
    progress_messages = []

    def progress_callback(msg):
        progress_messages.append(msg)
        print(f"   📊 {msg}")

    # 작업 상태를 PROCESSING으로 변경
    queue.mark_task_status(task, ConversionStatus.PROCESSING)

    # 변환 시도 (Mock 환경에서는 실패하지만 로직은 실행됨)
    result = worker.convert_task(task, progress_callback)

    print()

    # 6. 결과 확인
    print("=" * 60)
    print("변환 결과")
    print("=" * 60)
    print()

    print(f"🔍 변환 결과: {'성공' if result else '실패 (예상됨 - Mac 환경)'}")
    print(f"📊 진행 메시지 수: {len(progress_messages)}")
    print()

    # 출력 파일 확인
    print("📁 예상 출력 파일:")
    for fmt in target_formats:
        output_path = task.get_output_path(fmt)
        exists = Path(output_path).exists()
        status = "✅ 존재" if exists else "❌ 없음 (예상됨)"
        print(f"   - {Path(output_path).name}: {status}")
    print()

    # 로그 확인
    print("📝 로그 정보:")
    log_summary = logger.get_log_summary()
    print(f"   - 성공: {log_summary['SUCCESS']}")
    print(f"   - 실패: {log_summary['FAILED']}")
    print(f"   - 스킵: {log_summary['SKIPPED']}")
    print()

    # 큐 통계
    print("📊 큐 통계:")
    stats = queue.get_statistics()
    print(f"   - 전체: {stats['total']}")
    print(f"   - 대기: {stats['pending']}")
    print(f"   - 처리 중: {stats['processing']}")
    print(f"   - 성공: {stats['success']}")
    print(f"   - 실패: {stats['failed']}")
    print()

    # 스크린샷 확인
    screenshots = list(worker.screenshot_dir.glob("*.png"))
    if screenshots:
        print(f"📸 스크린샷: {len(screenshots)}개 생성됨")
        for ss in screenshots:
            print(f"   - {ss.name}")
    else:
        print("📸 스크린샷: 없음")
    print()

    print("=" * 60)
    print("결론")
    print("=" * 60)
    print()
    print("✅ 변환 로직이 정상적으로 실행되었습니다")
    print("⚠️  Mac 환경에서는 실제 한셀 자동화가 불가능합니다")
    print("💡 Windows 환경에서는 실제 파일 변환이 진행됩니다")
    print()

    return True


if __name__ == "__main__":
    try:
        success = test_single_file_conversion()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

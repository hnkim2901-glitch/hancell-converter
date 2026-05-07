"""
Windows API Mock 모듈
Mac에서 테스트할 수 있도록 Windows 의존성을 Mock으로 대체
"""
from unittest.mock import Mock, MagicMock


class MockProcess:
    """psutil.Process Mock"""
    def __init__(self, name='HCell.exe', exe=r'C:\Program Files\Hancom\Office 2022\HCell.exe'):
        self.info = {
            'name': name,
            'exe': exe
        }

    def terminate(self):
        pass

    def kill(self):
        pass

    def wait(self, timeout=5):
        pass


class MockPsutil:
    """psutil 모듈 Mock"""
    NoSuchProcess = Exception
    AccessDenied = Exception

    @staticmethod
    def process_iter(attrs=None):
        """실행 중인 프로세스 목록 반환 (Mock)"""
        return [
            MockProcess('HCell.exe', r'C:\Program Files\Hancom\Office 2022\HCell.exe'),
            MockProcess('chrome.exe', r'C:\Program Files\Google\Chrome\chrome.exe'),
        ]


class MockPopen:
    """subprocess.Popen Mock"""
    def __init__(self, *args, **kwargs):
        self.returncode = 0
        self.stdout = None
        self.stderr = None

    def terminate(self):
        pass

    def kill(self):
        pass

    def wait(self, timeout=None):
        return 0


class MockSubprocess:
    """subprocess 모듈 Mock"""
    Popen = MockPopen
    PIPE = -1


class MockDesktop:
    """pywinauto Desktop Mock"""
    def __init__(self, backend='uia'):
        self.backend = backend

    def windows(self):
        """윈도우 목록 반환 (Mock)"""
        return [
            MockWindow('한셀 - test.cell'),
            MockWindow('Chrome'),
        ]


class MockWindow:
    """pywinauto Window Mock"""
    def __init__(self, title='한셀'):
        self._title = title

    def window_text(self):
        return self._title


class MockApplication:
    """pywinauto Application Mock"""
    def __init__(self, backend='uia'):
        self.backend = backend

    def connect(self, **kwargs):
        return self

    def start(self, *args):
        return self


class MockPywinauto:
    """pywinauto 모듈 Mock"""
    Desktop = MockDesktop
    Application = MockApplication
    TimeoutError = Exception

    class keyboard:
        @staticmethod
        def send_keys(keys):
            """키 입력 Mock"""
            pass


class MockImageGrab:
    """PIL.ImageGrab Mock"""
    class Image:
        def __init__(self):
            pass

        def save(self, path):
            """이미지 저장 Mock"""
            # 실제로 빈 파일 생성
            with open(path, 'wb') as f:
                f.write(b'fake image')

    @staticmethod
    def grab():
        """화면 캡처 Mock"""
        return MockImageGrab.Image()


class MockWin32Com:
    """win32com 모듈 Mock"""
    class client:
        @staticmethod
        def Dispatch(app_name):
            """COM 객체 생성 Mock"""
            return MockWin32Com.MockCOMObject()

    class MockCOMObject:
        """COM 객체 Mock"""
        def __init__(self):
            self.Visible = False
            self.Workbooks = self

        def Open(self, filename):
            return self

        def SaveAs(self, filename, FileFormat=None):
            pass

        def Close(self):
            pass


def patch_windows_modules():
    """
    Windows 모듈들을 Mock으로 패치
    테스트 시작 전에 호출
    """
    import sys

    # psutil Mock
    sys.modules['psutil'] = MockPsutil

    # subprocess Mock (일부만 Mock)
    # subprocess는 표준 라이브러리라서 완전히 대체하면 문제가 생길 수 있음
    # 대신 테스트에서 직접 Mock 사용

    # pywinauto Mock
    sys.modules['pywinauto'] = MockPywinauto
    sys.modules['pywinauto.keyboard'] = MockPywinauto.keyboard
    sys.modules['pywinauto.timings'] = type('Module', (), {'TimeoutError': Exception})()

    # PIL.ImageGrab Mock
    if 'PIL' not in sys.modules:
        sys.modules['PIL'] = type('Module', (), {})()
    sys.modules['PIL'].ImageGrab = MockImageGrab

    # win32com Mock
    sys.modules['win32com'] = MockWin32Com
    sys.modules['win32com.client'] = MockWin32Com.client

    print("✅ Windows 모듈 Mock 패치 완료")


def unpatch_windows_modules():
    """Mock 패치 제거"""
    import sys

    modules_to_remove = [
        'psutil',
        'pywinauto',
        'pywinauto.keyboard',
        'pywinauto.timings',
        'win32com',
        'win32com.client',
    ]

    for module in modules_to_remove:
        if module in sys.modules:
            del sys.modules[module]

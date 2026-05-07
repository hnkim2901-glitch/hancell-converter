# 기여 가이드

한셀 파일 일괄 변환기 프로젝트에 기여해주셔서 감사합니다!

## 개발 환경 설정

### 필수 요구사항

- Windows 10/11
- Python 3.8 이상
- 한컴오피스 한셀 (테스트용)
- Git

### 설정 단계

1. 저장소 클론
```bash
git clone <repository-url>
cd hancell-converter
```

2. 가상 환경 생성 및 활성화
```bash
python -m venv venv
venv\Scripts\activate
```

3. 개발 의존성 설치
```bash
pip install -r requirements.txt
pip install pytest black flake8  # 개발 도구
```

4. 애플리케이션 실행
```bash
python app.py
```

## 코드 스타일

### Python 스타일 가이드

- PEP 8 준수
- Black 포맷터 사용 (라인 길이: 88)
- 타입 힌트 권장

```bash
# 코드 포맷팅
black .

# 린팅
flake8 .
```

### 네이밍 규칙

- 클래스: `PascalCase` (예: `HancellWorker`)
- 함수/메서드: `snake_case` (예: `convert_file`)
- 상수: `UPPER_SNAKE_CASE` (예: `DEFAULT_OUTPUT_DIR`)
- 비공개: `_leading_underscore` (예: `_internal_method`)

### 주석 및 문서화

- 모든 모듈, 클래스, 함수에 docstring 작성
- Google 스타일 docstring 사용

```python
def convert_file(source: str, target_format: str) -> bool:
    """
    파일을 지정된 형식으로 변환합니다.

    Args:
        source: 원본 파일 경로
        target_format: 변환할 형식 (PDF, HTML, XLS, XLSX)

    Returns:
        변환 성공 여부

    Raises:
        FileNotFoundError: 원본 파일이 없을 때
    """
    pass
```

## 브랜치 전략

### 브랜치 이름 규칙

- `feature/기능명`: 새 기능 개발
- `bugfix/버그명`: 버그 수정
- `hotfix/긴급수정`: 긴급 수정
- `docs/문서명`: 문서 작업

예시:
```bash
git checkout -b feature/add-dark-mode
git checkout -b bugfix/fix-popup-detection
```

## 커밋 메시지

### 형식

```
타입: 간단한 설명

상세 설명 (선택)

이슈 번호 (선택)
```

### 타입

- `feat`: 새 기능
- `fix`: 버그 수정
- `docs`: 문서 변경
- `style`: 코드 포맷팅 (기능 변경 없음)
- `refactor`: 리팩토링
- `test`: 테스트 추가/수정
- `chore`: 빌드/설정 변경

### 예시

```
feat: win32com 기반 변환 모듈 추가

pywinauto 외에 win32com을 사용한 변환 방식을 추가했습니다.
성능이 약 2배 향상되었습니다.

Closes #15
```

## Pull Request

### PR 생성 전 체크리스트

- [ ] 코드가 PEP 8을 준수하는가?
- [ ] Black 포맷터를 실행했는가?
- [ ] 모든 새 함수/클래스에 docstring이 있는가?
- [ ] 테스트가 통과하는가?
- [ ] CHANGELOG.md를 업데이트했는가?

### PR 템플릿

```markdown
## 변경 사항
- 주요 변경 사항 요약

## 관련 이슈
- Closes #이슈번호

## 테스트 방법
1. 단계 1
2. 단계 2

## 스크린샷 (UI 변경 시)
[스크린샷 첨부]

## 체크리스트
- [ ] 코드 스타일 확인
- [ ] 테스트 통과
- [ ] 문서 업데이트
```

## 테스트

### 단위 테스트

```bash
pytest tests/
```

### 수동 테스트

1. 다양한 한셀 파일 형식 (.cell, .nxl, .xls, .xlsx) 테스트
2. 대량 파일 (100개 이상) 테스트
3. 네트워크 드라이브 파일 테스트
4. 읽기 전용 파일 테스트
5. 손상된 파일 테스트

## 이슈 제출

### 버그 리포트

```markdown
**버그 설명**
명확하고 간결한 버그 설명

**재현 방법**
1. '...'로 이동
2. '...'를 클릭
3. '...'까지 스크롤
4. 오류 발생

**예상 동작**
예상했던 동작 설명

**실제 동작**
실제로 발생한 동작

**스크린샷**
가능하면 스크린샷 첨부

**환경**
- OS: Windows 10
- Python 버전: 3.11
- 한셀 버전: 2022
- 앱 버전: v1.0.0

**추가 정보**
기타 추가 정보
```

### 기능 제안

```markdown
**제안하는 기능**
기능에 대한 명확한 설명

**문제점**
현재 어떤 문제가 있나요?

**제안하는 해결책**
어떻게 해결할 수 있을까요?

**대안**
고려한 다른 방법들

**추가 정보**
기타 추가 정보
```

## 주요 개선 영역

### 우선순위: 높음

1. **win32com 완전 구현**: pywinauto 대신 COM 인터페이스 사용
2. **성능 최적화**: 변환 속도 개선
3. **오류 처리 강화**: 더 많은 팝업 케이스 처리

### 우선순위: 중간

1. **UI/UX 개선**: 다크 모드, 애니메이션
2. **통계 기능**: 대시보드, 그래프
3. **설정 저장**: 사용자 설정 프로필

### 우선순위: 낮음

1. **다국어 지원**: 영어, 일본어
2. **클라우드 연동**: OneDrive, Google Drive
3. **CLI 모드**: 명령줄 인터페이스

## 질문이나 도움이 필요하신가요?

- 이슈 트래커에 질문을 올려주세요
- 디스커션에 참여해주세요

감사합니다!

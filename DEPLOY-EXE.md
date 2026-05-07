# exe 직접 배포 가이드

가장 간단한 배포 방법입니다. 설치 없이 바로 실행 가능한 exe 파일을 생성합니다.

## 📋 목차
1. [Windows에서 빌드](#windows에서-빌드)
2. [테스트](#테스트)
3. [배포](#배포)
4. [사용자 가이드](#사용자-가이드)

---

## 1️⃣ Windows에서 빌드

### 준비물
- ✅ Windows 10/11 PC
- ✅ Python 3.8 이상
- ✅ hancell-converter-project 폴더

### 빌드 과정

**1. 프로젝트 폴더로 이동**
```batch
cd hancell-converter-project
```

**2. 설치 스크립트 실행**
```batch
setup.bat
```

이 과정에서:
- Python 버전 확인
- 가상 환경 생성 (venv/)
- 필요한 라이브러리 설치
- PyInstaller 설치

**3. exe 빌드**
```batch
build.bat
```

**빌드 과정 (약 2-5분):**
```
[1/4] PyInstaller 확인...
[2/4] exe 파일 빌드 중...
  - 파일 수집 중...
  - Python 인터프리터 임베딩...
  - 의존성 번들링...
  - 압축 중...
[3/4] 빌드 완료!
[4/4] 결과: dist/한셀변환기.exe
```

**4. 결과 확인**
```batch
dir dist
```

결과:
```
dist/
└── 한셀변환기.exe  (약 50-100MB)
```

---

## 2️⃣ 테스트

### 빌드된 exe 테스트

**1. 실행 테스트**
```batch
cd dist
한셀변환기.exe
```

→ UI 윈도우가 뜨면 성공! ✅

**2. 기능 테스트**

**A. 단일 파일 변환**
```
1. test.cell 파일을 드래그앤드롭
2. PDF 체크
3. 출력 폴더 지정
4. "변환 시작" 클릭
5. output 폴더에 test.pdf 생성 확인
```

**B. 여러 형식 변환**
```
1. test.cell 드래그앤드롭
2. PDF, HTML, XLSX 모두 체크
3. 변환 시작
4. 3개 파일 모두 생성 확인
```

**C. 폴더 변환**
```
1. 한셀 파일이 여러 개 있는 폴더 드래그
2. "하위 폴더 포함" 체크
3. 변환 시작
4. 모든 파일 변환 확인
```

**3. 로그 확인**
```
logs/conversion_log_YYYYMMDD_HHMMSS.csv 파일 확인
- 성공/실패 내역이 기록되어 있어야 함
```

### 다른 PC에서 테스트

**중요!** 다른 PC에서도 테스트해보세요:

```
1. 한셀이 설치되지 않은 PC
   → "한셀을 찾을 수 없음" 메시지 확인

2. 한셀이 설치된 PC
   → 정상 동작 확인

3. Windows 10 PC
   → 호환성 확인

4. Windows 11 PC
   → 호환성 확인
```

---

## 3️⃣ 배포

### A. 파일 준비

**1. exe 파일 복사**
```batch
# 배포용 폴더 생성
mkdir hancell-converter-release
copy dist\한셀변환기.exe hancell-converter-release\
```

**2. 문서 추가 (선택)**
```batch
copy README.md hancell-converter-release\
copy QUICKSTART.md hancell-converter-release\
copy LICENSE hancell-converter-release\
```

**3. 사용자 가이드 추가**

`hancell-converter-release/사용법.txt` 파일 생성:
```
한셀 파일 일괄 변환기 v1.0.0

[시스템 요구사항]
- Windows 10 이상
- 한컴오피스 한셀 설치 필요

[사용 방법]
1. 한셀변환기.exe 더블클릭
2. 변환할 한셀 파일을 드래그앤드롭
3. 변환 형식 선택 (PDF, HTML, XLS, XLSX)
4. 출력 폴더 지정
5. "변환 시작" 클릭

[문의]
이메일: your@email.com
```

**4. 압축 (선택)**
```batch
# 7-Zip 또는 WinRAR 사용
hancell-converter-v1.0.0.zip
```

### B. 배포 방법

#### 방법 1: 이메일/메신저
```
1. hancell-converter-v1.0.0.zip 첨부
2. 사용법 간단히 설명
3. 전송
```

**이메일 예시:**
```
제목: 한셀 파일 변환 프로그램

안녕하세요,

한셀 파일을 PDF, HTML, XLSX로 일괄 변환하는 프로그램입니다.

[사용 방법]
1. 첨부 파일 압축 해제
2. 한셀변환기.exe 실행
3. 파일 드래그앤드롭

문의사항이 있으시면 연락주세요.
```

#### 방법 2: USB/네트워크 공유
```
1. USB에 복사
   └── hancell-converter-release/
       ├── 한셀변환기.exe
       └── 사용법.txt

2. 네트워크 공유 폴더에 업로드
   \\server\share\한셀변환기\

3. 사용자에게 경로 안내
```

#### 방법 3: 웹 다운로드
```
1. 웹 호스팅 준비 (예: Google Drive, Dropbox)

2. 업로드
   - Google Drive: 파일 업로드 → 링크 공유
   - Dropbox: Public 폴더에 업로드
   - 자체 서버: FTP로 업로드

3. 다운로드 페이지 생성
```

**다운로드 페이지 예시 (HTML):**
```html
<!DOCTYPE html>
<html>
<head>
    <title>한셀 파일 변환기 다운로드</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; }
        .download-btn {
            background: #4CAF50; color: white; padding: 15px 30px;
            text-decoration: none; border-radius: 5px; font-size: 18px;
        }
    </style>
</head>
<body>
    <h1>한셀 파일 일괄 변환기</h1>
    <p>한셀 파일을 PDF, HTML, XLSX로 간편하게 변환하세요.</p>

    <h2>주요 기능</h2>
    <ul>
        <li>드래그앤드롭으로 간편한 파일 추가</li>
        <li>PDF, HTML, XLS, XLSX 다중 형식 지원</li>
        <li>대량 파일 일괄 변환</li>
        <li>실패한 파일 재시도</li>
    </ul>

    <h2>시스템 요구사항</h2>
    <ul>
        <li>Windows 10 이상</li>
        <li>한컴오피스 한셀 설치 필요</li>
    </ul>

    <h2>다운로드</h2>
    <a href="hancell-converter-v1.0.0.zip" class="download-btn">
        다운로드 (v1.0.0, 50MB)
    </a>

    <h2>사용 방법</h2>
    <ol>
        <li>위 다운로드 버튼 클릭</li>
        <li>압축 해제</li>
        <li>한셀변환기.exe 실행</li>
        <li>파일 드래그앤드롭</li>
    </ol>

    <p>문의: your@email.com</p>
</body>
</html>
```

#### 방법 4: GitHub Releases (무료)
```
1. GitHub 저장소 생성
2. 코드 업로드
3. Releases → New release
4. Tag: v1.0.0
5. 한셀변환기.exe 업로드
6. Publish
```

다운로드 URL:
```
https://github.com/yourusername/hancell-converter/releases/download/v1.0.0/한셀변환기.exe
```

---

## 4️⃣ 사용자 가이드

### 배포 시 포함할 간단 가이드

**빠른 시작 가이드.txt:**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  한셀 파일 일괄 변환기 v1.0.0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📌 시작하기

1단계: 프로그램 실행
   한셀변환기.exe를 더블클릭

2단계: 파일 추가
   한셀 파일(.cell, .xlsx 등)을
   드래그앤드롭 영역에 끌어다 놓기

3단계: 변환 설정
   ☑ PDF     - PDF 문서로 변환
   ☑ HTML    - 웹 페이지로 변환
   ☑ XLS     - Excel 97-2003 형식
   ☑ XLSX    - Excel 최신 형식

4단계: 출력 폴더 선택
   "찾아보기" 버튼으로 저장 위치 지정

5단계: 변환 시작
   "변환 시작" 버튼 클릭

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💡 팁
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

• 폴더 전체 변환
  폴더를 드래그앤드롭하면 안의 모든 파일 변환

• 하위 폴더 포함
  "하위 폴더 포함" 체크 시 서브폴더까지 탐색

• 기존 파일 스킵
  이미 변환된 파일은 자동으로 건너뜀

• 실패 재시도
  실패한 파일만 다시 변환 가능

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
❓ 문제 해결
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Q. "한셀을 찾을 수 없습니다"
A. 한컴오피스 한셀을 먼저 설치하세요.

Q. 변환이 실패합니다
A. logs 폴더의 CSV 파일 확인
   screenshots 폴더에 오류 화면 저장됨

Q. 프로그램이 느려요
A. "프로세스 재시작 간격"을 50개로 설정

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📞 문의
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

이메일: your@email.com
버그 리포트: GitHub Issues
```

---

## 📊 배포 체크리스트

### 빌드 전
- [ ] 모든 테스트 통과 확인
- [ ] 버전 번호 확인 (app.py)
- [ ] CHANGELOG.md 업데이트

### 빌드
- [ ] build.bat 실행
- [ ] dist/한셀변환기.exe 생성 확인
- [ ] 파일 크기 확인 (50-100MB)

### 테스트
- [ ] 현재 PC에서 실행 확인
- [ ] 단일 파일 변환 테스트
- [ ] 여러 형식 변환 테스트
- [ ] 폴더 변환 테스트
- [ ] 다른 PC에서 테스트

### 배포 준비
- [ ] 사용자 가이드 작성
- [ ] README 포함
- [ ] 압축 파일 생성 (선택)
- [ ] 다운로드 페이지 준비 (선택)

### 배포
- [ ] 파일 업로드
- [ ] 다운로드 링크 테스트
- [ ] 사용자에게 안내

### 배포 후
- [ ] 사용자 피드백 수집
- [ ] 버그 리포트 확인
- [ ] FAQ 작성

---

## 🎯 배포 완료!

이제 사용자들이:
1. exe 파일 다운로드
2. 더블클릭으로 실행
3. 파일 드래그앤드롭
4. 즉시 변환!

간단하고 빠르게 배포 완료! 🎉

---

## 📝 다음 버전 업데이트 시

```batch
# 1. 코드 수정
# 2. 버전 업데이트
# 3. 다시 빌드
build.bat

# 4. 새 버전 배포
hancell-converter-v1.1.0.zip
```

사용자에게 새 버전 안내:
```
v1.1.0 업데이트
- 새로운 기능: win32com 지원
- 버그 수정: 팝업 감지 개선
- 성능 향상: 2배 빠른 변환

다운로드: [링크]
```

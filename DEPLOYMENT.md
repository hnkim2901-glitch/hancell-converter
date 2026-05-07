# 배포 가이드

한셀 파일 일괄 변환기를 배포하는 여러 가지 방법을 설명합니다.

## 📦 배포 방법 비교

| 방법 | 난이도 | 전문성 | 장점 | 단점 |
|------|--------|--------|------|------|
| **exe 파일** | ⭐ 쉬움 | 없음 | 즉시 실행, 간단 | 업데이트 수동 |
| **Installer** | ⭐⭐ 보통 | 중급 | 전문적, 제거 쉬움 | 설정 필요 |
| **Microsoft Store** | ⭐⭐⭐ 어려움 | 고급 | 자동 업데이트 | 심사 필요, 복잡 |
| **GitHub Releases** | ⭐ 쉬움 | 없음 | 버전 관리 | GitHub 계정 필요 |

---

## 1️⃣ exe 파일 직접 배포 (가장 간단) ✅

### Windows에서 빌드

```batch
cd hancell-converter-project
build.bat
```

**결과:**
```
dist/
└── 한셀변환기.exe  (약 50-100MB)
```

### 배포 방법

**A. 웹사이트에 업로드**
```
1. dist/한셀변환기.exe 파일을 웹 호스팅에 업로드
2. 다운로드 링크 제공
3. 사용자가 다운로드 후 바로 실행
```

**B. 이메일/메신저로 전달**
```
- exe 파일을 직접 전송
- 압축(zip) 후 전송도 가능
```

**C. USB/네트워크 공유**
```
- USB에 복사하여 배포
- 네트워크 공유 폴더에 업로드
```

### 장점
- ✅ 설치 불필요
- ✅ 즉시 실행
- ✅ 배포 즉시 가능

### 단점
- ❌ 업데이트 시 전체 파일 재배포
- ❌ 제거가 수동 (파일 삭제)
- ❌ 시작 메뉴 등록 안됨

---

## 2️⃣ Installer 생성 (추천) ⭐

전문적인 설치 프로그램을 만듭니다.

### A. Inno Setup 사용

**1. Inno Setup 다운로드**
```
https://jrsoftware.org/isdl.php
```

**2. 스크립트 사용**

프로젝트에 포함된 `installer.iss` 파일 사용:

```batch
# Windows에서
1. Inno Setup Compiler 실행
2. installer.iss 파일 열기
3. Build > Compile 클릭
4. installer_output/HancellConverter-Setup-v1.0.0.exe 생성됨
```

**3. 배포**

```
installer_output/HancellConverter-Setup-v1.0.0.exe를 배포
- 파일 크기: 약 50-100MB
- 사용자가 다운로드 후 설치
```

### 장점
- ✅ 전문적인 설치 경험
- ✅ 시작 메뉴 등록
- ✅ 제어판에서 제거 가능
- ✅ 바탕화면 아이콘 (옵션)

### 단점
- ⚠️ Inno Setup 설치 필요
- ⚠️ 빌드 과정 추가

---

## 3️⃣ GitHub Releases 배포 (오픈소스) 🌟

### 준비

**1. GitHub 저장소 생성**
```bash
cd hancell-converter-project
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/yourusername/hancell-converter.git
git push -u origin main
```

**2. exe 빌드 (Windows에서)**
```batch
build.bat
```

**3. GitHub Release 생성**

```
1. GitHub 저장소 → Releases → Create a new release
2. Tag: v1.0.0
3. Title: 한셀 파일 일괄 변환기 v1.0.0
4. Description:
   ## 주요 기능
   - 드래그앤드롭 파일 변환
   - PDF, HTML, XLS, XLSX 지원
   - 실패 재시도 기능

   ## 다운로드
   아래 Assets에서 파일 다운로드

5. Assets: dist/한셀변환기.exe 업로드
6. Publish release
```

### 장점
- ✅ 버전 관리 자동
- ✅ 변경 이력 관리
- ✅ 다운로드 통계
- ✅ 업데이트 알림 가능

### 단점
- ⚠️ GitHub 계정 필요
- ⚠️ 공개 저장소 (무료)

---

## 4️⃣ 자동 배포 (CI/CD)

GitHub Actions로 자동 빌드 및 배포

### .github/workflows/release.yml

프로젝트에 포함된 워크플로우 파일 사용:
- Push 시 자동 테스트
- Tag 생성 시 자동 빌드 및 Release

**사용법:**
```bash
# 태그 생성 및 푸시
git tag v1.0.0
git push origin v1.0.0

# → GitHub Actions가 자동으로:
#    1. 테스트 실행
#    2. exe 빌드
#    3. Release 생성
#    4. exe 업로드
```

---

## 5️⃣ Microsoft Store 배포 (고급)

### 요구사항
- Microsoft 개발자 계정 ($19/년)
- MSIX 패키징
- 앱 심사 통과

### 단계
```
1. Microsoft Partner Center 계정 생성
2. 앱 등록 및 정보 입력
3. MSIX 패키지 생성
   - MSIX Packaging Tool 사용
4. 앱 제출 및 심사 대기 (1-3일)
5. 승인 후 Microsoft Store에서 다운로드 가능
```

### 장점
- ✅ 자동 업데이트
- ✅ Windows 통합
- ✅ 신뢰성 향상

### 단점
- ❌ 연간 비용
- ❌ 심사 필요
- ❌ 복잡한 설정

---

## 📋 배포 체크리스트

### 빌드 전
- [ ] 모든 테스트 통과 확인
- [ ] 버전 번호 업데이트
- [ ] CHANGELOG.md 업데이트
- [ ] README.md 확인

### 빌드
- [ ] Windows 환경에서 build.bat 실행
- [ ] exe 파일 동작 테스트
- [ ] 한셀 자동화 테스트
- [ ] 실제 파일 변환 테스트

### 배포
- [ ] exe 파일 또는 Installer 생성
- [ ] GitHub Release 또는 웹사이트 업로드
- [ ] 다운로드 링크 테스트
- [ ] 사용 가이드 제공

### 배포 후
- [ ] 사용자 피드백 수집
- [ ] 버그 리포트 모니터링
- [ ] 업데이트 계획 수립

---

## 🚀 추천 배포 시나리오

### 개인/소규모 사용
```
1. build.bat으로 exe 생성
2. USB 또는 네트워크 공유로 배포
```

### 팀/회사 내부 사용
```
1. Inno Setup으로 Installer 생성
2. 내부 웹사이트에서 다운로드 제공
3. 버전별 변경 이력 관리
```

### 오픈소스/공개 배포
```
1. GitHub 저장소 생성
2. GitHub Releases 사용
3. CI/CD 자동화
4. 이슈 트래커로 피드백 수집
```

### 상용 소프트웨어
```
1. Inno Setup으로 Installer 생성
2. 자체 웹사이트 + 결제 시스템
3. 라이선스 관리 시스템
4. (선택) Microsoft Store 등록
```

---

## 📝 버전 관리

### Semantic Versioning (권장)

```
v1.0.0
 │ │ │
 │ │ └─ PATCH: 버그 수정
 │ └─── MINOR: 새 기능 (하위 호환)
 └───── MAJOR: 큰 변경 (하위 호환 안됨)
```

**예시:**
- v1.0.0: 초기 릴리스
- v1.0.1: 버그 수정
- v1.1.0: 새 기능 추가 (win32com 지원)
- v2.0.0: UI 대폭 변경

---

## 🔄 업데이트 전략

### 수동 업데이트
```
1. 새 버전 빌드
2. 사용자에게 공지
3. 다운로드 링크 제공
4. 사용자가 직접 재설치
```

### 반자동 업데이트
```python
# app.py에 추가
import requests

def check_update():
    try:
        r = requests.get("https://api.github.com/repos/user/repo/releases/latest")
        latest = r.json()["tag_name"]
        current = "v1.0.0"

        if latest > current:
            # 업데이트 알림 표시
            show_update_dialog(latest)
    except:
        pass
```

### 자동 업데이트 (고급)
```
- Microsoft Store: 자동
- Squirrel.Windows 사용
- 복잡하므로 필요시에만
```

---

## 📞 지원 및 피드백

배포 후 사용자 지원을 위한 채널:

1. **GitHub Issues** (오픈소스)
   - 버그 리포트
   - 기능 요청
   - Q&A

2. **이메일**
   - support@yourcompany.com

3. **문서**
   - README.md
   - FAQ.md
   - 비디오 튜토리얼

---

## 💡 팁

### 파일 크기 줄이기
```bash
# PyInstaller 옵션
pyinstaller --onefile --noconsole --strip app.py

# UPX 압축 사용
pyinstaller --upx-dir=/path/to/upx ...
```

### 바이러스 백신 오탐지 방지
```
1. 코드 서명 인증서 구매 (연 $200-500)
2. exe 파일에 디지털 서명
3. 백신 업체에 오탐 신고
```

### 다국어 지원
```
1. 영어 README 추가
2. UI 다국어 지원
3. 여러 언어로 Release Notes 작성
```

# Mac에서 Windows exe 빌드하기

Mac 환경에서 Windows exe를 빌드하는 방법입니다.

## ⚠️ 중요: Mac에서 직접 빌드는 불가능

PyInstaller는 **크로스 컴파일을 지원하지 않습니다.**
- Mac → Mac용 .app만 가능
- Windows → Windows용 .exe만 가능
- Linux → Linux용 binary만 가능

## 🔧 해결 방법

### 방법 1: Windows PC 사용 (가장 간단) ✅

```bash
# 1. 프로젝트를 Windows PC로 전송
zip -r hancell-converter.zip hancell-converter-project/

# 2. Windows PC에서
# - 압축 해제
# - setup.bat 실행
# - build.bat 실행
# - dist/한셀변환기.exe 생성됨
```

**전송 방법:**
- USB 메모리
- 클라우드 (Google Drive, Dropbox)
- 이메일
- 네트워크 공유
- GitHub

---

### 방법 2: 가상 머신 (Mac에서 Windows 실행)

#### A. Parallels Desktop (유료, $99/년)

**장점:** 빠르고 쉬움
**단점:** 유료

```bash
1. Parallels Desktop 설치
2. Windows 10/11 설치
3. 프로젝트 폴더 공유
4. Windows에서 build.bat 실행
```

#### B. VirtualBox (무료)

**장점:** 무료
**단점:** 느림

```bash
# 1. VirtualBox 설치
brew install --cask virtualbox

# 2. Windows ISO 다운로드
# https://www.microsoft.com/software-download/windows11

# 3. 가상 머신 생성
# - RAM: 최소 4GB
# - 디스크: 50GB
# - Windows 설치

# 4. 공유 폴더 설정
# VirtualBox → 설정 → 공유 폴더
# Mac의 hancell-converter-project 폴더 공유

# 5. Windows에서 빌드
cd Z:\hancell-converter-project  # 공유 폴더
setup.bat
build.bat
```

#### C. UTM (무료, Apple Silicon 최적화)

**M1/M2 Mac 사용자에게 적합**

```bash
# 1. UTM 설치
brew install --cask utm

# 2. Windows 11 ARM 설치
# https://www.microsoft.com/software-download/windowsinsiderpreview

# 3. Python 설치 (ARM64 버전)
# 4. build.bat 실행
```

---

### 방법 3: 클라우드 빌드 서비스

#### GitHub Actions (무료) ✅

**자동으로 Windows 환경에서 빌드!**

```bash
# 1. GitHub 저장소 생성
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/yourusername/hancell-converter.git
git push -u origin main

# 2. Tag 생성
git tag v1.0.0
git push origin v1.0.0

# 3. GitHub Actions가 자동으로:
# - Windows 환경에서 빌드
# - exe 파일 생성
# - Release에 업로드
```

**결과:** GitHub Releases에서 exe 다운로드 가능!

프로젝트에 이미 `.github/workflows/release.yml` 파일이 있습니다.

---

### 방법 4: Docker + Wine (고급, 비추천)

**복잡하고 불안정하므로 권장하지 않음**

```bash
# Wine은 Windows 에뮬레이터
# PyInstaller + Wine 조합은 불안정
# 대부분 실패하거나 오류 발생
```

---

## 🎯 추천 순서

### 상황별 최적 방법

**1. Windows PC가 있다면:**
```
→ Windows PC 사용 (가장 확실)
```

**2. Windows PC가 없다면:**
```
→ GitHub Actions (무료, 자동화)
```

**3. 가상 머신을 원한다면:**
```
- 유료 OK → Parallels Desktop
- 무료 → VirtualBox
- M1/M2 Mac → UTM
```

**4. 급한 경우:**
```
→ 지인의 Windows PC 빌려쓰기
→ PC방 이용
→ 회사/학교 Windows PC
```

---

## 📋 GitHub Actions로 빌드하기 (추천!)

### 준비물
- GitHub 계정 (무료)
- 5분

### 단계

**1. GitHub 저장소 생성**
```bash
# Mac 터미널에서
cd hancell-converter-project

# Git 초기화
git init
git add .
git commit -m "Initial commit: 한셀 파일 일괄 변환기 v1.0.0"

# GitHub에서 새 저장소 생성 후
git remote add origin https://github.com/yourusername/hancell-converter.git
git push -u origin main
```

**2. Tag 생성 및 푸시**
```bash
git tag v1.0.0
git push origin v1.0.0
```

**3. GitHub Actions 자동 실행**
```
GitHub → Actions 탭
→ "Build and Release" 워크플로우 실행 중
→ 약 5-10분 소요

완료 후:
→ Releases 탭
→ v1.0.0 릴리스
→ 한셀변환기.exe 다운로드 가능!
```

**4. exe 다운로드**
```
https://github.com/yourusername/hancell-converter/releases/download/v1.0.0/한셀변환기.exe
```

### 장점
✅ Windows 불필요
✅ 완전 자동화
✅ 무료
✅ 버전 관리 자동
✅ Mac에서 모든 작업 가능

---

## 🔍 비교표

| 방법 | 비용 | 난이도 | 시간 | Windows PC 필요 |
|------|------|--------|------|-----------------|
| **Windows PC 사용** | 무료 | ⭐ 쉬움 | 10분 | ✅ 필요 |
| **GitHub Actions** | 무료 | ⭐⭐ 보통 | 15분 | ❌ 불필요 |
| **Parallels** | $99/년 | ⭐ 쉬움 | 1시간 | ❌ 불필요 |
| **VirtualBox** | 무료 | ⭐⭐⭐ 어려움 | 2시간 | ❌ 불필요 |
| **UTM (M1/M2)** | 무료 | ⭐⭐⭐ 어려움 | 2시간 | ❌ 불필요 |

---

## 💡 결론

### Windows PC가 있으면:
```bash
# Windows PC에서
cd hancell-converter-project
setup.bat
build.bat
# → dist/한셀변환기.exe 완성!
```

### Windows PC가 없으면:
```bash
# Mac에서
git tag v1.0.0
git push origin v1.0.0
# → GitHub Actions가 자동으로 exe 생성!
```

---

## 📝 참고

Mac에서 할 수 있는 일:
- ✅ 코드 작성
- ✅ 테스트 (pytest)
- ✅ 로직 검증
- ✅ 문서 작성
- ❌ Windows exe 빌드 (불가능)

Windows가 필요한 일:
- exe 파일 빌드
- 실제 한셀 자동화 테스트
- UI 테스트

하지만 **GitHub Actions를 사용하면** Mac에서도 모든 것이 가능합니다!

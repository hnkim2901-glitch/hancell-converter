#!/bin/bash
# Mac에서 테스트 실행 스크립트

echo "========================================="
echo "한셀 변환기 테스트 실행 (Mac)"
echo "========================================="
echo ""

# 색상 정의
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Python 버전 확인
echo "📍 Python 버전 확인..."
python3 --version

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Python3가 설치되어 있지 않습니다.${NC}"
    exit 1
fi

echo ""

# 가상 환경 확인/생성
if [ ! -d "venv" ]; then
    echo "📦 가상 환경 생성 중..."
    python3 -m venv venv
    echo -e "${GREEN}✅ 가상 환경 생성 완료${NC}"
else
    echo -e "${GREEN}✅ 기존 가상 환경 사용${NC}"
fi

echo ""

# 가상 환경 활성화
echo "🔄 가상 환경 활성화..."
source venv/bin/activate

echo ""

# 테스트 의존성 설치
echo "📦 테스트 의존성 설치..."
pip install -q -r requirements-test.txt

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ 의존성 설치 실패${NC}"
    exit 1
fi

echo -e "${GREEN}✅ 의존성 설치 완료${NC}"
echo ""

# pytest 실행
echo "🧪 테스트 실행 중..."
echo ""

pytest tests/ -v --tb=short --color=yes

TEST_RESULT=$?

echo ""
echo "========================================="

if [ $TEST_RESULT -eq 0 ]; then
    echo -e "${GREEN}✅ 모든 테스트 통과!${NC}"
else
    echo -e "${RED}❌ 일부 테스트 실패${NC}"
fi

echo "========================================="
echo ""

# 커버리지 리포트 (선택)
read -p "커버리지 리포트를 생성하시겠습니까? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "📊 커버리지 리포트 생성 중..."
    pytest tests/ --cov=converter --cov=utils --cov-report=html --cov-report=term
    echo ""
    echo -e "${GREEN}✅ 커버리지 리포트: htmlcov/index.html${NC}"
    echo ""

    # macOS에서 자동으로 브라우저 열기
    if [[ "$OSTYPE" == "darwin"* ]]; then
        open htmlcov/index.html
    fi
fi

exit $TEST_RESULT

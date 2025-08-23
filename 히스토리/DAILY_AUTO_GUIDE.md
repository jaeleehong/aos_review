# 매일 00:05 Google Play 리뷰 자동 캡처 시스템

## 🎯 개요
매일 00시 05분에 자동으로 Google Play 리뷰를 캡처하고 HTML 리포트를 업데이트하는 완전 자동화 시스템입니다.

## 📁 파일 구조
```
D:\aos review\
├── auto_capture_and_update.py    # 메인 자동화 스크립트
├── daily_auto_capture.bat        # 매일 실행 배치 파일
├── setup_scheduler.bat           # 작업 스케줄러 등록
├── remove_scheduler.bat          # 작업 스케줄러 제거
├── check_status.bat              # 시스템 상태 확인
├── 구글 플레이_리뷰.html          # HTML 리포트
├── logs/                         # 로그 폴더
│   └── auto_capture_YYYYMMDD.log # 일별 로그
├── 20250813/                     # 캡처된 이미지 폴더
├── 20250821/
└── 20250822/
```

## 🚀 설치 및 설정

### 1. 의존성 설치
```bash
pip install -r requirements_auto.txt
```

### 2. 작업 스케줄러 등록
**관리자 권한으로 실행:**
```bash
setup_scheduler.bat
```

### 3. 설정 확인
```bash
check_status.bat
```

## ⏰ 자동화 스케줄

### 실행 시간
- **매일 00:05** 자동 실행
- 백그라운드에서 실행 (화면 표시 없음)
- 완료 후 자동 종료

### 실행 과정
1. **00:05** - 자동 캡처 시작
2. **00:05~00:15** - 9개 게임 순차 캡처
3. **00:15~00:16** - HTML 파일 업데이트
4. **00:16** - 완료 및 종료

## 📊 모니터링

### 로그 확인
```bash
# 오늘 로그 확인
type logs\auto_capture_%date:~0,4%%date:~5,2%%date:~8,2%.log

# 최근 로그 확인
check_status.bat
```

### 상태 확인 항목
1. **작업 스케줄러 상태** - 등록된 작업 확인
2. **최근 로그** - 마지막 실행 결과
3. **캡처된 폴더** - 생성된 날짜별 폴더
4. **HTML 파일** - 리포트 파일 존재 여부
5. **Python 환경** - 필요한 라이브러리 설치 상태

## 🔧 관리 도구

### 작업 스케줄러 관리
```bash
# 등록
setup_scheduler.bat

# 제거
remove_scheduler.bat

# 상태 확인
check_status.bat
```

### 수동 실행
```bash
# 즉시 실행
daily_auto_capture.bat

# Python 스크립트 직접 실행
python auto_capture_and_update.py
```

## 📋 자동화 프로세스

### 1. 캡처 단계
- Chrome WebDriver 백그라운드 실행
- 각 게임의 Google Play 페이지 접속
- "리뷰 모두 보기" 버튼 클릭
- 평점 표시 하단부터 리뷰 모두 보기까지 캡처
- YYYYMMDD 폴더에 영문 파일명으로 저장

### 2. HTML 업데이트 단계
- 날짜 선택 드롭다운에 새 날짜 추가
- 통계 정보 업데이트
  - 캡처 일수 +1
  - 총 이미지 +9
  - 최근 캡처 날짜 업데이트
- 새 날짜의 콘텐츠 섹션 생성
- 전주 대비 비교 구조로 구성

### 3. 로그 기록
- 모든 과정을 상세 로그로 기록
- 성공/실패 상태 표시
- 오류 발생 시 상세 정보 기록

## 🎯 주요 기능

### 완전 자동화
- **매일 00:05 자동 실행**
- **백그라운드 실행** (화면 표시 없음)
- **자동 오류 처리** 및 재시도
- **상세 로그 기록**

### 스마트 업데이트
- **전주 대비 비교** 구조
- **사업실별 그룹화** (레드/블루/브라운)
- **통계 정보 실시간 업데이트**
- **중복 실행 방지**

### 모니터링 시스템
- **실시간 상태 확인**
- **로그 기반 문제 진단**
- **성공/실패 알림**

## 🔧 문제 해결

### 일반적인 문제

#### 1. 작업 스케줄러 등록 실패
```bash
# 관리자 권한으로 실행
setup_scheduler.bat
```

#### 2. Chrome WebDriver 오류
```bash
# Chrome 브라우저 업데이트
# Selenium 재설치
pip install --upgrade selenium
```

#### 3. 캡처 실패
```bash
# 로그 확인
check_status.bat

# 네트워크 연결 확인
# Google Play 페이지 접근 가능 여부 확인
```

#### 4. HTML 업데이트 실패
```bash
# 파일 권한 확인
# HTML 파일 백업 후 재시도
```

### 로그 분석
```bash
# 상세 로그 확인
type logs\auto_capture_YYYYMMDD.log

# 오류만 필터링
findstr "ERROR" logs\auto_capture_YYYYMMDD.log
```

## 📞 지원

### 정기 점검
- **매주 월요일** - 시스템 상태 확인
- **매월 1일** - 로그 파일 정리
- **분기별** - Python 라이브러리 업데이트

### 백업 권장사항
- **HTML 파일** - 주간 백업
- **캡처 이미지** - 월간 백업
- **로그 파일** - 분기별 백업

### 연락처
- 문제 발생 시 로그 파일과 함께 문의
- 네트워크 환경 안정성 확인 필요




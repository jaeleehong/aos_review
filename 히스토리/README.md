# AOS 리뷰 자동 캡처 시스템

Google Play 리뷰를 자동으로 캡처하고 HTML 대시보드를 업데이트하는 시스템입니다.

## 🚀 주요 기능

- **자동 캡처**: 9개 게임의 Google Play 리뷰 자동 캡처
- **HTML 대시보드**: 실시간 리뷰 현황 확인
- **GitHub 자동 배포**: 캡처 후 자동으로 GitHub Pages에 배포
- **스케줄링**: 매일 00:10에 자동 실행

## 📋 지원 게임

### 🎴 레드사업실
- 뉴맞고 (NewMatgo)
- 뉴맞고카카오 (NewMatgoKakao)
- 섯다 (Sudda)
- 섯다카카오 (SuddaKakao)
- 오리지널 (Original)

### 🃏 블루사업실
- 포커 (Poker)
- 포커카카오 (PokerKakao)
- 쇼다운홀덤 (ShowdownHoldem)

### 🎰 브라운사업실
- 뉴베가스 (NewVegas)

## 🛠️ 설치 및 설정

### 1. 필수 요구사항

- Python 3.8+
- Firefox 브라우저
- Git
- Windows 10/11

### 2. 의존성 설치

```bash
pip install -r requirements.txt
```

### 3. 자동화 설정

#### 자동 스케줄러 설정 (관리자 권한 필요)

```bash
# 관리자 권한으로 명령 프롬프트 실행 후
python setup_scheduler.py
```

이 명령어는 매일 00:10에 자동으로 실행되도록 Windows 작업 스케줄러를 설정합니다.

## 📁 파일 구조

```
aos_review/
├── auto_capture_and_update.py    # 메인 캡처 스크립트
├── daily_auto_capture.bat        # 자동 실행 배치 파일
├── local_auto_capture.bat        # 수동 실행 배치 파일
├── setup_scheduler.py            # 스케줄러 설정 스크립트
├── aos_review.html              # 메인 대시보드
├── 20250824/                    # 캡처된 이미지들
├── 앱아이콘/                    # 게임 아이콘들
└── logs/                        # 로그 파일들
```

## 🎯 사용 방법

### 자동 실행 (권장)
- 스케줄러 설정 후 매일 00:10에 자동으로 실행됩니다
- 별도 조작 없이 자동으로 캡처 및 배포됩니다

### 수동 실행
```bash
# 수동으로 캡처 및 배포
local_auto_capture.bat
```

### 개별 실행
```bash
# 캡처만 실행
python auto_capture_and_update.py
```

## 📊 대시보드 확인

- **로컬**: `aos_review.html` 파일을 브라우저에서 열기
- **온라인**: [https://jaeleehong.github.io/aos_review/aos_review.html](https://jaeleehong.github.io/aos_review/aos_review.html)

## 📝 로그 확인

- **자동 실행 로그**: `logs/auto_capture_YYYYMMDD.log`
- **배포 로그**: `logs/auto_deploy.log`
- **수동 실행 로그**: `logs/manual_deploy.log`

## ⚙️ 설정 옵션

### 실행 시간 변경
`setup_scheduler.py` 파일에서 다음 부분을 수정:

```python
"/st", "00:10",  # 원하는 시간으로 변경 (HH:MM 형식)
```

### 게임 추가/제거
`auto_capture_and_update.py` 파일의 `GAMES` 딕셔너리를 수정:

```python
GAMES = {
    "com.neowiz.games.newmatgo": "NewMatgo",
    # 새 게임 추가
    "com.example.newgame": "NewGame"
}
```

## 🔧 문제 해결

### 스케줄러 설정 실패
- 관리자 권한으로 실행했는지 확인
- Windows 작업 스케줄러 서비스가 실행 중인지 확인

### 캡처 실패
- Firefox가 설치되어 있는지 확인
- 인터넷 연결 상태 확인
- `logs/` 폴더의 로그 파일 확인

### GitHub 배포 실패
- Git 설정이 올바른지 확인
- GitHub 인증 정보 확인

## 📞 지원

문제가 발생하면 `logs/` 폴더의 로그 파일을 확인하거나 개발팀에 문의하세요.

---

© 2025 AION실 - Google Play 리뷰 자동 캡처 시스템

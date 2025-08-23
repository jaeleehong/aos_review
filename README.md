# Google Play 리뷰 자동 캡처 시스템

매일 자동으로 Google Play Store의 게임 리뷰를 캡처하고 HTML 파일에 업데이트하는 자동화 시스템입니다.

## 🎮 지원 게임

- **NewMatgo** (뉴맞고)
- **NewMatgoKakao** (뉴맞고카카오)
- **Original** (오리지널/고스톱2018)
- **Poker** (포커)
- **PokerKakao** (포커카카오)
- **Sudda** (섯다)
- **SuddaKakao** (섯다카카오)
- **ShowdownHoldem** (쇼다운홀덤)
- **NewVegas** (뉴베가스)

## 📁 프로젝트 구조

```
D:\aos review\
├── auto_capture_and_update.py    # 메인 자동화 스크립트
├── daily_auto_capture.bat        # 스케줄러용 배치 파일
├── setup_scheduler.py            # 스케줄러 설정 도구
├── google_play_review_capture.py # 수동 캡처 스크립트
├── update_html_images.py         # HTML 업데이트 스크립트
├── 구글 플레이_리뷰.html         # 메인 HTML 파일
├── logs/                         # 로그 파일 폴더
├── 20250823/                     # 캡처된 이미지 폴더 (날짜별)
├── 앱아이콘/                     # 게임 아이콘 폴더
└── .gitignore                    # Git 무시 파일 설정
```

## ⚙️ 설치 및 설정

### 1. 필수 요구사항
- Python 3.7+
- Firefox 브라우저
- Selenium WebDriver
- PIL (Pillow)
- BeautifulSoup4

### 2. 의존성 설치
```bash
pip install selenium pillow beautifulsoup4
```

### 3. Firefox WebDriver 설치
Firefox 브라우저가 설치되어 있어야 합니다.

## 🚀 사용법

### 자동 실행 설정 (권장)
```bash
python setup_scheduler.py
```
- 매일 00:10에 자동으로 실행됩니다
- 관리자 권한이 필요합니다

### 수동 실행
```bash
python auto_capture_and_update.py
```

### 개별 게임 캡처
```bash
python google_play_review_capture.py
```

## 📊 결과물

### 캡처된 이미지
- **위치**: `{날짜}/` 폴더 (예: `20250823/`)
- **형식**: `{게임명}_{날짜}.png`
- **크기**: 1200px 너비, 리뷰 섹션 높이

### HTML 리포트
- **파일**: `구글 플레이_리뷰.html`
- **내용**: 모든 게임의 리뷰 캡처 이미지
- **자동 업데이트**: 매일 캡처 후 자동 반영

### 로그 파일
- **위치**: `logs/` 폴더
- **형식**: `auto_capture_{날짜}.log`
- **내용**: 실행 과정 및 오류 정보

## 🔧 설정 옵션

### 실행 시간 변경
`setup_scheduler.py` 파일에서 다음 부분을 수정:
```python
"/st", "00:10"  # 원하는 시간으로 변경
```

### 게임 목록 수정
`auto_capture_and_update.py` 파일의 `GAMES` 딕셔너리를 수정:
```python
GAMES = {
    "com.neowiz.games.newmatgo": "NewMatgo",
    # 새로운 게임 추가
}
```

## 📝 주의사항

1. **PC 상태**: 자동 실행을 위해서는 PC가 켜져 있어야 합니다
2. **인터넷 연결**: Google Play Store 접속을 위해 인터넷이 필요합니다
3. **관리자 권한**: 스케줄러 설정 시 관리자 권한이 필요합니다
4. **브라우저 업데이트**: Firefox 브라우저가 최신 버전이어야 합니다

## 🛠️ 문제 해결

### 스케줄러가 실행되지 않는 경우
1. 관리자 권한으로 `setup_scheduler.py` 재실행
2. Windows 작업 스케줄러에서 작업 상태 확인
3. 로그 파일에서 오류 메시지 확인

### 캡처가 실패하는 경우
1. 인터넷 연결 상태 확인
2. Firefox 브라우저 업데이트
3. 로그 파일에서 상세 오류 확인

## 📄 라이선스

이 프로젝트는 개인 및 교육 목적으로 사용됩니다.

## 🤝 기여

버그 리포트나 기능 제안은 이슈로 등록해주세요.

# 구글 플레이 리뷰 캡쳐 도구

이 도구는 구글 플레이 스토어에서 지정된 게임들의 리뷰 섹션을 자동으로 캡쳐하는 파이썬 스크립트입니다.

## 설치 방법

1. **Python 설치**
   - Python 3.7 이상이 필요합니다.

2. **필요한 라이브러리 설치**
   ```bash
   pip install -r requirements.txt
   ```

3. **Chrome WebDriver 설치**
   - Chrome 브라우저가 설치되어 있어야 합니다.
   - ChromeDriver는 자동으로 다운로드됩니다 (selenium-manager 사용).

## 사용 방법

1. **스크립트 실행**
   ```bash
   python google_play_review_capture_v3.py
   ```

2. **결과 확인**
   - 캡쳐된 이미지는 `D:\aos review\YYYYMMDD\` 폴더에 저장됩니다.
   - 파일명 형식: `게임명_YYYYMMDD.png` (영문)

## 캡쳐 대상 게임

- NewMatgo (com.neowiz.games.newmatgo)
- NewMatgoKakao (com.neowiz.games.newmatgoKakao)
- Original (com.neowiz.games.gostop2018)
- Poker (com.neowiz.games.poker)
- PokerKakao (com.neowiz.games.pokerKakao)
- Sudda (com.neowiz.games.sudda)
- SuddaKakao (com.neowiz.games.suddaKakao)
- ShowdownHoldem (com.neowiz.games.pmang.holdem.poker)
- NewVegas (com.neowiz.playstudio.slot.casino)

## 캡쳐 영역

- **시작점**: 평점 표시 영역 하단
- **끝점**: "리뷰 모두 보기" 링크까지
- **내용**: 사용자 리뷰, 평점, 개발자 답변 등

## 주의사항

1. **인터넷 연결**: 안정적인 인터넷 연결이 필요합니다.
2. **Chrome 브라우저**: Chrome 브라우저가 설치되어 있어야 합니다.
3. **실행 시간**: 9개 게임을 순차적으로 처리하므로 약 5-10분 정도 소요됩니다.
4. **헤드리스 모드**: 기본적으로 브라우저 창이 표시됩니다. 헤드리스 모드로 실행하려면 코드에서 주석을 해제하세요.
5. **파일명**: 모든 파일은 영문으로 저장됩니다.

## 문제 해결

- **ChromeDriver 오류**: Chrome 브라우저를 최신 버전으로 업데이트하세요.
- **요소를 찾을 수 없음**: 구글 플레이 페이지 구조가 변경되었을 수 있습니다. XPath를 업데이트해야 할 수 있습니다.
- **권한 오류**: `D:\aos review` 폴더에 쓰기 권한이 있는지 확인하세요.

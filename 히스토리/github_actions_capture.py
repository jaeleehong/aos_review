#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub Actions용 Google Play 리뷰 자동 캡처 스크립트
"""

import os
import datetime
import logging
import time
import re
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from PIL import Image
from webdriver_manager.firefox import GeckoDriverManager
import io

# 게임 정보 정의
GAMES = {
    "com.neowiz.games.newmatgo": "NewMatgo",
    "com.neowiz.games.newmatgoKakao": "NewMatgoKakao",
    "com.neowiz.games.gostop2018": "Original",
    "com.neowiz.games.poker": "Poker",
    "com.neowiz.games.pokerKakao": "PokerKakao",
    "com.neowiz.games.sudda": "Sudda",
    "com.neowiz.games.suddaKakao": "SuddaKakao",
    "com.neowiz.games.pmang.holdem.poker": "ShowdownHoldem",
    "com.neowiz.playstudio.slot.casino": "NewVegas"
}

def setup_logging():
    """로깅 설정"""
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    
    log_file = os.path.join(log_dir, f"github_actions_capture_{datetime.datetime.now().strftime('%Y%m%d')}.log")
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def setup_driver():
    """GitHub Actions용 Firefox WebDriver 설정"""
    firefox_options = Options()
    
    # 헤드리스 모드 설정 (GitHub Actions 환경에 최적화)
    firefox_options.add_argument("--headless")
    firefox_options.add_argument("--no-sandbox")
    firefox_options.add_argument("--disable-dev-shm-usage")
    firefox_options.add_argument("--width=1920")
    firefox_options.add_argument("--height=1080")
    firefox_options.add_argument("--disable-gpu")
    firefox_options.add_argument("--disable-extensions")
    firefox_options.add_argument("--disable-plugins")
    firefox_options.add_argument("--disable-background-timer-throttling")
    firefox_options.add_argument("--disable-backgrounding-occluded-windows")
    firefox_options.add_argument("--disable-renderer-backgrounding")
    
    # 브라우저 설정
    firefox_options.set_preference("dom.webdriver.enabled", False)
    firefox_options.set_preference("useAutomationExtension", False)
    firefox_options.set_preference("general.useragent.override", 
                                 "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0")
    
    # 한국어 설정
    firefox_options.set_preference("intl.accept_languages", "ko-KR,ko;q=0.9,en;q=0.8")
    firefox_options.set_preference("general.useragent.locale", "ko-KR")
    
    # 네트워크 타임아웃 설정
    firefox_options.set_preference("network.http.connection-timeout", 30)
    firefox_options.set_preference("network.http.response-timeout", 30)
    firefox_options.set_preference("network.http.connection-retry-timeout", 30)
    
    # 메모리 및 성능 최적화
    firefox_options.set_preference("browser.cache.disk.enable", False)
    firefox_options.set_preference("browser.cache.memory.enable", False)
    firefox_options.set_preference("browser.cache.offline.enable", False)
    firefox_options.set_preference("network.http.use-cache", False)
    
    # 로컬 환경에서 실행
    try:
        from selenium.webdriver.firefox.service import Service
        # 특정 버전의 geckodriver 사용 (안정성 향상)
        service = Service(GeckoDriverManager(version="v0.33.0").install())
        
        # 로컬 Firefox 경로 설정
        firefox_options.binary_location = r"C:\Program Files\Mozilla Firefox\firefox.exe"
        
        driver = webdriver.Firefox(service=service, options=firefox_options)
        driver.set_page_load_timeout(60)
        driver.implicitly_wait(10)
        
        # 추가 대기 시간 (로컬 환경 안정화)
        time.sleep(3)
        
    except Exception as e:
        print(f"Firefox WebDriver 초기화 실패: {e}")
        raise
    
    return driver

def capture_game_review(driver, app_id, game_name, save_dir, logger):
    """게임 리뷰 섹션 캡처"""
    url = f"https://play.google.com/store/apps/details?id={app_id}&hl=ko"
    
    try:
        logger.info(f"캡처 시작: {game_name}")
        driver.get(url)
        time.sleep(8)  # 페이지 로딩 대기
        
        # 한국어로 강제 설정
        logger.info("한국어 설정 적용")
        driver.execute_script("""
            // 언어 설정을 한국어로 변경
            if (navigator.language !== 'ko-KR') {
                Object.defineProperty(navigator, 'language', {
                    get: function() { return 'ko-KR'; }
                });
            }
            if (navigator.languages) {
                Object.defineProperty(navigator, 'languages', {
                    get: function() { return ['ko-KR', 'ko', 'en-US', 'en']; }
                });
            }
        """)
        
        # 한국어 URL로 리다이렉트 시도
        current_url = driver.current_url
        if 'hl=ko' not in current_url:
            korean_url = current_url + ('&' if '?' in current_url else '?') + 'hl=ko'
            logger.info(f"한국어 URL로 리다이렉트: {korean_url}")
            driver.get(korean_url)
            time.sleep(3)
        
        # "리뷰 모두 보기" 버튼을 클릭하지 않고 기본 리뷰 섹션만 캡처
        logger.info(f"기본 리뷰 섹션 캡처 시작: {game_name} (버튼 클릭 없음)")
        
        # 시작 요소 찾기 ('평점 및 리뷰' 텍스트를 포함하는 요소)
        start_element = None
        start_element_selectors = [
            "//h2[text()='평점 및 리뷰']",
            "//h2[contains(text(), '평점')]",
            "//h2[contains(text(), '리뷰')]",
            "//div[contains(text(), '평점 및 리뷰')]",
            "//span[contains(text(), '평점 및 리뷰')]"
        ]
        
        for i, selector in enumerate(start_element_selectors):
            try:
                start_element = driver.find_element(By.XPATH, selector)
                logger.info(f"시작 요소 찾기 성공: '평점 및 리뷰' (선택자 {i+1}: {selector})")
                break
            except Exception as e:
                logger.debug(f"시작 요소 선택자 {i+1} 실패: {selector} - {e}")
                continue
        
        if start_element is None:
            logger.error(f"시작 요소를 찾을 수 없습니다: '평점 및 리뷰'")
            return False
        
        # 끝 요소 찾기 ('리뷰 모두 보기' 텍스트를 포함하는 요소)
        end_element = None
        end_element_selectors = [
            "//div[@role='button']//span[text()='리뷰 모두 보기']",
            "//span[text()='리뷰 모두 보기']",
            "//div[contains(text(), '리뷰 모두 보기')]",
            "//button[contains(text(), '리뷰 모두 보기')]",
            "//a[contains(text(), '리뷰 모두 보기')]"
        ]
        
        for i, selector in enumerate(end_element_selectors):
            try:
                end_element = driver.find_element(By.XPATH, selector)
                logger.info(f"끝 요소 찾기 성공: '리뷰 모두 보기' (선택자 {i+1}: {selector})")
                break
            except Exception as e:
                logger.debug(f"끝 요소 선택자 {i+1} 실패: {selector} - {e}")
                continue
        
        if end_element is None:
            logger.error(f"끝 요소를 찾을 수 없습니다: '리뷰 모두 보기'")
            return False
        
        # 시작 요소로 스크롤
        logger.info(f"시작 요소로 스크롤: {game_name}")
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'start'});", start_element)
        time.sleep(3)  # 스크롤 완료 대기
        
        # 전체 페이지 높이 설정
        logger.info("전체 페이지 높이 설정")
        total_height = driver.execute_script("return document.body.scrollHeight")
        driver.set_window_size(1920, total_height)
        time.sleep(2)
        
        # 스크린샷 촬영
        logger.info(f"전체 페이지 스크린샷 촬영: {game_name}")
        screenshot = driver.get_screenshot_as_png()
        img = Image.open(io.BytesIO(screenshot))
        
        logger.info(f"전체 스크린샷 크기: {img.width} x {img.height}")
        
        # 시작 요소와 끝 요소 위치 정보 가져오기
        start_location = start_element.location
        start_size = start_element.size
        end_location = end_element.location
        end_size = end_element.size
        
        logger.info(f"시작 요소 위치: x={start_location['x']}, y={start_location['y']}")
        logger.info(f"시작 요소 크기: width={start_size['width']}, height={start_size['height']}")
        logger.info(f"끝 요소 위치: x={end_location['x']}, y={end_location['y']}")
        logger.info(f"끝 요소 크기: width={end_size['width']}, height={end_size['height']}")
        
        # 캡처 영역 계산 (20250823과 동일한 영역으로 정확히 맞춤)
        # 시작 요소 위쪽에 평점 요약이 있으므로 더 위쪽으로 확장
        crop_left = max(0, start_location['x'] - 150)  # 시작 요소 왼쪽 150px 여유
        crop_top = max(0, start_location['y'] - 300)  # 시작 요소 위쪽 300px 여유 (평점 요약 포함)
        crop_right = min(img.width, start_location['x'] + 1350)  # 너비를 1350px로 확장
        crop_bottom = min(img.height, end_location['y'] + end_size['height'] + 200)  # 끝 요소 아래쪽 200px 여유 (새로운 기능 섹션 포함)
        
        logger.info(f"최종 크롭 영역: left={crop_left}, top={crop_top}, right={crop_right}, bottom={crop_bottom}")
        
        # 크롭 및 저장
        if crop_right > crop_left and crop_bottom > crop_top:
            cropped_img = img.crop((crop_left, crop_top, crop_right, crop_bottom))
        else:
            logger.warning(f"크롭 영역이 유효하지 않습니다. 전체 화면을 캡처합니다.")
            cropped_img = img
        
        # 파일 저장
        filename = f"{game_name}_{datetime.datetime.now().strftime('%Y%m%d')}.png"
        filepath = os.path.join(save_dir, filename)
        cropped_img.save(filepath)
        
        logger.info(f"캡처 완료: {filename} (크기: {cropped_img.width} x {cropped_img.height})")
        return True
        

        
    except Exception as e:
        logger.error(f"캡처 실패 {game_name}: {e}")
        return False

def main():
    """메인 실행 함수"""
    logger = setup_logging()
    logger.info("로컬 캡처 시작")
    
    # 저장 디렉토리 생성
    today = datetime.datetime.now().strftime('%Y%m%d')
    save_dir = today
    os.makedirs(save_dir, exist_ok=True)
    
    driver = None
    try:
        driver = setup_driver()
        logger.info("WebDriver 초기화 완료")
        
        success_count = 0
        total_games = len(GAMES)
        
        for app_id, game_name in GAMES.items():
            if capture_game_review(driver, app_id, game_name, save_dir, logger):
                success_count += 1
            time.sleep(5)  # 요청 간격
        
        logger.info(f"캡처 완료: {success_count}/{total_games} 성공")
        
        # HTML 파일 업데이트
        if success_count > 0:
            update_html_file(today, logger)
            logger.info("HTML 파일 업데이트 완료")
        
    except Exception as e:
        logger.error(f"실행 중 오류 발생: {e}")
        raise
    finally:
        if driver:
            driver.quit()
            logger.info("WebDriver 종료")

def update_html_file(date_folder, logger):
    """HTML 파일에 새로운 날짜 폴더 추가"""
    try:
        # aos_review.html 파일 읽기
        with open('aos_review.html', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 새로운 날짜 폴더가 이미 있는지 확인
        if date_folder not in content:
            # 날짜 선택 옵션에 추가
            date_pattern = r'<option value="(\d{8})">(\d{4}-\d{2}-\d{2})</option>'
            matches = re.findall(date_pattern, content)
            
            # 새로운 날짜 추가
            new_date_option = f'<option value="{date_folder}">{date_folder[:4]}-{date_folder[4:6]}-{date_folder[6:8]}</option>'
            
            # 날짜 옵션들을 정렬하여 추가
            all_dates = [(date_folder, f"{date_folder[:4]}-{date_folder[4:6]}-{date_folder[6:8]}")] + matches
            all_dates.sort(reverse=True)  # 최신 날짜가 위로
            
            # 기존 날짜 옵션들 제거
            for match in matches:
                old_option = f'<option value="{match[0]}">{match[1]}</option>'
                content = content.replace(old_option, '')
            
            # 새로운 날짜 옵션들 추가
            date_options = ''
            for date_val, date_display in all_dates:
                date_options += f'<option value="{date_val}">{date_display}</option>'
            
            # 날짜 선택 부분 찾아서 교체
            date_select_pattern = r'(<select id="dateSelect"[^>]*>).*?(</select>)'
            content = re.sub(date_select_pattern, r'\1' + date_options + r'\2', content, flags=re.DOTALL)
            
            # 파일 저장
            with open('aos_review.html', 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"HTML 파일에 {date_folder} 날짜 추가 완료")
        else:
            logger.info(f"{date_folder} 날짜가 이미 HTML에 존재함")
            
    except Exception as e:
        logger.error(f"HTML 파일 업데이트 실패: {e}")
        raise

if __name__ == "__main__":
    main()

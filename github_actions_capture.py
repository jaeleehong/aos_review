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
    
    # GitHub Actions 환경에서 실행
    try:
        from selenium.webdriver.firefox.service import Service
        # 특정 버전의 geckodriver 사용 (안정성 향상)
        service = Service(GeckoDriverManager(version="v0.33.0").install())
        driver = webdriver.Firefox(service=service, options=firefox_options)
        driver.set_page_load_timeout(60)
        driver.implicitly_wait(10)
        
        # 추가 대기 시간 (GitHub Actions 환경 안정화)
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
        time.sleep(10)  # 페이지 로딩 대기
        
        # 페이지 로딩 대기 및 전체 페이지 캡처
        logger.info(f"페이지 로딩 완료, 전체 페이지 캡처 시작: {game_name}")
        
        # 페이지가 완전히 로드될 때까지 대기
        time.sleep(5)
        
        # 전체 페이지 캡처
        screenshot = driver.get_screenshot_as_png()
        img = Image.open(io.BytesIO(screenshot))
        
        # 저장
        filename = f"{game_name}_{datetime.datetime.now().strftime('%Y%m%d')}.png"
        filepath = os.path.join(save_dir, filename)
        img.save(filepath, "PNG")
        
        logger.info(f"전체 페이지 캡처 완료: {filepath}")
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

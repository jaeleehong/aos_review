#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub Actions용 Google Play 리뷰 자동 캡처 스크립트
"""

import os
import datetime
import logging
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from PIL import Image
from webdriver_manager.chrome import ChromeDriverManager
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
    """GitHub Actions용 Chrome WebDriver 설정"""
    chrome_options = Options()
    
    # 헤드리스 모드 설정
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-plugins")
    chrome_options.add_argument("--disable-images")
    chrome_options.add_argument("--disable-javascript")
    
    # User-Agent 설정
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    # 언어 설정
    chrome_options.add_argument("--lang=ko-KR")
    
    # GitHub Actions 환경에서 실행
    try:
        from selenium.webdriver.chrome.service import Service
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.set_page_load_timeout(60)
        driver.implicitly_wait(10)
    except Exception as e:
        print(f"Chrome WebDriver 초기화 실패: {e}")
        raise
    
    return driver

def capture_game_review(driver, app_id, game_name, save_dir, logger):
    """게임 리뷰 섹션 캡처"""
    url = f"https://play.google.com/store/apps/details?id={app_id}&hl=ko"
    
    try:
        logger.info(f"캡처 시작: {game_name}")
        driver.get(url)
        time.sleep(10)  # 페이지 로딩 대기
        
        # 리뷰 섹션 찾기
        wait = WebDriverWait(driver, 20)
        review_section = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-testid='reviews-section']"))
        )
        
        # 스크롤하여 리뷰 섹션 확장
        driver.execute_script("arguments[0].scrollIntoView();", review_section)
        time.sleep(3)
        
        # 리뷰 섹션 캡처
        screenshot = driver.get_screenshot_as_png()
        img = Image.open(io.BytesIO(screenshot))
        
        # 리뷰 섹션 위치 계산 (대략적인 위치)
        window_height = driver.execute_script("return window.innerHeight;")
        review_y = review_section.location['y']
        
        # 리뷰 섹션만 크롭
        crop_box = (0, max(0, review_y - 100), 1920, min(img.height, review_y + 800))
        cropped_img = img.crop(crop_box)
        
        # 저장
        filename = f"{game_name}_{datetime.datetime.now().strftime('%Y%m%d')}.png"
        filepath = os.path.join(save_dir, filename)
        cropped_img.save(filepath, "PNG")
        
        logger.info(f"캡처 완료: {filepath}")
        return True
        
    except Exception as e:
        logger.error(f"캡처 실패 {game_name}: {e}")
        return False

def main():
    """메인 실행 함수"""
    logger = setup_logging()
    logger.info("GitHub Actions 캡처 시작")
    
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
        
    except Exception as e:
        logger.error(f"실행 중 오류 발생: {e}")
        raise
    finally:
        if driver:
            driver.quit()
            logger.info("WebDriver 종료")

if __name__ == "__main__":
    main()

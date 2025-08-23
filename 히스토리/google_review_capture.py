#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
모든 게임 리뷰 캡처하는 테스트 스크립트 (Firefox WebDriver 사용)
"""

import os
import datetime
import logging
import io
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from PIL import Image
import time

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

# 로깅 설정
def setup_logging():
    """로깅 설정"""
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    
    log_file = os.path.join(log_dir, f"test_all_games_firefox_{datetime.datetime.now().strftime('%Y%m%d')}.log")
    
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
    """Firefox WebDriver 설정"""
    firefox_options = Options()
    firefox_options.add_argument("--width=1920")
    firefox_options.add_argument("--height=1080")
    firefox_options.set_preference("dom.webdriver.enabled", False)
    firefox_options.set_preference("useAutomationExtension", False)
    firefox_options.set_preference("general.useragent.override", "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0")
    
    # 한국어 설정 추가
    firefox_options.set_preference("intl.accept_languages", "ko-KR,ko;q=0.9,en;q=0.8")
    firefox_options.set_preference("general.useragent.locale", "ko-KR")
    
    return webdriver.Firefox(options=firefox_options)

def capture_game_review_firefox(driver, app_id, game_name, save_dir, logger):
    """게임 리뷰 섹션 캡처 (Firefox 사용)"""
    url = f"https://play.google.com/store/apps/details?id={app_id}"
    
    try:
        logger.info(f"캡처 시작: {game_name} ({url})")
        driver.get(url)
        time.sleep(8)  # 페이지 로딩 대기 시간 증가
        
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
        
        # 캡처 영역 계산 (시작 요소부터 끝 요소까지, 너비 1200px로 고정)
        crop_left = max(0, start_location['x'])
        crop_top = max(0, start_location['y'] - 20)  # 시작 요소 위쪽 20px 여유
        crop_right = min(img.width, start_location['x'] + 1200)  # 너비를 1200px로 고정
        crop_bottom = min(img.height, end_location['y'] + end_size['height'] + 30)  # 끝 요소 아래쪽 30px 여유
        
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
        logger.error(f"캡처 실패 ({game_name}): {e}")
        return False

def main():
    """메인 실행 함수"""
    # 로깅 설정
    logger = setup_logging()
    
    base_dir = "D:\\aos review"
    save_dir = os.path.join(base_dir, "20250823")
    
    # 오늘 날짜
    today = datetime.datetime.now().strftime('%Y%m%d')
    
    logger.info("=" * 50)
    logger.info("모든 게임 리뷰 캡처 테스트 (Firefox) 시작")
    logger.info(f"캡처 날짜: {today}")
    logger.info(f"저장 폴더: {save_dir}")
    logger.info(f"캡처할 게임 수: {len(GAMES)}개")
    logger.info("=" * 50)
    
    # 폴더 생성
    os.makedirs(save_dir, exist_ok=True)
    logger.info(f"저장 폴더 생성: {save_dir}")
    
    # WebDriver 설정
    try:
        driver = setup_driver()
        logger.info("Firefox WebDriver 초기화 성공")
    except Exception as e:
        logger.error(f"Firefox WebDriver 초기화 실패: {e}")
        return False
    
    try:
        # 모든 게임 캡처
        success_count = 0
        
        for app_id, game_name in GAMES.items():
            logger.info(f"게임 캡처 시작: {game_name} ({app_id})")
            
            if capture_game_review_firefox(driver, app_id, game_name, save_dir, logger):
                logger.info(f"{game_name} Firefox 캡처 성공!")
                success_count += 1
            else:
                logger.error(f"{game_name} Firefox 캡처 실패")
            
            logger.info("=" * 50)
        
        logger.info("=" * 50)
        if success_count == len(GAMES):
            logger.info("모든 게임 Firefox 캡처 성공!")
            logger.info("=" * 50)
            return True
        elif success_count > 0:
            logger.info(f"{success_count}/{len(GAMES)} 게임 Firefox 캡처 성공!")
            logger.info("=" * 50)
            return True
        else:
            logger.error("모든 게임 Firefox 캡처 실패")
            logger.info("=" * 50)
            return False
    
    except Exception as e:
        logger.error(f"예상치 못한 오류 발생: {e}")
        return False
    
    finally:
        try:
            driver.quit()
            logger.info("Firefox WebDriver 종료")
        except:
            pass

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)

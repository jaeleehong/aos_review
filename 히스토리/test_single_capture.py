#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
뉴맞고 1개만 캡처하는 테스트 스크립트
"""

import os
import datetime
import logging
import io
import time
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from PIL import Image

def setup_logging():
    """로깅 설정"""
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    
    log_file = os.path.join(log_dir, f"test_single_capture_{datetime.datetime.now().strftime('%Y%m%d')}.log")
    
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
    
    # 헤드리스 모드 설정 (백그라운드 실행)
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
    firefox_options.set_preference("general.useragent.override", "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0")
    
    # 한국어 설정 추가
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
    
    return webdriver.Firefox(options=firefox_options)

def capture_newmatgo_review(driver, logger):
    """뉴맞고 리뷰 섹션 캡처"""
    url = "https://play.google.com/store/apps/details?id=com.neowiz.games.newmatgo"
    
    try:
        logger.info(f"캡처 시작: NewMatgo ({url})")
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
        logger.info(f"기본 리뷰 섹션 캡처 시작: NewMatgo (버튼 클릭 없음)")
        
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
        logger.info(f"시작 요소로 스크롤: NewMatgo")
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'start'});", start_element)
        time.sleep(3)  # 스크롤 완료 대기
        
        # 전체 페이지 높이 설정
        logger.info("전체 페이지 높이 설정")
        total_height = driver.execute_script("return document.body.scrollHeight")
        driver.set_window_size(1920, total_height)
        time.sleep(2)
        
        # 스크린샷 촬영
        logger.info(f"전체 페이지 스크린샷 촬영: NewMatgo")
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
        
        # 캡처 영역 계산 (평점 및 리뷰 섹션에서 리뷰 모두 보기 버튼까지)
        crop_left = max(0, start_location['x'])
        crop_top = max(0, start_location['y'] - 50)  # 시작 요소 위쪽 50px 여유 (평점 정보 포함)
        crop_right = min(img.width, start_location['x'] + 900)  # 너비를 900px로 조정 (여백 더 줄이기)
        crop_bottom = min(img.height, end_location['y'])  # 리뷰 모두 보기 버튼 위까지만 캡처
        
        logger.info(f"최종 크롭 영역: left={crop_left}, top={crop_top}, right={crop_right}, bottom={crop_bottom}")
        
        # 크롭 및 저장
        if crop_right > crop_left and crop_bottom > crop_top:
            cropped_img = img.crop((crop_left, crop_top, crop_right, crop_bottom))
        else:
            logger.warning(f"크롭 영역이 유효하지 않습니다. 전체 화면을 캡처합니다.")
            cropped_img = img
        
        # 파일 저장
        filename = f"NewMatgo_test_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        filepath = filename
        cropped_img.save(filepath)
        
        logger.info(f"캡처 완료: {filename} (크기: {cropped_img.width} x {cropped_img.height})")
        logger.info(f"파일 저장 위치: {os.path.abspath(filepath)}")
        return True
        
    except Exception as e:
        logger.error(f"캡처 실패 (NewMatgo): {e}")
        return False

def main():
    """메인 실행 함수"""
    logger = setup_logging()
    logger.info("뉴맞고 리뷰 캡처 테스트 시작")
    
    driver = None
    try:
        driver = setup_driver()
        logger.info("Firefox WebDriver 초기화 완료")
        
        if capture_newmatgo_review(driver, logger):
            logger.info("뉴맞고 캡처 성공!")
        else:
            logger.error("뉴맞고 캡처 실패!")
        
    except Exception as e:
        logger.error(f"실행 중 오류 발생: {e}")
        raise
    finally:
        if driver:
            driver.quit()
            logger.info("WebDriver 종료")

if __name__ == "__main__":
    main()

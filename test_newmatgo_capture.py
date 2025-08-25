#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
뉴맞고만 테스트로 캡처하는 스크립트
"""

import os
import datetime
import logging
import io
import subprocess
import sys
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from PIL import Image
import time
from bs4 import BeautifulSoup
import re

# 뉴맞고 게임 정보만 정의
GAMES = {
    "com.neowiz.games.newmatgo": "NewMatgo"
}

def setup_logging():
    """로깅 설정"""
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    
    log_file = os.path.join(log_dir, f"test_newmatgo_{datetime.datetime.now().strftime('%Y%m%d')}.log")
    
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
    firefox_options.add_argument("--height=1200")  # 높이를 늘려서 더 많은 내용 표시
    firefox_options.add_argument("--headless")  # 헤드리스 모드 활성화 (백그라운드 실행)
    firefox_options.set_preference("dom.webdriver.enabled", False)
    firefox_options.set_preference("useAutomationExtension", False)
    firefox_options.set_preference("general.useragent.override", "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0")
    
    # 한국어 설정 추가
    firefox_options.set_preference("intl.accept_languages", "ko-KR,ko;q=0.9,en;q=0.8")
    firefox_options.set_preference("general.useragent.locale", "ko-KR")
    
    # 추가 설정으로 더 정확한 렌더링 보장
    firefox_options.set_preference("layout.css.devPixelsPerPx", "1.0")  # 픽셀 밀도 설정
    firefox_options.set_preference("browser.cache.disk.enable", False)  # 캐시 비활성화
    firefox_options.set_preference("browser.cache.memory.enable", False)  # 메모리 캐시 비활성화
    
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
        
        # 화면 크기 최적화를 위한 동적 조정
        logger.info("화면 크기 최적화 시작")
        try:
            # 현재 창 크기 확인
            current_size = driver.get_window_size()
            logger.info(f"현재 창 크기: {current_size['width']} x {current_size['height']}")
            
            # 페이지 내용에 맞게 창 크기 조정
            driver.set_window_size(1920, 1200)
            time.sleep(2)
            
            # 페이지가 완전히 로드될 때까지 대기
            WebDriverWait(driver, 10).until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )
            
            logger.info("화면 크기 최적화 완료")
        except Exception as e:
            logger.warning(f"화면 크기 최적화 실패: {e}")
        
        # "리뷰 모두 보기" 버튼을 클릭하지 않고 기본 리뷰 섹션만 캡처
        logger.info(f"기본 리뷰 섹션 캡처 시작: {game_name} (버튼 클릭 없음)")
        
        # 시작 요소 찾기 ("평점 및 리뷰" 제목 - 분석된 정확한 선택자 사용)
        start_element = None
        start_element_selectors = [
            "//h2[contains(text(), '평점 및 리뷰')]",
            ".XfZNbf",
            "//h2[text()='평점 및 리뷰']",
            "//div[contains(text(), '평점 및 리뷰')]",
            "//span[contains(text(), '평점 및 리뷰')]"
        ]
        
        for i, selector in enumerate(start_element_selectors):
            try:
                if selector.startswith("."):
                    # CSS 선택자 사용
                    start_element = driver.find_element(By.CSS_SELECTOR, selector)
                    logger.info(f"시작 요소 찾기 성공: CSS 선택자 {i+1}: {selector}")
                else:
                    # XPath 선택자 사용
                    start_element = driver.find_element(By.XPATH, selector)
                    logger.info(f"시작 요소 찾기 성공: XPath 선택자 {i+1}: {selector}")
                break
            except Exception as e:
                logger.debug(f"시작 요소 선택자 {i+1} 실패: {selector} - {e}")
                continue
        
        if start_element is None:
            logger.error(f"시작 요소를 찾을 수 없습니다: '평점 및 리뷰'")
            return False
        
        # 끝 요소 찾기 ("리뷰 모두 보기" 버튼 - 분석된 정확한 선택자 사용)
        end_element = None
        end_element_selectors = [
            "//span[contains(text(), '리뷰 모두 보기')]",
            ".VfPpkd-vQzf8d",
            ".Jwxk6d button span",
            "//span[@class='VfPpkd-vQzf8d']",
            "//button[contains(text(), '리뷰 모두 보기')]",
            "//div[contains(text(), '리뷰 모두 보기')]"
        ]
        
        for i, selector in enumerate(end_element_selectors):
            try:
                if selector.startswith("."):
                    # CSS 선택자 사용
                    end_element = driver.find_element(By.CSS_SELECTOR, selector)
                    logger.info(f"끝 요소 찾기 성공: CSS 선택자 {i+1}: {selector}")
                else:
                    # XPath 선택자 사용
                    end_element = driver.find_element(By.XPATH, selector)
                    logger.info(f"끝 요소 찾기 성공: XPath 선택자 {i+1}: {selector}")
                break
            except Exception as e:
                logger.debug(f"끝 요소 선택자 {i+1} 실패: {selector} - {e}")
                continue
        
        if end_element is None:
            logger.warning(f"끝 요소를 찾을 수 없습니다. 기본 높이로 캡처합니다.")
            # 끝 요소를 찾지 못한 경우, 시작 요소에서 2000px 아래로 캡처
            start_location = start_element.location
            end_location = {'y': start_location['y'] + 2000}
            end_size = {'height': 0}
        else:
            end_location = end_element.location
            end_size = end_element.size
        
        # 시작 요소로 스크롤
        logger.info(f"시작 요소로 스크롤: {game_name}")
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'start'});", start_element)
        time.sleep(3)  # 스크롤 완료 대기
        
        # 더 많은 리뷰를 보기 위해 추가 스크롤
        logger.info("추가 리뷰 로드를 위한 스크롤 시작")
        for i in range(3):  # 3번 스크롤하여 더 많은 리뷰 로드
            driver.execute_script("window.scrollBy(0, 800);")
            time.sleep(2)  # 각 스크롤 후 대기
            logger.info(f"추가 스크롤 {i+1}/3 완료")
        
        # 전체 페이지 높이 설정 (전체 화면 캡처)
        logger.info("전체 페이지 높이 설정")
        total_height = driver.execute_script("return document.body.scrollHeight")
        logger.info(f"전체 페이지 높이: {total_height}px")
        
        # 전체 화면 크기로 설정
        driver.set_window_size(1920, total_height)
        time.sleep(3)  # 크기 변경 후 안정화 대기
        
        # 페이지가 완전히 렌더링될 때까지 대기
        WebDriverWait(driver, 10).until(
            lambda driver: driver.execute_script("return document.readyState") == "complete"
        )
        
        # 추가로 스크롤하여 모든 콘텐츠가 로드되도록 함
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(1)
        
        # 스크린샷 촬영
        logger.info(f"전체 페이지 스크린샷 촬영: {game_name}")
        screenshot = driver.get_screenshot_as_png()
        img = Image.open(io.BytesIO(screenshot))
        
        logger.info(f"전체 스크린샷 크기: {img.width} x {img.height}")
        
        # 시작 요소와 끝 요소 위치 정보 가져오기
        start_location = start_element.location
        start_size = start_element.size
        
        logger.info(f"시작 요소 위치: x={start_location['x']}, y={start_location['y']}")
        logger.info(f"시작 요소 크기: width={start_size['width']}, height={start_size['height']}")
        logger.info(f"끝 요소 위치: x={end_location['x']}, y={end_location['y']}")
        logger.info(f"끝 요소 크기: width={end_size['width']}, height={end_size['height']}")
        
        # 캡처 영역 파악을 위한 상세 정보 출력
        logger.info("=" * 50)
        logger.info("캡처 영역 파악 정보:")
        logger.info(f"전체 이미지 크기: {img.width} x {img.height}")
        logger.info(f"시작 요소: x={start_location['x']}, y={start_location['y']}, w={start_size['width']}, h={start_size['height']}")
        logger.info(f"끝 요소: x={end_location['x']}, y={end_location['y']}, w={end_size['width']}, h={end_size['height']}")
        logger.info(f"리뷰 섹션 높이: {end_location['y'] - start_location['y']}px")
        logger.info("=" * 50)
        
        # 캡처 영역 계산 (고정 크기: 1000 x 1800 - 우측 사이드바 제외)
        crop_width = 1000  # 너비를 1000px로 설정 (우측 사이드바 제외)
        crop_left = max(0, start_location['x'] - 100)  # 시작 요소에서 왼쪽으로 100px 여백
        
        # 시작 요소가 "평점 및 리뷰" 제목인지 확인하고 적절한 여백 설정
        if "평점" in start_element.text or "리뷰" in start_element.text:
            crop_top = max(0, start_location['y'] - 100)  # "평점 및 리뷰" 제목 위쪽 100px 여유
        else:
            crop_top = max(0, start_location['y'] - 200)  # 다른 요소인 경우 여백
            
        crop_right = min(img.width, crop_left + crop_width)  # 조정된 너비 적용
        
        # 고정 높이 1800px로 설정
        crop_bottom = min(img.height, crop_top + 1800)  # 시작점에서 1800px 아래까지
        
        # 최소 캡처 높이 보장
        min_height = 1800
        if crop_bottom - crop_top < min_height:
            crop_bottom = min(img.height, crop_top + min_height)
        
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
    
    base_dir = os.getcwd()  # 현재 작업 디렉토리 사용
    today = datetime.datetime.now().strftime('%Y%m%d')
    save_dir = os.path.join(base_dir, today)
    
    logger.info("=" * 50)
    logger.info("뉴맞고 테스트 캡처 시작")
    logger.info(f"실행 날짜: {today}")
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
        # 뉴맞고만 캡처
        success_count = 0
        
        for app_id, game_name in GAMES.items():
            logger.info(f"게임 캡처 시작: {game_name} ({app_id})")
            
            if capture_game_review_firefox(driver, app_id, game_name, save_dir, logger):
                logger.info(f"{game_name} 캡처 성공!")
                success_count += 1
            else:
                logger.error(f"{game_name} 캡처 실패")
            
            logger.info("=" * 50)
        
        logger.info("=" * 50)
        if success_count == len(GAMES):
            logger.info("뉴맞고 캡처 성공!")
            logger.info("=" * 50)
            return True
        else:
            logger.error("뉴맞고 캡처 실패")
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

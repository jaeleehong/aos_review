#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
구글 플레이 스토어 뉴맞고 페이지 구조 분석
"""

import os
import datetime
import logging
import time
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def setup_logging():
    """로깅 설정"""
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    
    log_file = os.path.join(log_dir, f"analyze_newmatgo_{datetime.datetime.now().strftime('%Y%m%d')}.log")
    
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
    
    # 브라우저 설정
    firefox_options.set_preference("dom.webdriver.enabled", False)
    firefox_options.set_preference("useAutomationExtension", False)
    firefox_options.set_preference("general.useragent.override", "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0")
    
    # 한국어 설정 추가
    firefox_options.set_preference("intl.accept_languages", "ko-KR,ko;q=0.9,en;q=0.8")
    firefox_options.set_preference("general.useragent.locale", "ko-KR")
    
    return webdriver.Firefox(options=firefox_options)

def analyze_newmatgo_page(driver, logger):
    """뉴맞고 페이지 구조 분석"""
    url = "https://play.google.com/store/apps/details?id=com.neowiz.games.newmatgo"
    
    try:
        logger.info(f"뉴맞고 페이지 분석 시작: {url}")
        driver.get(url)
        time.sleep(8)  # 페이지 로딩 대기
        
        # 한국어 URL로 리다이렉트 시도
        current_url = driver.current_url
        if 'hl=ko' not in current_url:
            korean_url = current_url + ('&' if '?' in current_url else '?') + 'hl=ko'
            logger.info(f"한국어 URL로 리다이렉트: {korean_url}")
            driver.get(korean_url)
            time.sleep(3)
        
        logger.info("=== 페이지 기본 정보 ===")
        logger.info(f"현재 URL: {driver.current_url}")
        logger.info(f"페이지 제목: {driver.title}")
        
        # 페이지 높이 확인
        total_height = driver.execute_script("return document.body.scrollHeight")
        logger.info(f"전체 페이지 높이: {total_height}px")
        
        logger.info("\n=== 평점 및 리뷰 섹션 분석 ===")
        
        # 평점 및 리뷰 섹션 찾기
        review_section_selectors = [
            "//h2[text()='평점 및 리뷰']",
            "//h2[contains(text(), '평점')]",
            "//h2[contains(text(), '리뷰')]",
            "//div[contains(text(), '평점 및 리뷰')]",
            "//span[contains(text(), '평점 및 리뷰')]"
        ]
        
        review_section = None
        for i, selector in enumerate(review_section_selectors):
            try:
                review_section = driver.find_element(By.XPATH, selector)
                logger.info(f"평점 및 리뷰 섹션 찾기 성공 (선택자 {i+1}: {selector})")
                break
            except Exception as e:
                logger.debug(f"평점 및 리뷰 섹션 선택자 {i+1} 실패: {selector} - {e}")
                continue
        
        if review_section:
            location = review_section.location
            size = review_section.size
            logger.info(f"평점 및 리뷰 섹션 위치: x={location['x']}, y={location['y']}")
            logger.info(f"평점 및 리뷰 섹션 크기: width={size['width']}, height={size['height']}")
            logger.info(f"평점 및 리뷰 섹션 텍스트: {review_section.text}")
        
        # 평점 정보 찾기
        logger.info("\n=== 평점 정보 분석 ===")
        rating_selectors = [
            "//div[contains(@class, 'rating')]",
            "//div[contains(@class, 'score')]",
            "//span[contains(@class, 'rating')]",
            "//div[contains(text(), '점')]"
        ]
        
        for i, selector in enumerate(rating_selectors):
            try:
                elements = driver.find_elements(By.XPATH, selector)
                if elements:
                    logger.info(f"평점 관련 요소 {i+1} 발견: {selector}")
                    for j, elem in enumerate(elements[:3]):  # 처음 3개만
                        logger.info(f"  - 요소 {j+1}: {elem.text[:100]}...")
            except Exception as e:
                logger.debug(f"평점 선택자 {i+1} 실패: {selector} - {e}")
        
        # 리뷰 개수 정보 찾기
        logger.info("\n=== 리뷰 개수 정보 분석 ===")
        review_count_selectors = [
            "//div[contains(text(), '리뷰')]",
            "//span[contains(text(), '리뷰')]",
            "//div[contains(text(), '만개')]",
            "//span[contains(text(), '만개')]"
        ]
        
        for i, selector in enumerate(review_count_selectors):
            try:
                elements = driver.find_elements(By.XPATH, selector)
                if elements:
                    logger.info(f"리뷰 개수 관련 요소 {i+1} 발견: {selector}")
                    for j, elem in enumerate(elements[:5]):  # 처음 5개만
                        text = elem.text.strip()
                        if text and len(text) < 50:  # 짧은 텍스트만
                            logger.info(f"  - 요소 {j+1}: '{text}'")
            except Exception as e:
                logger.debug(f"리뷰 개수 선택자 {i+1} 실패: {selector} - {e}")
        
        # 개별 리뷰 찾기
        logger.info("\n=== 개별 리뷰 분석 ===")
        review_selectors = [
            "//div[@data-review-id]",
            "//div[contains(@class, 'review')]",
            "//div[@role='article']",
            "//div[contains(@class, 'single-review')]"
        ]
        
        for i, selector in enumerate(review_selectors):
            try:
                reviews = driver.find_elements(By.XPATH, selector)
                if reviews:
                    logger.info(f"리뷰 요소 {i+1} 발견: {selector} - {len(reviews)}개")
                    for j, review in enumerate(reviews[:3]):  # 처음 3개만
                        location = review.location
                        size = review.size
                        logger.info(f"  - 리뷰 {j+1}: 위치(x={location['x']}, y={location['y']}), 크기({size['width']}x{size['height']})")
            except Exception as e:
                logger.debug(f"리뷰 선택자 {i+1} 실패: {selector} - {e}")
        
        # 리뷰 모두 보기 버튼 찾기
        logger.info("\n=== 리뷰 모두 보기 버튼 분석 ===")
        show_all_selectors = [
            "//div[@role='button']//span[text()='리뷰 모두 보기']",
            "//span[text()='리뷰 모두 보기']",
            "//div[contains(text(), '리뷰 모두 보기')]",
            "//button[contains(text(), '리뷰 모두 보기')]",
            "//a[contains(text(), '리뷰 모두 보기')]"
        ]
        
        for i, selector in enumerate(show_all_selectors):
            try:
                elements = driver.find_elements(By.XPATH, selector)
                if elements:
                    logger.info(f"리뷰 모두 보기 버튼 {i+1} 발견: {selector}")
                    for j, elem in enumerate(elements):
                        location = elem.location
                        size = elem.size
                        logger.info(f"  - 버튼 {j+1}: 위치(x={location['x']}, y={location['y']}), 크기({size['width']}x{size['height']})")
                        logger.info(f"  - 버튼 텍스트: '{elem.text}'")
            except Exception as e:
                logger.debug(f"리뷰 모두 보기 선택자 {i+1} 실패: {selector} - {e}")
        
        # 새로운 기능 섹션 찾기
        logger.info("\n=== 새로운 기능 섹션 분석 ===")
        new_features_selectors = [
            "//div[contains(text(), '새로운 기능')]",
            "//h2[contains(text(), '새로운 기능')]",
            "//div[contains(text(), 'What')]",
            "//div[contains(text(), 'New')]"
        ]
        
        for i, selector in enumerate(new_features_selectors):
            try:
                elements = driver.find_elements(By.XPATH, selector)
                if elements:
                    logger.info(f"새로운 기능 섹션 {i+1} 발견: {selector}")
                    for j, elem in enumerate(elements):
                        location = elem.location
                        logger.info(f"  - 섹션 {j+1}: 위치(x={location['x']}, y={location['y']})")
                        logger.info(f"  - 섹션 텍스트: '{elem.text[:100]}...'")
            except Exception as e:
                logger.debug(f"새로운 기능 선택자 {i+1} 실패: {selector} - {e}")
        
        # 부적절한 앱 신고 버튼 찾기
        logger.info("\n=== 부적절한 앱 신고 버튼 분석 ===")
        report_selectors = [
            "//div[contains(text(), '부적절한 앱')]",
            "//span[contains(text(), '부적절한 앱')]",
            "//button[contains(text(), '신고')]",
            "//a[contains(text(), '신고')]"
        ]
        
        for i, selector in enumerate(report_selectors):
            try:
                elements = driver.find_elements(By.XPATH, selector)
                if elements:
                    logger.info(f"신고 버튼 {i+1} 발견: {selector}")
                    for j, elem in enumerate(elements):
                        location = elem.location
                        logger.info(f"  - 버튼 {j+1}: 위치(x={location['x']}, y={location['y']})")
                        logger.info(f"  - 버튼 텍스트: '{elem.text}'")
            except Exception as e:
                logger.debug(f"신고 버튼 선택자 {i+1} 실패: {selector} - {e}")
        
        logger.info("\n=== 페이지 분석 완료 ===")
        return True
        
    except Exception as e:
        logger.error(f"페이지 분석 실패: {e}")
        return False

def main():
    """메인 실행 함수"""
    logger = setup_logging()
    logger.info("구글 플레이 스토어 뉴맞고 페이지 분석 시작")
    
    driver = None
    try:
        driver = setup_driver()
        logger.info("Firefox WebDriver 초기화 완료")
        
        if analyze_newmatgo_page(driver, logger):
            logger.info("뉴맞고 페이지 분석 성공!")
        else:
            logger.error("뉴맞고 페이지 분석 실패!")
        
    except Exception as e:
        logger.error(f"실행 중 오류 발생: {e}")
        raise
    finally:
        if driver:
            driver.quit()
            logger.info("WebDriver 종료")

if __name__ == "__main__":
    main()

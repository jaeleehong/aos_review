#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
페이지 구조 분석 스크립트
"""

import os
import sys
import time
import datetime
import logging
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def setup_logging():
    """로깅 설정"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(f'logs/analyze_page_{datetime.datetime.now().strftime("%Y%m%d")}.log', encoding='utf-8')
        ]
    )
    return logging.getLogger(__name__)

def setup_driver():
    """Firefox WebDriver 설정"""
    firefox_options = Options()
    firefox_options.add_argument("--width=1920")
    firefox_options.add_argument("--height=1080")
    # firefox_options.add_argument("--headless")  # 헤드리스 모드 비활성화 (페이지 분석용)
    firefox_options.set_preference("dom.webdriver.enabled", False)
    firefox_options.set_preference("useAutomationExtension", False)
    firefox_options.set_preference("general.useragent.override", "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0")
    
    driver = webdriver.Firefox(options=firefox_options)
    driver.implicitly_wait(10)
    return driver

def analyze_page_structure(driver, app_id, logger):
    """페이지 구조 분석"""
    try:
        url = f"https://play.google.com/store/apps/details?id={app_id}"
        logger.info(f"페이지 분석 시작: {url}")
        
        driver.get(url)
        time.sleep(5)
        
        # 한국어 설정
        try:
            korean_url = f"{url}&hl=ko"
            driver.get(korean_url)
            time.sleep(3)
            logger.info("한국어 설정 적용")
        except Exception as e:
            logger.warning(f"한국어 설정 실패: {e}")
        
        # 페이지 높이 확인
        total_height = driver.execute_script("return document.body.scrollHeight")
        logger.info(f"전체 페이지 높이: {total_height}")
        
        # 리뷰 관련 요소들 찾기
        logger.info("=" * 50)
        logger.info("리뷰 관련 요소 분석")
        logger.info("=" * 50)
        
        # 1. 전체 평점 요소 찾기
        rating_selectors = [
            "//div[contains(text(), '평점')]",
            "//span[contains(text(), '평점')]",
            "//h1[contains(text(), '평점')]",
            "//div[contains(@class, 'rating')]"
        ]
        
        for i, selector in enumerate(rating_selectors):
            try:
                elements = driver.find_elements(By.XPATH, selector)
                for j, element in enumerate(elements):
                    location = element.location
                    size = element.size
                    text = element.text[:50] if element.text else "텍스트 없음"
                    logger.info(f"평점 요소 {i+1}-{j+1}: {selector}")
                    logger.info(f"  위치: x={location['x']}, y={location['y']}")
                    logger.info(f"  크기: width={size['width']}, height={size['height']}")
                    logger.info(f"  텍스트: {text}")
            except Exception as e:
                logger.debug(f"평점 요소 {i+1} 실패: {e}")
        
        # 2. 리뷰 수 요소 찾기
        review_count_selectors = [
            "//div[contains(text(), '리뷰') and contains(text(), '만개')]",
            "//span[contains(text(), '리뷰') and contains(text(), '만개')]",
            "//div[contains(text(), '리뷰')]",
            "//span[contains(text(), '리뷰')]"
        ]
        
        for i, selector in enumerate(review_count_selectors):
            try:
                elements = driver.find_elements(By.XPATH, selector)
                for j, element in enumerate(elements):
                    location = element.location
                    size = element.size
                    text = element.text[:50] if element.text else "텍스트 없음"
                    logger.info(f"리뷰 수 요소 {i+1}-{j+1}: {selector}")
                    logger.info(f"  위치: x={location['x']}, y={location['y']}")
                    logger.info(f"  크기: width={size['width']}, height={size['height']}")
                    logger.info(f"  텍스트: {text}")
            except Exception as e:
                logger.debug(f"리뷰 수 요소 {i+1} 실패: {e}")
        
        # 3. 별점 분포 그래프 찾기
        chart_selectors = [
            "//div[contains(@class, 'chart')]",
            "//div[contains(@class, 'bar')]",
            "//div[contains(@class, 'rating')]//div[contains(@class, 'bar')]",
            "//div[@role='progressbar']"
        ]
        
        for i, selector in enumerate(chart_selectors):
            try:
                elements = driver.find_elements(By.XPATH, selector)
                for j, element in enumerate(elements):
                    location = element.location
                    size = element.size
                    logger.info(f"차트 요소 {i+1}-{j+1}: {selector}")
                    logger.info(f"  위치: x={location['x']}, y={location['y']}")
                    logger.info(f"  크기: width={size['width']}, height={size['height']}")
            except Exception as e:
                logger.debug(f"차트 요소 {i+1} 실패: {e}")
        
        # 4. 개별 리뷰 요소 찾기
        review_selectors = [
            "//div[contains(@class, 'review')]",
            "//div[contains(@class, 'comment')]",
            "//div[@data-review-id]",
            "//div[contains(@class, 'g1rdde')]"
        ]
        
        for i, selector in enumerate(review_selectors):
            try:
                elements = driver.find_elements(By.XPATH, selector)
                logger.info(f"리뷰 요소 {i+1}: {selector} - {len(elements)}개 발견")
                for j, element in enumerate(elements[:3]):  # 처음 3개만
                    location = element.location
                    size = element.size
                    logger.info(f"  리뷰 {j+1}: x={location['x']}, y={location['y']}, w={size['width']}, h={size['height']}")
            except Exception as e:
                logger.debug(f"리뷰 요소 {i+1} 실패: {e}")
        
        # 5. "리뷰 모두 보기" 버튼 찾기
        button_selectors = [
            "//div[@role='button']//span[text()='리뷰 모두 보기']",
            "//span[text()='리뷰 모두 보기']",
            "//div[contains(text(), '리뷰 모두 보기')]",
            "//button[contains(text(), '리뷰 모두 보기')]"
        ]
        
        for i, selector in enumerate(button_selectors):
            try:
                elements = driver.find_elements(By.XPATH, selector)
                for j, element in enumerate(elements):
                    location = element.location
                    size = element.size
                    text = element.text[:50] if element.text else "텍스트 없음"
                    logger.info(f"버튼 요소 {i+1}-{j+1}: {selector}")
                    logger.info(f"  위치: x={location['x']}, y={location['y']}")
                    logger.info(f"  크기: width={size['width']}, height={size['height']}")
                    logger.info(f"  텍스트: {text}")
            except Exception as e:
                logger.debug(f"버튼 요소 {i+1} 실패: {e}")
        
        # 6. 전체 리뷰 섹션의 경계 찾기
        logger.info("=" * 50)
        logger.info("전체 리뷰 섹션 경계 분석")
        logger.info("=" * 50)
        
        # 페이지의 모든 div 요소들의 위치 정보 수집
        all_divs = driver.find_elements(By.TAG_NAME, "div")
        review_related_divs = []
        
        for div in all_divs:
            try:
                location = div.location
                size = div.size
                text = div.text[:30] if div.text else ""
                
                # 리뷰 관련 텍스트가 포함된 div 찾기
                if any(keyword in text.lower() for keyword in ['리뷰', '평점', '별점', '만개']):
                    review_related_divs.append({
                        'location': location,
                        'size': size,
                        'text': text
                    })
            except:
                continue
        
        # 위치별로 정렬
        review_related_divs.sort(key=lambda x: x['location']['y'])
        
        logger.info(f"리뷰 관련 div 요소 {len(review_related_divs)}개 발견:")
        for i, div in enumerate(review_related_divs[:10]):  # 처음 10개만
            logger.info(f"  {i+1}: y={div['location']['y']}, x={div['location']['x']}, w={div['size']['width']}, h={div['size']['height']}, text='{div['text']}'")
        
        return True
        
    except Exception as e:
        logger.error(f"페이지 분석 실패: {e}")
        return False

def main():
    """메인 실행 함수"""
    logger = setup_logging()
    
    app_id = 'com.neowiz.games.newmatgo'
    
    logger.info("=" * 50)
    logger.info("페이지 구조 분석 시작")
    logger.info(f"분석 대상: {app_id}")
    logger.info("=" * 50)
    
    try:
        driver = setup_driver()
        logger.info("Firefox WebDriver 초기화 성공")
        
        if analyze_page_structure(driver, app_id, logger):
            logger.info("페이지 분석 완료!")
        else:
            logger.error("페이지 분석 실패!")
            return False
        
        # 사용자가 수동으로 확인할 수 있도록 대기
        logger.info("페이지가 열렸습니다. 브라우저에서 페이지 구조를 확인하세요.")
        logger.info("분석이 완료되면 Enter를 눌러주세요...")
        input()
        
        return True
        
    except Exception as e:
        logger.error(f"분석 중 오류 발생: {e}")
        return False
    finally:
        driver.quit()
        logger.info("Firefox WebDriver 종료")

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
피망 뉴맞고 페이지에서 리뷰 영역을 찾는 확인 스크립트
"""

import os
import datetime
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# 로깅 설정
def setup_logging():
    """로깅 설정"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def setup_driver():
    """Chrome WebDriver 설정"""
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    # chrome_options.add_argument("--headless")  # 헤드리스 모드 비활성화 (화면 확인용)
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    return webdriver.Chrome(options=chrome_options)

def check_newmatgo_review_area(driver, logger):
    """뉴맞고 리뷰 영역 확인"""
    url = "https://play.google.com/store/apps/details?id=com.neowiz.games.newmatgo"
    
    try:
        logger.info(f"페이지 접속: {url}")
        driver.get(url)
        time.sleep(5)  # 페이지 로딩 대기
        
        logger.info("=" * 50)
        logger.info("리뷰 영역 찾기 시작")
        logger.info("=" * 50)
        
        # 1. 평점 섹션 찾기
        logger.info("1. 평점 섹션 찾기:")
        rating_selectors = [
            "//div[contains(@class, 'TTRhpd')]",
            "//div[contains(@class, 'jILTFe')]",
            "//div[contains(@class, 'VWIeTd')]",
            "//div[contains(@class, 'g1rdde')]",
            "//div[contains(@class, 'rating')]",
            "//div[contains(@class, 'score')]",
            "//div[contains(@class, 'stars')]",
        ]
        
        for i, selector in enumerate(rating_selectors):
            try:
                element = driver.find_element(By.XPATH, selector)
                location = element.location
                size = element.size
                text = element.text[:100] if element.text else "텍스트 없음"
                logger.info(f"  선택자 {i+1} 성공: {selector}")
                logger.info(f"    위치: x={location['x']}, y={location['y']}")
                logger.info(f"    크기: width={size['width']}, height={size['height']}")
                logger.info(f"    텍스트: {text}")
                break
            except Exception as e:
                logger.info(f"  선택자 {i+1} 실패: {selector}")
        
        # 2. 리뷰 섹션 찾기
        logger.info("\n2. 리뷰 섹션 찾기:")
        review_selectors = [
            "//div[contains(@class, 'Jwxk6d')]",
            "//div[contains(@class, 'Jwxk6d') and contains(@class, 'review')]",
            "//div[contains(@class, 'Jwxk6d') and contains(@class, 'rating')]",
            "//div[contains(@class, 'Jwxk6d') and contains(@class, 'reviews')]",
            "//div[contains(@class, 'review') and contains(@class, 'list')]",
            "//div[contains(@class, 'reviews') and contains(@class, 'list')]",
            "//div[contains(@class, 'review') and contains(@class, 'section')]",
            "//div[contains(@class, 'reviews') and contains(@class, 'section')]",
            "//div[contains(@class, 'bar') and contains(@class, 'chart')]",
            "//div[contains(@class, 'rating') and contains(@class, 'distribution')]",
            "//div[contains(@class, 'star') and contains(@class, 'distribution')]",
        ]
        
        for i, selector in enumerate(review_selectors):
            try:
                element = driver.find_element(By.XPATH, selector)
                location = element.location
                size = element.size
                text = element.text[:100] if element.text else "텍스트 없음"
                logger.info(f"  선택자 {i+1} 성공: {selector}")
                logger.info(f"    위치: x={location['x']}, y={location['y']}")
                logger.info(f"    크기: width={size['width']}, height={size['height']}")
                logger.info(f"    텍스트: {text}")
                break
            except Exception as e:
                logger.info(f"  선택자 {i+1} 실패: {selector}")
        
        # 3. 리뷰 모두 보기 버튼 찾기
        logger.info("\n3. 리뷰 모두 보기 버튼 찾기:")
        review_button_selectors = [
            "//span[contains(text(), '리뷰 모두 보기')]",
            "//button[contains(text(), '리뷰 모두 보기')]",
            "//a[contains(text(), '리뷰 모두 보기')]",
            "//div[contains(text(), '리뷰 모두 보기')]",
            "//span[contains(text(), '모든 리뷰 보기')]",
            "//button[contains(text(), '모든 리뷰 보기')]",
            "//a[contains(text(), '모든 리뷰 보기')]",
            "//div[contains(text(), '모든 리뷰 보기')]",
        ]
        
        for i, selector in enumerate(review_button_selectors):
            try:
                element = driver.find_element(By.XPATH, selector)
                location = element.location
                size = element.size
                text = element.text
                logger.info(f"  선택자 {i+1} 성공: {selector}")
                logger.info(f"    위치: x={location['x']}, y={location['y']}")
                logger.info(f"    크기: width={size['width']}, height={size['height']}")
                logger.info(f"    텍스트: {text}")
                break
            except Exception as e:
                logger.info(f"  선택자 {i+1} 실패: {selector}")
        
        # 4. 개별 리뷰 찾기
        logger.info("\n4. 개별 리뷰 찾기:")
        individual_review_selectors = [
            "//div[contains(@class, 'review')]",
            "//div[contains(@class, 'reviews')]",
            "//div[contains(text(), '박상염')]",
            "//div[contains(text(), '오덕인')]",
            "//div[contains(text(), '은민국')]",
        ]
        
        for i, selector in enumerate(individual_review_selectors):
            try:
                elements = driver.find_elements(By.XPATH, selector)
                logger.info(f"  선택자 {i+1} 성공: {selector} (찾은 요소 수: {len(elements)})")
                for j, element in enumerate(elements[:3]):  # 처음 3개만 확인
                    location = element.location
                    size = element.size
                    text = element.text[:50] if element.text else "텍스트 없음"
                    logger.info(f"    요소 {j+1}: 위치=({location['x']}, {location['y']}), 크기=({size['width']}, {size['height']}), 텍스트={text}")
                break
            except Exception as e:
                logger.info(f"  선택자 {i+1} 실패: {selector}")
        
        # 5. 페이지 소스에서 리뷰 관련 클래스 찾기
        logger.info("\n5. 페이지 소스에서 리뷰 관련 클래스 찾기:")
        page_source = driver.page_source
        review_classes = ['review', 'rating', 'star', 'Jwxk6d', 'TTRhpd', 'jILTFe', 'VWIeTd', 'g1rdde']
        
        for class_name in review_classes:
            count = page_source.count(f'class="{class_name}"')
            if count > 0:
                logger.info(f"  클래스 '{class_name}': {count}개 발견")
        
        logger.info("\n" + "=" * 50)
        logger.info("확인 완료! 브라우저 창을 확인해주세요.")
        logger.info("=" * 50)
        
        # 브라우저 창을 열어둔 상태로 대기
        input("엔터를 누르면 브라우저가 종료됩니다...")
        
        return True
        
    except Exception as e:
        logger.error(f"확인 중 오류 발생: {e}")
        return False

def main():
    """메인 실행 함수"""
    logger = setup_logging()
    
    logger.info("=" * 50)
    logger.info("피망 뉴맞고 리뷰 영역 확인 시작")
    logger.info("=" * 50)
    
    # WebDriver 설정
    try:
        driver = setup_driver()
        logger.info("Chrome WebDriver 초기화 성공")
    except Exception as e:
        logger.error(f"Chrome WebDriver 초기화 실패: {e}")
        return False
    
    try:
        # 뉴맞고 리뷰 영역 확인
        if check_newmatgo_review_area(driver, logger):
            logger.info("확인 완료!")
            return True
        else:
            logger.error("확인 실패")
            return False
    
    except Exception as e:
        logger.error(f"예상치 못한 오류 발생: {e}")
        return False
    
    finally:
        try:
            driver.quit()
            logger.info("Chrome WebDriver 종료")
        except:
            pass

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)

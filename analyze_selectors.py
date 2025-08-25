#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google Play Store 페이지에서 리뷰 섹션의 CSS 선택자와 XPath 추출
"""

import os
import datetime
import logging
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from bs4 import BeautifulSoup

def setup_logging():
    """로깅 설정"""
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    
    log_file = os.path.join(log_dir, f"analyze_selectors_{datetime.datetime.now().strftime('%Y%m%d')}.log")
    
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
    firefox_options.add_argument("--headless")
    firefox_options.set_preference("dom.webdriver.enabled", False)
    firefox_options.set_preference("useAutomationExtension", False)
    firefox_options.set_preference("general.useragent.override", "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0")
    
    # 한국어 설정
    firefox_options.set_preference("intl.accept_languages", "ko-KR,ko;q=0.9,en;q=0.8")
    firefox_options.set_preference("general.useragent.locale", "ko-KR")
    
    return webdriver.Firefox(options=firefox_options)

def generate_xpath(element):
    """요소의 XPath 생성"""
    if element.tag_name == "html":
        return "/html"
    
    parent = element.find_element(By.XPATH, "..")
    siblings = parent.find_elements(By.XPATH, f"{element.tag_name}")
    
    if len(siblings) == 1:
        return f"{generate_xpath(parent)}/{element.tag_name}"
    else:
        index = 1
        for sibling in siblings:
            if sibling == element:
                break
            index += 1
        return f"{generate_xpath(parent)}/{element.tag_name}[{index}]"

def analyze_selectors(driver, logger):
    """페이지에서 리뷰 관련 요소들의 선택자 분석"""
    url = "https://play.google.com/store/apps/details?id=com.neowiz.games.newmatgo&hl=ko"
    
    try:
        logger.info(f"페이지 로딩: {url}")
        driver.get(url)
        time.sleep(8)
        
        # 한국어 설정 적용
        logger.info("한국어 설정 적용")
        driver.execute_script("""
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
        
        logger.info("=" * 80)
        logger.info("리뷰 섹션 선택자 분석 시작")
        logger.info("=" * 80)
        
        # 1. "전화" 탭 요소 찾기
        logger.info("\n1. '전화' 탭 요소 분석:")
        phone_tab_selectors = [
            "//span[contains(text(), '전화')]",
            "//span[text()='전화']",
            "//div[contains(text(), '전화')]",
            "//span[@class='ypTNYd' and contains(text(), '전화')]",
            "//span[@jsname='ODzDMd' and contains(text(), '전화')]",
            ".ypTNYd",
            "//span[contains(@class, 'ypTNYd')]"
        ]
        
        for i, selector in enumerate(phone_tab_selectors):
            try:
                if selector.startswith("."):
                    element = driver.find_element(By.CSS_SELECTOR, selector)
                    logger.info(f"  CSS 선택자 {i+1}: {selector}")
                else:
                    element = driver.find_element(By.XPATH, selector)
                    logger.info(f"  XPath 선택자 {i+1}: {selector}")
                
                # 요소의 상세 정보 출력
                logger.info(f"    - 태그: {element.tag_name}")
                logger.info(f"    - 클래스: {element.get_attribute('class')}")
                logger.info(f"    - jsname: {element.get_attribute('jsname')}")
                logger.info(f"    - 텍스트: {element.text}")
                logger.info(f"    - 위치: x={element.location['x']}, y={element.location['y']}")
                logger.info(f"    - 크기: w={element.size['width']}, h={element.size['height']}")
                
                # 고유한 XPath 생성
                unique_xpath = generate_xpath(element)
                logger.info(f"    - 고유 XPath: {unique_xpath}")
                logger.info("")
                break
            except Exception as e:
                logger.debug(f"  선택자 {i+1} 실패: {selector} - {e}")
                continue
        
        # 2. "평점 및 리뷰" 제목 요소 찾기
        logger.info("\n2. '평점 및 리뷰' 제목 요소 분석:")
        review_title_selectors = [
            "//h2[contains(text(), '평점 및 리뷰')]",
            "//h2[text()='평점 및 리뷰']",
            "//div[contains(text(), '평점 및 리뷰')]",
            "//span[contains(text(), '평점 및 리뷰')]",
            "h2",
            ".qZmL0 h2"
        ]
        
        for i, selector in enumerate(review_title_selectors):
            try:
                if selector.startswith(".") or not selector.startswith("//"):
                    element = driver.find_element(By.CSS_SELECTOR, selector)
                    logger.info(f"  CSS 선택자 {i+1}: {selector}")
                else:
                    element = driver.find_element(By.XPATH, selector)
                    logger.info(f"  XPath 선택자 {i+1}: {selector}")
                
                if "평점" in element.text or "리뷰" in element.text:
                    logger.info(f"    - 태그: {element.tag_name}")
                    logger.info(f"    - 클래스: {element.get_attribute('class')}")
                    logger.info(f"    - 텍스트: {element.text}")
                    logger.info(f"    - 위치: x={element.location['x']}, y={element.location['y']}")
                    logger.info(f"    - 크기: w={element.size['width']}, h={element.size['height']}")
                    
                    # 고유한 XPath 생성
                    unique_xpath = generate_xpath(element)
                    logger.info(f"    - 고유 XPath: {unique_xpath}")
                    logger.info("")
                    break
            except Exception as e:
                logger.debug(f"  선택자 {i+1} 실패: {selector} - {e}")
                continue
        
        # 3. 리뷰 컨테이너 요소 찾기
        logger.info("\n3. 리뷰 컨테이너 요소 분석:")
        review_container_selectors = [
            "//div[contains(@class, 'Jwxk6d')]",
            ".Jwxk6d",
            "//section[contains(@class, 'Jwxk6d')]",
            "//div[contains(@class, 'qZmL0')]",
            ".qZmL0",
            "//section[contains(@class, 'qZmL0')]"
        ]
        
        for i, selector in enumerate(review_container_selectors):
            try:
                if selector.startswith("."):
                    element = driver.find_element(By.CSS_SELECTOR, selector)
                    logger.info(f"  CSS 선택자 {i+1}: {selector}")
                else:
                    element = driver.find_element(By.XPATH, selector)
                    logger.info(f"  XPath 선택자 {i+1}: {selector}")
                
                logger.info(f"    - 태그: {element.tag_name}")
                logger.info(f"    - 클래스: {element.get_attribute('class')}")
                logger.info(f"    - 위치: x={element.location['x']}, y={element.location['y']}")
                logger.info(f"    - 크기: w={element.size['width']}, h={element.size['height']}")
                
                # 고유한 XPath 생성
                unique_xpath = generate_xpath(element)
                logger.info(f"    - 고유 XPath: {unique_xpath}")
                logger.info("")
                break
            except Exception as e:
                logger.debug(f"  선택자 {i+1} 실패: {selector} - {e}")
                continue
        
        # 4. "리뷰 모두 보기" 버튼 요소 찾기
        logger.info("\n4. '리뷰 모두 보기' 버튼 요소 분석:")
        view_all_reviews_selectors = [
            "//span[contains(text(), '리뷰 모두 보기')]",
            "//div[contains(text(), '리뷰 모두 보기')]",
            "//button[contains(text(), '리뷰 모두 보기')]",
            "//a[contains(text(), '리뷰 모두 보기')]",
            ".Jwxk6d button span",
            ".Jwxk6d div[role='button'] span"
        ]
        
        for i, selector in enumerate(view_all_reviews_selectors):
            try:
                if selector.startswith("."):
                    element = driver.find_element(By.CSS_SELECTOR, selector)
                    logger.info(f"  CSS 선택자 {i+1}: {selector}")
                else:
                    element = driver.find_element(By.XPATH, selector)
                    logger.info(f"  XPath 선택자 {i+1}: {selector}")
                
                if "리뷰 모두 보기" in element.text:
                    logger.info(f"    - 태그: {element.tag_name}")
                    logger.info(f"    - 클래스: {element.get_attribute('class')}")
                    logger.info(f"    - 텍스트: {element.text}")
                    logger.info(f"    - 위치: x={element.location['x']}, y={element.location['y']}")
                    logger.info(f"    - 크기: w={element.size['width']}, h={element.size['height']}")
                    
                    # 고유한 XPath 생성
                    unique_xpath = generate_xpath(element)
                    logger.info(f"    - 고유 XPath: {unique_xpath}")
                    logger.info("")
                    break
            except Exception as e:
                logger.debug(f"  선택자 {i+1} 실패: {selector} - {e}")
                continue
        
        # 5. 개별 리뷰 요소 찾기
        logger.info("\n5. 개별 리뷰 요소 분석:")
        try:
            review_elements = driver.find_elements(By.CSS_SELECTOR, "[data-review-id]")
            if review_elements:
                logger.info(f"  data-review-id 속성을 가진 리뷰 요소 {len(review_elements)}개 발견")
                for i, element in enumerate(review_elements[:3]):  # 처음 3개만 분석
                    logger.info(f"    리뷰 {i+1}:")
                    logger.info(f"      - data-review-id: {element.get_attribute('data-review-id')}")
                    logger.info(f"      - 클래스: {element.get_attribute('class')}")
                    logger.info(f"      - 위치: x={element.location['x']}, y={element.location['y']}")
                    logger.info(f"      - 크기: w={element.size['width']}, h={element.size['height']}")
                    
                    # 고유한 XPath 생성
                    unique_xpath = generate_xpath(element)
                    logger.info(f"      - 고유 XPath: {unique_xpath}")
                    logger.info("")
            else:
                logger.info("  data-review-id 속성을 가진 리뷰 요소를 찾을 수 없습니다.")
        except Exception as e:
            logger.debug(f"  리뷰 요소 분석 실패: {e}")
        
        # 6. 페이지 구조 분석
        logger.info("\n6. 페이지 구조 분석:")
        try:
            # 전체 페이지 HTML 구조 분석
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # 리뷰 관련 주요 클래스들 찾기
            review_classes = []
            for element in soup.find_all(class_=True):
                classes = element.get('class', [])
                for cls in classes:
                    if any(keyword in cls.lower() for keyword in ['review', 'rating', 'comment', 'feedback']):
                        if cls not in review_classes:
                            review_classes.append(cls)
            
            logger.info(f"  리뷰 관련 클래스들: {review_classes}")
            
        except Exception as e:
            logger.debug(f"  페이지 구조 분석 실패: {e}")
        
        logger.info("=" * 80)
        logger.info("선택자 분석 완료")
        logger.info("=" * 80)
        
        return True
        
    except Exception as e:
        logger.error(f"선택자 분석 실패: {e}")
        return False

def main():
    """메인 실행 함수"""
    logger = setup_logging()
    
    logger.info("=" * 80)
    logger.info("Google Play Store 리뷰 섹션 선택자 분석 시작")
    logger.info("=" * 80)
    
    try:
        driver = setup_driver()
        logger.info("Firefox WebDriver 초기화 성공")
    except Exception as e:
        logger.error(f"Firefox WebDriver 초기화 실패: {e}")
        return False
    
    try:
        success = analyze_selectors(driver, logger)
        if success:
            logger.info("선택자 분석 성공!")
        else:
            logger.error("선택자 분석 실패")
        return success
    
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

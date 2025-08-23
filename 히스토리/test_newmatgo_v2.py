#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
뉴맞고 게임만 캡처하는 테스트 스크립트 v2 (전체 페이지 스크린샷 방식)
"""

import os
import datetime
import logging
import io
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from PIL import Image
import time

# 로깅 설정
def setup_logging():
    """로깅 설정"""
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    
    log_file = os.path.join(log_dir, f"test_newmatgo_v2_{datetime.datetime.now().strftime('%Y%m%d')}.log")
    
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
    """Chrome WebDriver 설정"""
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--force-device-scale-factor=1")
    chrome_options.add_argument("--disable-web-security")
    chrome_options.add_argument("--allow-running-insecure-content")
    chrome_options.add_argument("--disable-features=VizDisplayCompositor")
    # chrome_options.add_argument("--headless")  # 헤드리스 모드 비활성화 (디버깅용)
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    return webdriver.Chrome(options=chrome_options)

def capture_newmatgo_review_v2(driver, save_dir, logger):
    """뉴맞고 리뷰 섹션 캡처 v2 (전체 페이지 스크린샷 방식)"""
    url = "https://play.google.com/store/apps/details?id=com.neowiz.games.newmatgo"
    
    try:
        logger.info(f"캡처 시작: NewMatgo ({url})")
        driver.get(url)
        time.sleep(8)  # 페이지 로딩 대기 시간 증가
        
        # "리뷰 모두 보기" 버튼을 클릭하지 않고 기본 리뷰 섹션만 캡처
        logger.info(f"기본 리뷰 섹션 캡처 시작: NewMatgo (버튼 클릭 없음)")
        
        # 리뷰 섹션 찾기
        review_section = None
        review_section_selectors = [
            "//div[contains(@class, 'Jwxk6d')]",  # 메인 리뷰 섹션
        ]
        
        for i, selector in enumerate(review_section_selectors):
            try:
                review_section = driver.find_element(By.XPATH, selector)
                logger.info(f"리뷰 섹션 찾기 성공: NewMatgo (선택자 {i+1}: {selector})")
                break
            except Exception as e:
                logger.debug(f"리뷰 섹션 선택자 {i+1} 실패: {selector} - {e}")
                continue
        
        if review_section is None:
            logger.error(f"리뷰 섹션을 찾을 수 없습니다: NewMatgo")
            return False
        
        # 리뷰 섹션으로 스크롤
        logger.info(f"리뷰 섹션으로 스크롤: NewMatgo")
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'start'});", review_section)
        time.sleep(3)  # 스크롤 완료 대기
        
        # 전체 페이지 높이 설정 (모든 콘텐츠가 보이도록)
        logger.info("전체 페이지 높이 설정")
        total_height = driver.execute_script("return document.body.scrollHeight")
        driver.set_window_size(1920, total_height)
        time.sleep(2)
        
        # 스크린샷 촬영 (ActionChains 사용)
        logger.info(f"전체 페이지 스크린샷 촬영: NewMatgo")
        
        # ActionChains를 사용하여 스크린샷 촬영
        actions = ActionChains(driver)
        actions.pause(2)  # 추가 대기
        actions.perform()
        
        # 스크린샷 촬영
        screenshot = driver.get_screenshot_as_png()
        img = Image.open(io.BytesIO(screenshot))
        
        logger.info(f"전체 스크린샷 크기: {img.width} x {img.height}")
        
        # 리뷰 섹션 위치 정보 가져오기
        section_location = review_section.location
        section_size = review_section.size
        
        logger.info(f"리뷰 섹션 위치: x={section_location['x']}, y={section_location['y']}")
        logger.info(f"리뷰 섹션 크기: width={section_size['width']}, height={section_size['height']}")
        
        # 리뷰 모두 보기 버튼 찾기
        review_end_y = None
        try:
            review_end_element = driver.find_element(By.XPATH, "//span[contains(text(), '리뷰 모두 보기')]")
            review_end_y = review_end_element.location['y']
            logger.info(f"리뷰 모두 보기 버튼 위치: y={review_end_y}")
        except Exception as e:
            logger.debug(f"리뷰 모두 보기 버튼 찾기 실패: {e}")
        
        # 캡처 영역 계산
        crop_left = max(0, section_location['x'])
        crop_top = max(0, section_location['y'])
        crop_right = min(img.width, section_location['x'] + section_size['width'])
        
        # 하단 경계 설정
        if review_end_y and review_end_y > crop_top:
            crop_bottom = review_end_y
            logger.info(f"리뷰 모두 보기 버튼 위까지만 캡처: bottom={crop_bottom}")
        else:
            crop_bottom = min(img.height, section_location['y'] + section_size['height'])
            logger.info(f"리뷰 섹션 전체 캡처: bottom={crop_bottom}")
        
        logger.info(f"최종 크롭 영역: left={crop_left}, top={crop_top}, right={crop_right}, bottom={crop_bottom}")
        
        # 크롭 및 저장
        if crop_right > crop_left and crop_bottom > crop_top:
            cropped_img = img.crop((crop_left, crop_top, crop_right, crop_bottom))
        else:
            logger.warning(f"크롭 영역이 유효하지 않습니다. 전체 화면을 캡처합니다.")
            cropped_img = img
        
        # 파일 저장
        filename = f"NewMatgo_v2_{datetime.datetime.now().strftime('%Y%m%d')}.png"
        filepath = os.path.join(save_dir, filename)
        cropped_img.save(filepath)
        
        logger.info(f"캡처 완료: {filename} (크기: {cropped_img.width} x {cropped_img.height})")
        return True
        
    except Exception as e:
        logger.error(f"캡처 실패 (NewMatgo): {e}")
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
    logger.info("뉴맞고 리뷰 캡처 테스트 v2 시작")
    logger.info(f"캡처 날짜: {today}")
    logger.info(f"저장 폴더: {save_dir}")
    logger.info("=" * 50)
    
    # 폴더 생성
    os.makedirs(save_dir, exist_ok=True)
    logger.info(f"저장 폴더 생성: {save_dir}")
    
    # WebDriver 설정
    try:
        driver = setup_driver()
        logger.info("Chrome WebDriver 초기화 성공")
    except Exception as e:
        logger.error(f"Chrome WebDriver 초기화 실패: {e}")
        return False
    
    try:
        # 뉴맞고만 캡처
        if capture_newmatgo_review_v2(driver, save_dir, logger):
            logger.info("=" * 50)
            logger.info("뉴맞고 v2 캡처 성공!")
            logger.info("=" * 50)
            return True
        else:
            logger.error("뉴맞고 v2 캡처 실패")
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

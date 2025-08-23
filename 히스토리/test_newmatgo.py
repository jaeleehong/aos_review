#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
뉴맞고 게임만 캡처하는 테스트 스크립트
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
from PIL import Image
import time

# 로깅 설정
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
    """Chrome WebDriver 설정"""
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    # chrome_options.add_argument("--headless")  # 헤드리스 모드 비활성화 (디버깅용)
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    return webdriver.Chrome(options=chrome_options)

def capture_newmatgo_review(driver, save_dir, logger):
    """뉴맞고 리뷰 섹션 캡처"""
    url = "https://play.google.com/store/apps/details?id=com.neowiz.games.newmatgo"
    
    try:
        logger.info(f"캡처 시작: NewMatgo ({url})")
        driver.get(url)
        time.sleep(8)  # 페이지 로딩 대기 시간 증가
        
        # "리뷰 모두 보기" 버튼을 클릭하지 않고 기본 리뷰 섹션만 캡처
        logger.info(f"기본 리뷰 섹션 캡처 시작: NewMatgo (버튼 클릭 없음)")
        
        # 평점 표시 영역 찾기
        rating_section = None
        rating_selectors = [
            "//div[contains(@class, 'TTRhpd')]",  # 기존 선택자
            "//div[contains(@class, 'jILTFe')]",  # 새로운 클래스명
            "//div[contains(@class, 'VWIeTd')]",  # 대체 클래스명
            "//div[contains(@class, 'g1rdde')]",  # 추가 대체 클래스명
            "//div[contains(@class, 'rating')]",  # rating 클래스 포함
            "//div[contains(@class, 'score')]",   # score 클래스 포함
            "//div[contains(@class, 'stars')]",   # stars 클래스 포함
        ]
        
        for i, selector in enumerate(rating_selectors):
            try:
                rating_section = WebDriverWait(driver, 3).until(
                    EC.presence_of_element_located((By.XPATH, selector))
                )
                rating_bottom = rating_section.location['y'] + rating_section.size['height']
                logger.info(f"평점 섹션 찾기 성공: NewMatgo (선택자 {i+1}: {selector})")
                logger.info(f"평점 섹션 위치: y={rating_section.location['y']}, height={rating_section.size['height']}, bottom={rating_bottom}")
                break
            except Exception as e:
                logger.debug(f"평점 섹션 선택자 {i+1} 실패: {selector} - {e}")
                continue
        
        if rating_section is None:
            logger.error(f"평점 섹션을 찾을 수 없습니다: NewMatgo")
            return False
        
        # 기본 리뷰 섹션 찾기 - 확인된 정보를 바탕으로 정확한 선택자 사용
        review_section = None
        review_section_selectors = [
            # 확인된 정확한 선택자 (우선순위 1)
            "//div[contains(@class, 'Jwxk6d')]",  # 메인 리뷰 섹션 (860x1321 크기)
            # 대체 선택자들
            "//div[contains(@class, 'Jwxk6d') and contains(@class, 'review')]",
            "//div[contains(@class, 'Jwxk6d') and contains(@class, 'rating')]",
            "//div[contains(@class, 'Jwxk6d') and contains(@class, 'reviews')]",
            # 리뷰 목록이 포함된 섹션
            "//div[contains(@class, 'review') and contains(@class, 'list')]",
            "//div[contains(@class, 'reviews') and contains(@class, 'list')]",
            "//div[contains(@class, 'review') and contains(@class, 'section')]",
            "//div[contains(@class, 'reviews') and contains(@class, 'section')]",
            # 평점 분포 차트가 포함된 섹션
            "//div[contains(@class, 'bar') and contains(@class, 'chart')]",
            "//div[contains(@class, 'rating') and contains(@class, 'distribution')]",
            "//div[contains(@class, 'star') and contains(@class, 'distribution')]",
            # 리뷰 관련 클래스들 (더 구체적)
            "//div[contains(@class, 'review') and not(contains(@class, 'app'))]",  # app 클래스가 없는 review
            "//div[contains(@class, 'reviews') and not(contains(@class, 'app'))]",  # app 클래스가 없는 reviews
            "//div[contains(@class, 'rating') and not(contains(@class, 'app'))]",  # app 클래스가 없는 rating
            # Google Play Store의 실제 클래스명들
            "//div[contains(@class, 'TTRhpd')]",  # 평점 섹션
            "//div[contains(@class, 'jILTFe')]",  # 평점 섹션 (새로운 클래스)
            "//div[contains(@class, 'VWIeTd')]",  # 평점 섹션 (대체 클래스)
            "//div[contains(@class, 'g1rdde')]",  # 평점 섹션 (추가 클래스)
            # 리뷰 관련 텍스트가 포함된 요소들
            "//div[contains(text(), '리뷰')]",
            "//div[contains(text(), '평점')]",
            "//div[contains(text(), '별점')]",
            "//div[contains(text(), 'review')]",
            "//div[contains(text(), 'rating')]",
            "//div[contains(text(), 'star')]"
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
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", review_section)
        time.sleep(3)  # 스크롤 완료 대기
        
        # 스크린샷 촬영 및 디버깅
        logger.info(f"스크린샷 캡처 시작: NewMatgo")
        
        # 페이지가 완전히 로드될 때까지 대기
        time.sleep(5)  # 스크린샷 촬영 전 대기 시간 증가
        
        # 스크린샷 촬영
        screenshot = driver.get_screenshot_as_png()
        img = Image.open(io.BytesIO(screenshot))
        
        logger.info(f"전체 스크린샷 크기: {img.width} x {img.height}")
        
        # 리뷰 섹션의 정확한 경계 계산
        section_location = review_section.location
        section_size = review_section.size
        
        # 리뷰 모두 보기 버튼 찾기 (캡처 영역 제한용)
        review_end_y = None
        try:
            review_end_selectors = [
                "//span[contains(text(), '리뷰 모두 보기')]",
                "//button[contains(text(), '리뷰 모두 보기')]",
                "//a[contains(text(), '리뷰 모두 보기')]",
                "//div[contains(text(), '리뷰 모두 보기')]",
                "//span[contains(text(), '모든 리뷰 보기')]",
                "//button[contains(text(), '모든 리뷰 보기')]",
                "//a[contains(text(), '모든 리뷰 보기')]",
                "//div[contains(text(), '모든 리뷰 보기')]"
            ]
            
            for selector in review_end_selectors:
                try:
                    review_end_element = driver.find_element(By.XPATH, selector)
                    review_end_y = review_end_element.location['y']
                    logger.info(f"리뷰 모두 보기 버튼 위치: y={review_end_y}")
                    break
                except:
                    continue
        except Exception as e:
            logger.debug(f"리뷰 모두 보기 버튼 찾기 실패: {e}")
        
        # 캡처 영역 계산
        crop_left = max(0, section_location['x'])
        crop_top = max(0, section_location['y'])
        crop_right = min(img.width, section_location['x'] + section_size['width'])
        
        # 하단 경계 설정 (리뷰 모두 보기 버튼 위까지만)
        if review_end_y and review_end_y > crop_top:
            crop_bottom = review_end_y
            logger.info(f"리뷰 모두 보기 버튼 위까지만 캡처: bottom={crop_bottom}")
        else:
            crop_bottom = min(img.height, section_location['y'] + section_size['height'])
            logger.info(f"리뷰 섹션 전체 캡처: bottom={crop_bottom}")
        
        logger.info(f"리뷰 섹션 위치: x={section_location['x']}, y={section_location['y']}")
        logger.info(f"리뷰 섹션 크기: width={section_size['width']}, height={section_size['height']}")
        logger.info(f"최종 크롭 영역: left={crop_left}, top={crop_top}, right={crop_right}, bottom={crop_bottom}")
        
        if crop_right > crop_left and crop_bottom > crop_top:
            cropped_img = img.crop((crop_left, crop_top, crop_right, crop_bottom))
        else:
            logger.warning(f"크롭 영역이 유효하지 않습니다. 전체 화면을 캡처합니다.")
            cropped_img = img
        
        # 파일 저장
        filename = f"NewMatgo_{datetime.datetime.now().strftime('%Y%m%d')}.png"
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
    logger.info("뉴맞고 리뷰 캡처 테스트 시작")
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
        if capture_newmatgo_review(driver, save_dir, logger):
            logger.info("=" * 50)
            logger.info("뉴맞고 캡처 성공!")
            logger.info("=" * 50)
            return True
        else:
            logger.error("뉴맞고 캡처 실패")
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

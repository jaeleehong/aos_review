#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google Play 리뷰 자동 캡처 및 HTML 업데이트 스크립트 (Firefox 버전)
뉴맞고에서 성공한 방식을 모든 게임에 적용
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
from PIL import Image
import time

# 게임 정보
GAMES = {
    "NewMatgo": {
        "package": "com.neowiz.games.newmatgo",
        "name": "피망 뉴맞고"
    },
    "NewMatgoKakao": {
        "package": "com.neowiz.games.newmatgoKakao",
        "name": "피망 뉴맞고 for Kakao"
    },
    "Original": {
        "package": "com.neowiz.games.pmang.gostop",
        "name": "피망 고스톱"
    },
    "Poker": {
        "package": "com.neowiz.games.poker",
        "name": "피망 포커"
    },
    "PokerKakao": {
        "package": "com.neowiz.games.pokerKakao",
        "name": "피망 포커 for Kakao"
    },
    "Sudda": {
        "package": "com.neowiz.games.sudda",
        "name": "피망 섯다"
    },
    "SuddaKakao": {
        "package": "com.neowiz.games.suddaKakao",
        "name": "피망 섯다 for Kakao"
    },
    "ShowdownHoldem": {
        "package": "com.neowiz.games.pmang.holdem.poker",
        "name": "피망 쇼다운 홀덤"
    },
    "NewVegas": {
        "package": "com.neowiz.playstudio.slot.casino",
        "name": "피망 뉴베가스"
    }
}

# 로깅 설정
def setup_logging():
    """로깅 설정"""
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    
    log_file = os.path.join(log_dir, f"auto_capture_{datetime.datetime.now().strftime('%Y%m%d')}.log")
    
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

def capture_review_section(driver, package_name, game_name, save_dir, logger):
    """리뷰 섹션 캡처 (뉴맞고에서 성공한 방식 적용)"""
    url = f"https://play.google.com/store/apps/details?id={package_name}"
    
    try:
        logger.info(f"캡처 시작: {game_name} ({url})")
        driver.get(url)
        time.sleep(3)
        
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
        
        # 리뷰 섹션 찾기 (뉴맞고에서 성공한 방식)
        logger.info(f"기본 리뷰 섹션 캡처 시작: {game_name} (버튼 클릭 없음)")
        
        review_section = None
        review_section_selectors = [
            "//div[contains(@class, 'Jwxk6d')]",  # 메인 리뷰 섹션 (뉴맞고에서 성공한 선택자)
        ]
        
        for i, selector in enumerate(review_section_selectors):
            try:
                review_section = driver.find_element(By.XPATH, selector)
                logger.info(f"리뷰 섹션 찾기 성공: {game_name} (선택자 {i+1}: {selector})")
                break
            except Exception as e:
                logger.debug(f"리뷰 섹션 선택자 {i+1} 실패: {selector} - {e}")
                continue
        
        if review_section is None:
            logger.error(f"리뷰 섹션을 찾을 수 없습니다: {game_name}")
            return False
        
        # 리뷰 섹션으로 스크롤
        logger.info(f"리뷰 섹션으로 스크롤: {game_name}")
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'start'});", review_section)
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
        
        # 파일 저장 (firefox 제외)
        filename = f"{game_name}_{datetime.datetime.now().strftime('%Y%m%d')}.png"
        filepath = os.path.join(save_dir, filename)
        cropped_img.save(filepath)
        
        logger.info(f"캡처 완료: {filename} (크기: {cropped_img.width} x {cropped_img.height})")
        return True
        
    except Exception as e:
        logger.error(f"캡처 실패 ({game_name}): {e}")
        return False

def update_html_file(save_dir, logger):
    """HTML 파일 업데이트"""
    try:
        html_file_path = os.path.join(os.path.dirname(save_dir), "구글 플레이_리뷰.html")
        logger.info(f"HTML 파일 업데이트 시작: {html_file_path}")
        
        if not os.path.exists(html_file_path):
            logger.warning(f"HTML 파일이 존재하지 않습니다: {html_file_path}")
            return False
        
        # HTML 파일 읽기
        with open(html_file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # 날짜 폴더명 추출
        folder_name = os.path.basename(save_dir)
        
        # 이미지 경로 업데이트 (상대 경로 사용)
        for game_key, game_info in GAMES.items():
            old_pattern = f'src="./{folder_name}/{game_key}_'
            new_pattern = f'src="./{folder_name}/{game_key}_{folder_name}.png"'
            
            # 기존 패턴을 찾아서 교체
            import re
            pattern = f'src="\./{folder_name}/{game_key}_[^"]*\.png"'
            replacement = f'src="./{folder_name}/{game_key}_{folder_name}.png"'
            html_content = re.sub(pattern, replacement, html_content)
        
        # 통계 정보 업데이트
        today = datetime.datetime.now().strftime('%Y%m%d')
        
        # 캡처 일수 증가
        capture_days_pattern = r'캡처 일수: (\d+)일'
        match = re.search(capture_days_pattern, html_content)
        if match:
            current_days = int(match.group(1))
            new_days = current_days + 1
            html_content = re.sub(capture_days_pattern, f'캡처 일수: {new_days}일', html_content)
        
        # 총 이미지 수 증가
        total_images_pattern = r'총 이미지: (\d+)개'
        match = re.search(total_images_pattern, html_content)
        if match:
            current_images = int(match.group(1))
            new_images = current_images + len(GAMES)
            html_content = re.sub(total_images_pattern, f'총 이미지: {new_images}개', html_content)
        
        # 최근 캡처 날짜 업데이트
        recent_capture_pattern = r'최근 캡처: \d{8}'
        html_content = re.sub(recent_capture_pattern, f'최근 캡처: {today}', html_content)
        
        # HTML 파일 저장
        with open(html_file_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"통계 정보 업데이트: 캡처 일수 +1, 총 이미지 +{len(GAMES)}, 최근 캡처 {today}")
        logger.info(f"HTML 파일 업데이트 완료: {html_file_path}")
        return True
        
    except Exception as e:
        logger.error(f"HTML 파일 업데이트 실패: {e}")
        return False

def main():
    """메인 실행 함수"""
    # 로깅 설정
    logger = setup_logging()
    
    base_dir = "D:\\aos review"
    today = datetime.datetime.now().strftime('%Y%m%d')
    save_dir = os.path.join(base_dir, today)
    
    logger.info("=" * 50)
    logger.info("Google Play 리뷰 자동 캡처 시작")
    logger.info(f"캡처 날짜: {today}")
    logger.info(f"저장 폴더: {save_dir}")
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
        # 각 게임별 캡처
        success_count = 0
        failed_games = []
        
        for game_key, game_info in GAMES.items():
            logger.info(f"캡처 진행 중: {game_key}")
            
            if capture_review_section(driver, game_info["package"], game_key, save_dir, logger):
                success_count += 1
            else:
                failed_games.append(game_key)
        
        logger.info(f"캡처 완료: {success_count}개 게임 성공")
        
        if failed_games:
            logger.warning(f"캡처 실패한 게임: {', '.join(failed_games)}")
        
        # HTML 파일 업데이트
        if success_count > 0:
            logger.info("HTML 파일 업데이트 시작")
            if update_html_file(save_dir, logger):
                logger.info("HTML 파일 업데이트 성공")
            else:
                logger.warning("HTML 파일 업데이트 실패")
        
        logger.info("=" * 50)
        logger.info("자동화 완료!")
        logger.info(f"캡처된 게임: {', '.join([game for game in GAMES.keys() if game not in failed_games])}")
        logger.info("=" * 50)
        
        return success_count > 0
    
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

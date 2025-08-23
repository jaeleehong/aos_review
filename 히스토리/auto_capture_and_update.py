#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google Play 리뷰 캡처 및 HTML 자동 업데이트 통합 스크립트
매일 00:05에 자동 실행되도록 설계됨
"""

import os
import re
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

# 게임 정보
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

# 사업실별 게임 분류
BUSINESS_UNITS = {
    "red": ["NewMatgo", "NewMatgoKakao", "Sudda", "SuddaKakao", "Original"],
    "blue": ["Poker", "PokerKakao", "ShowdownHoldem"],
    "brown": ["NewVegas"]
}

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
    """리뷰 섹션 캡처"""
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
        
        # "리뷰 모두 보기" 버튼을 클릭하지 않고 기본 리뷰 섹션만 캡처
        logger.info(f"기본 리뷰 섹션 캡처 시작: {game_name} (버튼 클릭 없음)")
        
        # 평점 표시 영역 찾기 - 여러 선택자 시도
        rating_section = None
        rating_selectors = [
            "//div[contains(@class, 'TTRhpd')]",  # 기존 선택자
            "//div[contains(@class, 'jILTFe')]",  # 새로운 클래스명
            "//div[contains(@class, 'VWIeTd')]",  # 대체 클래스명
            "//div[contains(@class, 'g1rdde')]",  # 추가 대체 클래스명
            "//div[contains(@class, 'rating')]",  # rating 클래스 포함
            "//div[contains(@class, 'score')]",   # score 클래스 포함
            "//div[contains(@class, 'stars')]",   # stars 클래스 포함
            "//div[contains(@class, 'review') and contains(@class, 'rating')]",  # review와 rating 조합
            "//div[contains(@class, 'app') and contains(@class, 'rating')]",     # app과 rating 조합
            "//div[contains(@class, 'store') and contains(@class, 'rating')]",   # store와 rating 조합
            "//div[contains(@class, 'play') and contains(@class, 'rating')]",    # play와 rating 조합
            "//div[contains(@class, 'google') and contains(@class, 'rating')]",  # google과 rating 조합
            "//div[contains(@class, 'rating') or contains(@class, 'score') or contains(@class, 'stars')]",  # OR 조건
            "//div[contains(@class, 'TTRhpd') or contains(@class, 'jILTFe') or contains(@class, 'VWIeTd')]",  # 기존 + 새로운 클래스들
            "//div[contains(@class, 'g1rdde') or contains(@class, 'rating') or contains(@class, 'score')]",  # 추가 대체들
            "//div[contains(@class, 'review') or contains(@class, 'rating') or contains(@class, 'score') or contains(@class, 'stars')]",  # 모든 관련 클래스
            "//div[contains(@class, 'app') or contains(@class, 'store') or contains(@class, 'play') or contains(@class, 'google')]",  # 모든 관련 클래스
            "//div[contains(@class, 'TTRhpd') or contains(@class, 'jILTFe') or contains(@class, 'VWIeTd') or contains(@class, 'g1rdde') or contains(@class, 'rating') or contains(@class, 'score') or contains(@class, 'stars')]",  # 모든 가능한 클래스
            "//div[contains(@class, 'review') or contains(@class, 'rating') or contains(@class, 'score') or contains(@class, 'stars') or contains(@class, 'app') or contains(@class, 'store') or contains(@class, 'play') or contains(@class, 'google')]",  # 모든 관련 클래스
            "//div[contains(@class, 'TTRhpd') or contains(@class, 'jILTFe') or contains(@class, 'VWIeTd') or contains(@class, 'g1rdde') or contains(@class, 'rating') or contains(@class, 'score') or contains(@class, 'stars') or contains(@class, 'review') or contains(@class, 'app') or contains(@class, 'store') or contains(@class, 'play') or contains(@class, 'google')]"  # 모든 가능한 클래스
        ]
        
        for i, selector in enumerate(rating_selectors):
            try:
                rating_section = WebDriverWait(driver, 3).until(
                    EC.presence_of_element_located((By.XPATH, selector))
                )
                rating_bottom = rating_section.location['y'] + rating_section.size['height']
                logger.info(f"평점 섹션 찾기 성공: {game_name} (선택자 {i+1}: {selector})")
                logger.info(f"평점 섹션 위치: y={rating_section.location['y']}, height={rating_section.size['height']}, bottom={rating_bottom}")
                break
            except Exception as e:
                logger.debug(f"평점 섹션 선택자 {i+1} 실패: {selector} - {e}")
                continue
        
        if rating_section is None:
            # 모든 선택자가 실패한 경우, 페이지 소스를 저장하여 디버깅
            try:
                page_source = driver.page_source
                debug_file = os.path.join(save_dir, f"{game_name}_debug_page_source.html")
                with open(debug_file, 'w', encoding='utf-8') as f:
                    f.write(page_source)
                logger.error(f"평점 섹션을 찾을 수 없습니다: {game_name} - 페이지 소스 저장됨: {debug_file}")
            except Exception as e:
                logger.error(f"페이지 소스 저장 실패: {game_name} - {e}")
            return False
        
        # 리뷰 섹션 찾기 (뉴맞고에서 성공한 방식 적용)
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
            # 모든 선택자가 실패한 경우, 페이지 소스를 저장하여 디버깅
            try:
                page_source = driver.page_source
                debug_file = os.path.join(save_dir, f"{game_name}_debug_page_source.html")
                with open(debug_file, 'w', encoding='utf-8') as f:
                    f.write(page_source)
                logger.error(f"리뷰 섹션을 찾을 수 없습니다: {game_name} - 페이지 소스 저장됨: {debug_file}")
            except Exception as e:
                logger.error(f"페이지 소스 저장 실패: {game_name} - {e}")
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
        
        # 스크린샷 촬영 및 디버깅
        logger.info(f"전체 페이지 스크린샷 촬영: {game_name}")
        
        # 페이지가 완전히 로드될 때까지 대기
        time.sleep(3)
        
        # 스크린샷 촬영
        screenshot = driver.get_screenshot_as_png()
        img = Image.open(io.BytesIO(screenshot))
        
        logger.info(f"전체 스크린샷 크기: {img.width} x {img.height}")
        
        # 리뷰 섹션 위치 정보 가져오기 (뉴맞고에서 성공한 방식)
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
                    review_end_y = review_end_element.location['y']
                    if review_end_y > crop_top and review_end_y < crop_bottom:
                        crop_bottom = review_end_y
                        logger.info(f"리뷰 모두 보기 버튼 위치: y={review_end_y}")
                        logger.info(f"수정된 크롭 영역: top={crop_top}, bottom={crop_bottom}")
                
            except Exception as e:
                logger.debug(f"리뷰 섹션 하단 경계 찾기 실패: {e}")
            
            if crop_right > crop_left and crop_bottom > crop_top:
                cropped_img = img.crop((crop_left, crop_top, crop_right, crop_bottom))
            else:
                logger.warning(f"리뷰 섹션 크롭 영역이 유효하지 않습니다. 전체 화면을 캡처합니다.")
                cropped_img = img
        else:
            # 리뷰 섹션을 찾지 못한 경우, 평점 섹션을 기준으로 캡처
            logger.warning(f"리뷰 섹션을 찾을 수 없습니다. 평점 섹션을 기준으로 캡처합니다: {game_name}")
            
            # 평점 섹션 위치를 기준으로 캡처 시작점 설정
            if rating_section:
                rating_top = rating_section.location['y']
                logger.info(f"평점 섹션 상단 위치: {rating_top}")
                
                # 평점 섹션 위쪽부터 화면 하단까지 캡처 (첨부된 이미지와 유사한 영역)
                crop_top = max(0, rating_top - 50)  # 평점 섹션 위 50px 여유 공간
                crop_bottom = img.height
                
                logger.info(f"평점 섹션 기준 크롭 영역: top={crop_top}, bottom={crop_bottom}")
                
                if crop_bottom > crop_top:
                    cropped_img = img.crop((0, crop_top, img.width, crop_bottom))
                else:
                    logger.warning(f"크롭 영역이 유효하지 않습니다. 전체 화면을 캡처합니다.")
                    cropped_img = img
            else:
                # 평점 섹션도 찾지 못한 경우 전체 화면 캡처
                logger.warning(f"평점 섹션도 찾을 수 없습니다. 전체 화면을 캡처합니다.")
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

def update_html_file(html_file, new_date, new_images, logger):
    """HTML 파일 자동 업데이트"""
    try:
        logger.info(f"HTML 파일 업데이트 시작: {html_file}")
        
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 1. 날짜 선택 드롭다운에 새 날짜 추가
        date_select_pattern = r'(<select id="dateSelect" class="date-select" onchange="showDateContent\(this\.value\)">\s*)(.*?)(\s*</select>)'
        match = re.search(date_select_pattern, content, re.DOTALL)
        
        if match:
            existing_options = match.group(2)
            new_option = f'<option value="{new_date}">{new_date[:4]}년 {new_date[4:6]}월 {new_date[6:8]}일</option>\n                        '
            
            if new_date not in existing_options:
                new_options = new_option + existing_options
                content = re.sub(date_select_pattern, r'\1' + new_options + r'\3', content, flags=re.DOTALL)
                logger.info(f"날짜 선택 드롭다운 업데이트: {new_date}")
        
        # 2. 통계 정보 업데이트
        # 캡처 일수 증가
        content = re.sub(r'(<div class="stat-number">)(\d+)(</div>\s*<div class="stat-label">캡처 일수</div>)', 
                        lambda m: m.group(1) + str(int(m.group(2)) + 1) + m.group(3), content)
        
        # 총 이미지 수 증가
        content = re.sub(r'(<div class="stat-number">)(\d+)(</div>\s*<div class="stat-label">총 이미지</div>)', 
                        lambda m: m.group(1) + str(int(m.group(2)) + len(new_images)) + m.group(3), content)
        
        # 최근 캡처 날짜 업데이트
        content = re.sub(r'(<div class="stat-number">)(\d+)(</div>\s*<div class="stat-label">최근 캡처</div>)', 
                        lambda m: m.group(1) + new_date + m.group(3), content)
        
        logger.info(f"통계 정보 업데이트: 캡처 일수 +1, 총 이미지 +{len(new_images)}, 최근 캡처 {new_date}")
        
        # 3. 새 날짜 콘텐츠 섹션 추가
        new_content_section = generate_content_section(new_date, new_images)
        
        # 첫 번째 date-content 섹션 앞에 삽입
        content = re.sub(r'(<div class="content-area">\s*)(<div class="date-content")', 
                        r'\1' + new_content_section + r'\n\n                \2', content)
        
        # 4. 파일 저장
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"HTML 파일 업데이트 완료: {html_file}")
        return True
        
    except Exception as e:
        logger.error(f"HTML 업데이트 실패: {e}")
        return False

def generate_content_section(date, images):
    """새 날짜의 콘텐츠 섹션 생성"""
    year = date[:4]
    month = date[4:6]
    day = date[6:8]
    
    # 이전 날짜 계산 (가장 최근 날짜를 전주로 설정)
    prev_date = get_previous_date(date)
    
    section = f'''                <div class="date-content" id="content-{date}" style="display: none;">
                    <div class="comparison-info">
                        <h3>📊 {year}년 {month}월 {day}일 리포트 (전주 대비)</h3>
                        <div class="comparison-dates">
                            <span class="prev-week-info">📅 전주: {prev_date[:4]}년 {prev_date[4:6]}월 {prev_date[6:8]}일</span>
                            <span class="current-week-info">📅 금주: {year}년 {month}월 {day}일</span>
                        </div>
                    </div>'''
    
    # 사업실별로 게임 그룹화
    for business_type, games in BUSINESS_UNITS.items():
        business_name = {"red": "레드사업실", "blue": "블루사업실", "brown": "브라운사업실"}[business_type]
        business_emoji = {"red": "🎴", "blue": "♠️", "brown": "🎰"}[business_type]
        
        section += f'''

                    <div class="business-group {business_type}">
                        <div class="business-header {business_type}">
                            {business_emoji} {business_name}
                        </div>
                        <div class="app-grid">'''
        
        for game in games:
            if game in images:
                section += generate_game_card(game, prev_date, date, business_type)
        
        section += '''
                        </div>
                    </div>'''
    
    section += '''
                </div>'''
    
    return section

def generate_game_card(game, prev_date, current_date, business_type):
    """게임 카드 HTML 생성"""
    korean_names = {
        "NewMatgo": "뉴맞고", "NewMatgoKakao": "뉴맞고카카오", "Original": "오리지널",
        "Poker": "포커", "PokerKakao": "포커카카오", "ShowdownHoldem": "쇼다운홀덤",
        "Sudda": "섯다", "SuddaKakao": "섯다카카오", "NewVegas": "뉴베가스"
    }
    
    korean_name = korean_names.get(game, game)
    icon_name = korean_name.lower()
    
    return f'''

                            <div class="app-card {business_type}">
                                <div class="app-header">
                                    <h4><img src="앱아이콘/{icon_name}.webp" alt="{korean_name} 아이콘" class="app-icon"> {korean_name}</h4>
                                </div>
                                <div class="image-comparison">
                                    <div class="image-section">
                                        <h5 class="prev-week">📅 전주 ({prev_date[:4]}년 {prev_date[4:6]}월 {prev_date[6:8]}일)</h5>
                                        <img src="{prev_date}/{game}_{prev_date}.png" alt="{korean_name} 전주 리뷰" class="capture-image"
                                            onclick="openModal(this.src)">
                                        <div class="image-info">
                                            📸 {game}_{prev_date}.png<br>
                                            클릭하면 원본 크기로 확대됩니다
                                        </div>
                                    </div>
                                    <div class="image-section">
                                        <h5 class="current-week">📅 금주 ({current_date[:4]}년 {current_date[4:6]}월 {current_date[6:8]}일)</h5>
                                        <img src="{current_date}/{game}_{current_date}.png" alt="{korean_name} 금주 리뷰" class="capture-image"
                                            onclick="openModal(this.src)">
                                        <div class="image-info">
                                            📸 {game}_{current_date}.png<br>
                                            클릭하면 원본 크기로 확대됩니다
                                        </div>
                                    </div>
                                </div>
                            </div>'''

def get_previous_date(current_date):
    """이전 날짜 계산 (가장 최근 폴더 찾기)"""
    base_dir = "D:\\aos review"
    folders = [f for f in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, f)) and f.isdigit()]
    folders.sort(reverse=True)
    
    for folder in folders:
        if folder < current_date:
            return folder
    
    return current_date  # 이전 날짜가 없으면 현재 날짜 반환

def main():
    """메인 실행 함수"""
    # 로깅 설정
    logger = setup_logging()
    
    base_dir = "D:\\aos review"
    html_file = os.path.join(base_dir, "구글 플레이_리뷰.html")
    
    # 오늘 날짜
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
        logger.info("Chrome WebDriver 초기화 성공")
    except Exception as e:
        logger.error(f"Chrome WebDriver 초기화 실패: {e}")
        return False
    
    try:
        captured_images = []
        
        # 각 게임 캡처
        for package_name, game_name in GAMES.items():
            logger.info(f"캡처 진행 중: {game_name}")
            if capture_review_section(driver, package_name, game_name, save_dir, logger):
                captured_images.append(game_name)
        
        logger.info(f"캡처 완료: {len(captured_images)}개 게임 성공")
        
        # HTML 파일 업데이트
        if captured_images and os.path.exists(html_file):
            logger.info("HTML 파일 업데이트 시작")
            if update_html_file(html_file, today, captured_images, logger):
                logger.info("=" * 50)
                logger.info("자동화 완료!")
                logger.info(f"캡처된 게임: {', '.join(captured_images)}")
                logger.info("=" * 50)
                return True
            else:
                logger.error("HTML 업데이트 실패")
                return False
        else:
            if not captured_images:
                logger.error("캡처된 이미지가 없습니다.")
            if not os.path.exists(html_file):
                logger.error(f"HTML 파일을 찾을 수 없습니다: {html_file}")
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


#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
매일 자동으로 Google Play 리뷰를 캡처하고 HTML 파일을 업데이트하는 스크립트
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

# 게임 정보 정의
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
    firefox_options.add_argument("--height=1200")  # 높이를 늘려서 더 많은 내용 표시
    firefox_options.add_argument("--headless")  # 백그라운드 실행을 위한 헤드리스 모드
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
            "//a[contains(text(), '리뷰 모두 보기')]",
            "//div[contains(text(), '새로운 기능')]",
            "//h3[contains(text(), '새로운 기능')]",
            "//div[contains(text(), '부적절한 앱으로 신고')]",
            "//a[contains(text(), '부적절한 앱으로 신고')]"
        ]
        
        for i, selector in enumerate(end_element_selectors):
            try:
                end_element = driver.find_element(By.XPATH, selector)
                logger.info(f"끝 요소 찾기 성공: (선택자 {i+1}: {selector})")
                break
            except Exception as e:
                logger.debug(f"끝 요소 선택자 {i+1} 실패: {selector} - {e}")
                continue
        
        if end_element is None:
            logger.warning(f"끝 요소를 찾을 수 없습니다. 기본 높이로 캡처합니다.")
            # 끝 요소를 찾지 못한 경우, 시작 요소에서 2000px 아래로 캡처
            end_location = {'y': start_location['y'] + 2000}
            end_size = {'height': 0}
        else:
            end_location = end_element.location
            end_size = end_element.size
        
        # 시작 요소로 스크롤
        logger.info(f"시작 요소로 스크롤: {game_name}")
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'start'});", start_element)
        time.sleep(3)  # 스크롤 완료 대기
        
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
        end_location = end_element.location
        end_size = end_element.size
        
        logger.info(f"시작 요소 위치: x={start_location['x']}, y={start_location['y']}")
        logger.info(f"시작 요소 크기: width={start_size['width']}, height={start_size['height']}")
        logger.info(f"끝 요소 위치: x={end_location['x']}, y={end_location['y']}")
        logger.info(f"끝 요소 크기: width={end_size['width']}, height={end_size['height']}")
        
        # 캡처 영역 계산 (고정 크기: 1000 x 1800 - 우측 사이드바 제외)
        crop_width = 1000  # 너비를 1000px로 설정 (우측 사이드바 제외)
        crop_left = max(0, start_location['x'] - 100)  # 시작 요소에서 왼쪽으로 100px 여백
        crop_top = max(0, start_location['y'] - 100)  # 시작 요소 위쪽 100px 여유
        crop_right = min(img.width, crop_left + crop_width)  # 조정된 너비 적용
        
        # 고정 높이 1800px로 설정
        crop_bottom = min(img.height, crop_top + 1800)  # 시작점에서 1800px 아래까지
        
        # 최소 캡처 높이 보장 (최소 1800px)
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

def update_html_with_new_images(save_dir, logger):
    """새로 캡처된 이미지들을 HTML 파일에 업데이트"""
    try:
        html_file = 'aos_review.html'
        
        if not os.path.exists(html_file):
            logger.error(f"HTML 파일을 찾을 수 없습니다: {html_file}")
            return False
        
        # 오늘 날짜
        today = datetime.datetime.now().strftime('%Y%m%d')
        today_formatted = f"{today[:4]}-{today[4:6]}-{today[6:8]}"
        
        # HTML 파일 읽기
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        logger.info(f"HTML 파일을 읽었습니다: {html_file}")
        
        # BeautifulSoup으로 HTML 파싱
        soup = BeautifulSoup(content, 'html.parser')
        changes_made = 0
        
        # 1. 날짜 선택 드롭다운 업데이트
        date_select = soup.find('select', {'id': 'dateSelect'})
        if date_select:
            # 기존 옵션들에서 날짜 값 추출
            existing_dates = []
            for option in date_select.find_all('option'):
                value = option.get('value', '')
                if value and value not in existing_dates:
                    existing_dates.append(value)
            
            # 오늘 날짜가 없으면 첫 번째 옵션으로 추가
            if today not in existing_dates:
                new_option = soup.new_tag('option', value=today)
                new_option.string = today_formatted
                date_select.insert(0, new_option)
                changes_made += 1
                logger.info(f"날짜 선택 드롭다운에 새 날짜 추가: {today} ({today_formatted})")
            
            # 기존 selected 속성 제거
            for option in date_select.find_all('option', selected=True):
                del option['selected']
            
            # 오늘 날짜 옵션에 selected 추가
            today_option = date_select.find('option', {'value': today})
            if today_option:
                today_option['selected'] = 'selected'
                changes_made += 1
                logger.info(f"기본 선택 날짜를 {today}로 설정")
        
        # 2. availableDates 배열 업데이트
        script_tags = soup.find_all('script')
        for script in script_tags:
            if script.string and 'availableDates' in script.string:
                # availableDates 배열 찾기 및 업데이트
                # 패턴: const availableDates = [['20251112', ...]];
                pattern = r"const availableDates = \[(\[[^\]]+\])\];"
                match = re.search(pattern, script.string)
                
                if match:
                    # 중첩 배열에서 날짜 추출
                    inner_array = match.group(1)
                    dates_match = re.search(r"\[([^\]]+)\]", inner_array)
                    if dates_match:
                        dates_str = dates_match.group(1)
                        # 날짜 추출 (따옴표 제거)
                        dates = [d.strip().strip("'\"") for d in dates_str.split(',') if d.strip()]
                        
                        # 오늘 날짜가 없으면 추가
                        if today not in dates:
                            dates.insert(0, today)
                            # 평면 배열로 수정 (중첩 배열 제거)
                            new_dates_str = "['" + "', '".join(dates) + "']"
                            new_script_content = re.sub(
                                pattern,
                                f"const availableDates = [{new_dates_str}];",
                                script.string
                            )
                            script.string = new_script_content
                            changes_made += 1
                            logger.info(f"availableDates 배열 업데이트: {today} 추가됨 (총 {len(dates)}개 날짜)")
                else:
                    # 평면 배열 패턴도 시도
                    pattern_flat = r"const availableDates = \[([^\]]+)\];"
                    match_flat = re.search(pattern_flat, script.string)
                    if match_flat:
                        dates_str = match_flat.group(1)
                        dates = [d.strip().strip("'\"") for d in dates_str.split(',') if d.strip()]
                        
                        if today not in dates:
                            dates.insert(0, today)
                            new_dates_str = "['" + "', '".join(dates) + "']"
                            new_script_content = re.sub(
                                pattern_flat,
                                f"const availableDates = [{new_dates_str}];",
                                script.string
                            )
                            script.string = new_script_content
                            changes_made += 1
                            logger.info(f"availableDates 배열 업데이트: {today} 추가됨 (총 {len(dates)}개 날짜)")
                
                # 페이지 로드 시 기본 날짜 업데이트
                default_date_pattern = r"showDateContent\('([^']+)'\);"
                default_date_match = re.search(default_date_pattern, script.string)
                if default_date_match:
                    current_default = default_date_match.group(1)
                    if current_default != today:
                        new_script_content = re.sub(
                            default_date_pattern,
                            f"showDateContent('{today}');",
                            script.string
                        )
                        script.string = new_script_content
                        changes_made += 1
                        logger.info(f"기본 날짜 업데이트: {current_default} -> {today}")
                break
        
        # 변경사항이 있으면 파일에 저장
        if changes_made > 0:
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(str(soup))
            logger.info(f"총 {changes_made}개의 변경사항이 HTML 파일에 반영되었습니다.")
            logger.info(f"파일이 저장되었습니다: {html_file}")
            return True
        else:
            logger.info("변경할 내용이 없습니다. 모든 항목이 이미 최신 상태입니다.")
            return True
            
    except Exception as e:
        logger.error(f"HTML 업데이트 중 오류 발생: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def git_commit_and_push(logger, git_dir=None):
    """Git commit 및 push 자동화"""
    try:
        logger.info("=" * 50)
        logger.info("Git 작업 시작")
        
        # Git 작업 디렉토리 설정 (기본값: D:\aos_review)
        if git_dir is None:
            git_dir = r'D:\aos_review'
        
        # 디렉토리 존재 확인
        if not os.path.exists(git_dir):
            logger.warning(f"Git 작업 디렉토리가 존재하지 않습니다: {git_dir}")
            return False
        
        logger.info(f"Git 작업 디렉토리: {git_dir}")
        
        # Git이 설치되어 있는지 확인
        try:
            subprocess.run(['git', '--version'], 
                         capture_output=True, 
                         check=True, 
                         encoding='utf-8')
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.warning("Git이 설치되어 있지 않거나 PATH에 없습니다. Git 작업을 건너뜁니다.")
            return False
        
        # 지정된 디렉토리가 Git 저장소인지 확인
        try:
            subprocess.run(['git', 'status'], 
                         capture_output=True, 
                         check=True, 
                         cwd=git_dir,
                         encoding='utf-8')
        except subprocess.CalledProcessError:
            logger.warning(f"디렉토리가 Git 저장소가 아닙니다: {git_dir}")
            return False
        
        # 변경사항이 있는지 확인
        status_result = subprocess.run(['git', 'status', '--porcelain'], 
                                      capture_output=True, 
                                      check=True, 
                                      cwd=git_dir,
                                      encoding='utf-8')
        
        if not status_result.stdout.strip():
            logger.info("커밋할 변경사항이 없습니다.")
            return True
        
        logger.info("변경된 파일:")
        logger.info(status_result.stdout)
        
        # git add .
        logger.info("git add . 실행 중...")
        add_result = subprocess.run(['git', 'add', '.'], 
                                   capture_output=True, 
                                   check=True, 
                                   cwd=git_dir,
                                   encoding='utf-8')
        logger.info("git add 완료")
        
        # git commit
        commit_message = "Update and add new log files and scripts"
        logger.info(f"git commit 실행 중... (메시지: {commit_message})")
        commit_result = subprocess.run(['git', 'commit', '-m', commit_message], 
                                      capture_output=True, 
                                      check=True, 
                                      cwd=git_dir,
                                      encoding='utf-8')
        logger.info("git commit 완료")
        if commit_result.stdout:
            logger.info(commit_result.stdout)
        
        # git push origin master
        logger.info("git push origin master 실행 중...")
        push_result = subprocess.run(['git', 'push', 'origin', 'master'], 
                                    capture_output=True, 
                                    check=True, 
                                    cwd=git_dir,
                                    encoding='utf-8')
        logger.info("git push 완료")
        if push_result.stdout:
            logger.info(push_result.stdout)
        
        logger.info("Git 작업 성공!")
        logger.info("=" * 50)
        return True
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Git 작업 실패: {e}")
        if e.stdout:
            logger.error(f"stdout: {e.stdout}")
        if e.stderr:
            logger.error(f"stderr: {e.stderr}")
        logger.info("=" * 50)
        return False
    except Exception as e:
        logger.error(f"Git 작업 중 예상치 못한 오류 발생: {e}")
        import traceback
        logger.error(traceback.format_exc())
        logger.info("=" * 50)
        return False

def main():
    """메인 실행 함수"""
    # 로깅 설정
    logger = setup_logging()
    
    base_dir = os.getcwd()  # 현재 작업 디렉토리 사용
    today = datetime.datetime.now().strftime('%Y%m%d')
    save_dir = os.path.join(base_dir, today)
    
    logger.info("=" * 50)
    logger.info("자동 Google Play 리뷰 캡처 및 HTML 업데이트 시작")
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
        # 모든 게임 캡처
        success_count = 0
        
        for app_id, game_name in GAMES.items():
            logger.info(f"게임 캡처 시작: {game_name} ({app_id})")
            
            if capture_game_review_firefox(driver, app_id, game_name, save_dir, logger):
                logger.info(f"{game_name} 캡처 성공!")
                success_count += 1
            else:
                logger.error(f"{game_name} 캡처 실패")
            
            logger.info("=" * 50)
        
        # HTML 파일 업데이트
        logger.info("HTML 파일 업데이트 시작")
        html_updated = update_html_with_new_images(save_dir, logger)
        if html_updated:
            logger.info("HTML 파일 업데이트 성공!")
        else:
            logger.error("HTML 파일 업데이트 실패")
        
        logger.info("=" * 50)
        
        # Git commit 및 push (성공 여부와 관계없이 시도)
        # D:\aos_review 디렉토리에서 Git 작업 실행
        git_success = git_commit_and_push(logger, git_dir=r'D:\aos_review')
        
        if success_count == len(GAMES):
            logger.info("모든 게임 캡처 및 HTML 업데이트 성공!")
            if git_success:
                logger.info("Git 작업도 성공적으로 완료되었습니다!")
            logger.info("=" * 50)
            return True
        elif success_count > 0:
            logger.info(f"{success_count}/{len(GAMES)} 게임 캡처 성공!")
            if git_success:
                logger.info("Git 작업도 성공적으로 완료되었습니다!")
            logger.info("=" * 50)
            return True
        else:
            logger.error("모든 게임 캡처 실패")
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

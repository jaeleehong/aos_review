import os
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# 게임 정보 정의 (영문 이름으로 변경)
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

def setup_driver():
    """Chrome WebDriver 설정"""
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    
    driver = webdriver.Chrome(options=chrome_options)
    return driver

def create_folder_structure():
    """폴더 구조 생성"""
    today = datetime.now().strftime("%Y%m%d")
    base_path = r"D:\aos review"
    today_folder = os.path.join(base_path, today)
    
    if not os.path.exists(base_path):
        os.makedirs(base_path)
    if not os.path.exists(today_folder):
        os.makedirs(today_folder)
    
    return today_folder

def navigate_to_reviews(driver):
    """리뷰 섹션으로 이동"""
    try:
        # 페이지 하단으로 스크롤하여 리뷰 섹션 로드
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)
        
        # 다시 위로 스크롤
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(2)
        
        # 리뷰 탭이나 링크 찾기 시도
        review_selectors = [
            "//span[text()='리뷰']",
            "//a[text()='리뷰']",
            "//button[text()='리뷰']",
            "//span[contains(text(), '리뷰')]",
            "//a[contains(text(), '리뷰')]",
            "//button[contains(text(), '리뷰')]",
            "//span[text()='Reviews']",
            "//a[text()='Reviews']",
            "//button[text()='Reviews']"
        ]
        
        for selector in review_selectors:
            try:
                elements = driver.find_elements(By.XPATH, selector)
                for element in elements:
                    if element.is_displayed() and element.is_enabled():
                        print(f"리뷰 링크 발견: {element.text}")
                        element.click()
                        time.sleep(3)
                        return True
            except:
                continue
        
        # 리뷰 섹션으로 직접 스크롤
        print("리뷰 링크를 찾을 수 없어 직접 스크롤합니다.")
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight * 0.7);")
        time.sleep(2)
        
        return True
        
    except Exception as e:
        print(f"리뷰 섹션 이동 오류: {str(e)}")
        return False

def find_review_elements(driver):
    """리뷰 관련 요소들 찾기"""
    try:
        # 평점 표시 영역 찾기
        rating_selectors = [
            "//div[contains(@class, 'rating')]",
            "//div[contains(@class, 'score')]",
            "//div[contains(@class, 'stars')]",
            "//div[contains(@class, 'review-score')]",
            "//div[contains(@class, 'rating-bar')]",
            "//div[contains(@class, 'rating-info')]",
            "//div[contains(@class, 'rating')]//span",
            "//div[contains(@class, 'score')]//span",
            "//span[contains(@class, 'rating')]",
            "//span[contains(@class, 'score')]"
        ]
        
        rating_element = None
        for selector in rating_selectors:
            try:
                elements = driver.find_elements(By.XPATH, selector)
                for element in elements:
                    if element.is_displayed():
                        text = element.text.strip()
                        if text and ('★' in text or 'star' in text.lower() or 'rating' in text.lower()):
                            rating_element = element
                            print(f"평점 요소 발견: {text[:30]}...")
                            break
                if rating_element:
                    break
            except:
                continue
        
        # "리뷰 모두 보기" 링크 찾기
        view_all_selectors = [
            "//span[contains(text(), '리뷰 모두 보기')]",
            "//span[contains(text(), 'View all reviews')]",
            "//a[contains(text(), '리뷰 모두 보기')]",
            "//a[contains(text(), 'View all reviews')]",
            "//button[contains(text(), '리뷰 모두 보기')]",
            "//button[contains(text(), 'View all reviews')]",
            "//span[contains(text(), '모든 리뷰')]",
            "//a[contains(text(), '모든 리뷰')]",
            "//span[contains(text(), 'All reviews')]",
            "//a[contains(text(), 'All reviews')]",
            "//span[contains(text(), '리뷰') and contains(text(), '보기')]",
            "//a[contains(text(), '리뷰') and contains(text(), '보기')]"
        ]
        
        view_all_element = None
        for selector in view_all_selectors:
            try:
                elements = driver.find_elements(By.XPATH, selector)
                for element in elements:
                    if element.is_displayed():
                        view_all_element = element
                        print(f"'모든 리뷰' 요소 발견: {element.text}")
                        break
                if view_all_element:
                    break
            except:
                continue
        
        return rating_element, view_all_element
        
    except Exception as e:
        print(f"리뷰 요소 찾기 오류: {str(e)}")
        return None, None

def capture_review_section(driver, game_id, game_name, save_folder):
    """특정 게임의 리뷰 섹션 캡쳐"""
    try:
        # 구글 플레이 URL 구성
        url = f"https://play.google.com/store/apps/details?id={game_id}&hl=ko"
        print(f"접속 중: {game_name} ({url})")
        
        driver.get(url)
        time.sleep(5)  # 페이지 로딩 대기
        
        # 리뷰 섹션으로 이동
        if not navigate_to_reviews(driver):
            print(f"리뷰 섹션으로 이동할 수 없습니다: {game_name}")
            return False
        
        # 리뷰 요소들 찾기
        rating_element, view_all_element = find_review_elements(driver)
        
        if not rating_element or not view_all_element:
            print(f"리뷰 요소를 찾을 수 없습니다: {game_name}")
            return False
        
        # 캡쳐 영역 계산
        rating_location = rating_element.location
        rating_size = rating_element.size
        
        view_all_location = view_all_element.location
        view_all_size = view_all_element.size
        
        # 캡쳐 영역 설정 (평점 하단부터 리뷰 모두 보기까지)
        start_y = rating_location['y'] + rating_size['height']
        end_y = view_all_location['y'] + view_all_size['height']
        
        print(f"캡쳐 영역: Y={start_y} ~ {end_y}, 높이={end_y - start_y}")
        
        # 전체 페이지 스크린샷 찍기
        driver.save_screenshot("temp_screenshot.png")
        
        # PIL을 사용해서 특정 영역만 잘라내기
        from PIL import Image
        
        # 스크린샷 로드
        screenshot = Image.open("temp_screenshot.png")
        
        # 캡쳐 영역 설정 (전체 너비, 지정된 높이)
        width = screenshot.width
        height = end_y - start_y
        
        # 영역 잘라내기
        cropped_image = screenshot.crop((0, start_y, width, end_y))
        
        # 파일명 생성
        today = datetime.now().strftime("%Y%m%d")
        filename = f"{game_name}_{today}.png"
        filepath = os.path.join(save_folder, filename)
        
        # 이미지 저장
        cropped_image.save(filepath)
        
        # 임시 파일 삭제
        os.remove("temp_screenshot.png")
        
        print(f"캡쳐 완료: {filename}")
        return True
        
    except Exception as e:
        print(f"오류 발생 ({game_name}): {str(e)}")
        return False

def main():
    """메인 함수"""
    print("구글 플레이 리뷰 캡쳐 시작...")
    
    # 폴더 생성
    save_folder = create_folder_structure()
    print(f"저장 폴더: {save_folder}")
    
    # WebDriver 설정
    driver = setup_driver()
    
    try:
        success_count = 0
        total_games = len(GAMES)
        
        for game_id, game_name in GAMES.items():
            print(f"\n처리 중: {game_name} ({success_count + 1}/{total_games})")
            
            if capture_review_section(driver, game_id, game_name, save_folder):
                success_count += 1
            else:
                print(f"실패: {game_name}")
            
            # 다음 게임 처리 전 잠시 대기
            time.sleep(3)
        
        print(f"\n캡쳐 완료: {success_count}/{total_games} 게임")
        
    except Exception as e:
        print(f"전체 오류 발생: {str(e)}")
    
    finally:
        driver.quit()
        print("WebDriver 종료")

if __name__ == "__main__":
    main()

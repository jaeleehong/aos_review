import os
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
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

def scroll_to_reviews_section(driver):
    """리뷰 섹션으로 스크롤"""
    try:
        # 페이지 하단으로 스크롤하여 리뷰 섹션 로드
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)
        
        # 다시 위로 스크롤하여 리뷰 섹션 근처로
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight * 0.6);")
        time.sleep(2)
        
        # 리뷰 관련 텍스트가 있는지 확인
        page_text = driver.page_source.lower()
        if '리뷰' in page_text or 'review' in page_text:
            print("리뷰 섹션 발견")
            return True
        else:
            print("리뷰 섹션을 찾을 수 없습니다")
            return False
            
    except Exception as e:
        print(f"스크롤 오류: {str(e)}")
        return False

def find_review_boundaries(driver):
    """리뷰 섹션의 경계 찾기"""
    try:
        # 모든 텍스트 요소들 찾기
        all_elements = driver.find_elements(By.XPATH, "//*[text()]")
        
        rating_start_y = None
        review_end_y = None
        
        for element in all_elements:
            try:
                text = element.text.strip()
                if not text:
                    continue
                    
                location = element.location
                if not location:
                    continue
                
                # 평점 관련 텍스트 찾기 (시작점)
                if ('★' in text or 'star' in text.lower() or 'rating' in text.lower()) and rating_start_y is None:
                    rating_start_y = location['y']
                    print(f"평점 시작점 발견: {text[:30]}... (Y: {rating_start_y})")
                
                # "리뷰 모두 보기" 또는 유사한 텍스트 찾기 (끝점)
                if ('리뷰 모두 보기' in text or 'view all reviews' in text.lower() or 
                    '모든 리뷰' in text or 'all reviews' in text.lower()) and review_end_y is None:
                    review_end_y = location['y'] + element.size['height']
                    print(f"리뷰 끝점 발견: {text} (Y: {review_end_y})")
                    break
                    
            except Exception as e:
                continue
        
        return rating_start_y, review_end_y
        
    except Exception as e:
        print(f"경계 찾기 오류: {str(e)}")
        return None, None

def capture_review_section(driver, game_id, game_name, save_folder):
    """특정 게임의 리뷰 섹션 캡쳐"""
    try:
        # 구글 플레이 URL 구성
        url = f"https://play.google.com/store/apps/details?id={game_id}&hl=ko"
        print(f"접속 중: {game_name} ({url})")
        
        driver.get(url)
        time.sleep(5)  # 페이지 로딩 대기
        
        # 리뷰 섹션으로 스크롤
        if not scroll_to_reviews_section(driver):
            print(f"리뷰 섹션을 찾을 수 없습니다: {game_name}")
            return False
        
        # 리뷰 경계 찾기
        rating_start_y, review_end_y = find_review_boundaries(driver)
        
        if rating_start_y is None or review_end_y is None:
            print(f"리뷰 경계를 찾을 수 없습니다: {game_name}")
            # 기본값으로 페이지 중간 부분 캡쳐
            rating_start_y = 400
            review_end_y = 800
            print(f"기본값 사용: Y={rating_start_y} ~ {review_end_y}")
        
        # 캡쳐 영역 계산
        start_y = rating_start_y
        end_y = review_end_y
        
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
        
        # 영역이 유효한지 확인
        if height <= 0 or start_y < 0 or end_y > screenshot.height:
            print("캡쳐 영역이 유효하지 않습니다. 전체 페이지를 캡쳐합니다.")
            cropped_image = screenshot
        else:
            # 영역 잘라내기
            cropped_image = screenshot.crop((0, start_y, width, end_y))
        
        # 파일명 생성 (영문 이름 사용)
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

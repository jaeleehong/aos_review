import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

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

def analyze_page_structure(driver, game_id, game_name):
    """페이지 구조 분석"""
    try:
        url = f"https://play.google.com/store/apps/details?id={game_id}&hl=ko"
        print(f"\n=== {game_name} 페이지 분석 ===")
        print(f"URL: {url}")
        
        driver.get(url)
        time.sleep(5)
        
        # 페이지 제목 확인
        title = driver.title
        print(f"페이지 제목: {title}")
        
        # 리뷰 관련 모든 요소 찾기
        print("\n--- 리뷰 관련 요소들 ---")
        review_elements = driver.find_elements(By.XPATH, "//*[contains(text(), '리뷰') or contains(text(), 'Reviews') or contains(text(), 'review')]")
        
        for i, elem in enumerate(review_elements):
            try:
                tag_name = elem.tag_name
                text = elem.text.strip()
                class_name = elem.get_attribute("class")
                is_displayed = elem.is_displayed()
                
                if text and len(text) < 100:  # 텍스트가 있고 너무 길지 않은 것만
                    print(f"{i+1:2d}. {tag_name} (class: {class_name}, displayed: {is_displayed})")
                    print(f"     텍스트: {text}")
                    
                    # 클릭 가능한지 확인
                    try:
                        if elem.is_enabled():
                            print(f"     클릭 가능: 예")
                    except:
                        print(f"     클릭 가능: 확인 불가")
                    print()
            except Exception as e:
                print(f"{i+1:2d}. 요소 분석 실패: {str(e)}")
        
        # 평점 관련 요소들 찾기
        print("\n--- 평점 관련 요소들 ---")
        rating_elements = driver.find_elements(By.XPATH, "//*[contains(@class, 'rating') or contains(@class, 'score') or contains(@class, 'star')]")
        
        for i, elem in enumerate(rating_elements[:10]):  # 처음 10개만
            try:
                tag_name = elem.tag_name
                class_name = elem.get_attribute("class")
                text = elem.text.strip()
                is_displayed = elem.is_displayed()
                
                if is_displayed:
                    print(f"{i+1:2d}. {tag_name} (class: {class_name})")
                    if text:
                        print(f"     텍스트: {text[:50]}...")
                    print()
            except:
                continue
        
        # 페이지 소스에서 리뷰 관련 부분 확인
        print("\n--- 페이지 소스 분석 ---")
        page_source = driver.page_source
        
        # 리뷰 관련 키워드가 포함된 라인들 찾기
        lines = page_source.split('\n')
        review_lines = []
        for line in lines:
            if '리뷰' in line or 'review' in line.lower() or 'rating' in line.lower():
                if len(line.strip()) < 200:  # 너무 긴 라인은 제외
                    review_lines.append(line.strip())
        
        print(f"리뷰 관련 라인 {len(review_lines)}개 발견:")
        for i, line in enumerate(review_lines[:10]):  # 처음 10개만
            print(f"{i+1:2d}. {line}")
        
        return True
        
    except Exception as e:
        print(f"분석 중 오류 발생: {str(e)}")
        return False

def main():
    """메인 함수"""
    print("구글 플레이 페이지 구조 분석 시작...")
    
    # 테스트할 게임 (첫 번째 게임만)
    test_game = {
        "com.neowiz.games.newmatgo": "뉴맞고"
    }
    
    driver = setup_driver()
    
    try:
        for game_id, game_name in test_game.items():
            analyze_page_structure(driver, game_id, game_name)
            
            # 사용자 입력 대기
            input("\n계속하려면 Enter를 누르세요...")
            
    except Exception as e:
        print(f"전체 오류 발생: {str(e)}")
    
    finally:
        driver.quit()
        print("분석 완료")

if __name__ == "__main__":
    main()


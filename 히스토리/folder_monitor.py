#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
폴더 감시 및 HTML 자동 업데이트 스크립트
"""

import os
import time
import re
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class FolderMonitor(FileSystemEventHandler):
    def __init__(self, base_dir, html_file):
        self.base_dir = base_dir
        self.html_file = html_file
        self.last_update = {}
    
    def on_created(self, event):
        if event.is_directory:
            # 새 폴더가 생성되었을 때
            folder_name = os.path.basename(event.src_path)
            if folder_name.isdigit() and len(folder_name) == 8:  # YYYYMMDD 형식
                print(f"새 폴더 감지: {folder_name}")
                time.sleep(2)  # 파일 생성 완료 대기
                self.update_html_for_new_folder(folder_name)
    
    def on_moved(self, event):
        if event.is_directory:
            # 폴더가 이동되었을 때
            folder_name = os.path.basename(event.dest_path)
            if folder_name.isdigit() and len(folder_name) == 8:
                print(f"폴더 이동 감지: {folder_name}")
                time.sleep(2)
                self.update_html_for_new_folder(folder_name)
    
    def update_html_for_new_folder(self, folder_name):
        """새 폴더에 대한 HTML 업데이트"""
        folder_path = os.path.join(self.base_dir, folder_name)
        
        # 폴더 내 이미지 파일 확인
        if not os.path.exists(folder_path):
            return
        
        image_files = [f for f in os.listdir(folder_path) if f.endswith('.png')]
        if not image_files:
            return
        
        # 이미 업데이트된 폴더인지 확인
        if folder_name in self.last_update:
            return
        
        print(f"HTML 업데이트 시작: {folder_name} ({len(image_files)}개 이미지)")
        
        # 게임명 추출
        games = []
        for img_file in image_files:
            game_name = img_file.split('_')[0]
            if game_name not in games:
                games.append(game_name)
        
        # HTML 업데이트
        if self.update_html_file(folder_name, games):
            self.last_update[folder_name] = time.time()
            print(f"HTML 업데이트 완료: {folder_name}")
        else:
            print(f"HTML 업데이트 실패: {folder_name}")
    
    def update_html_file(self, new_date, new_images):
        """HTML 파일 업데이트"""
        try:
            with open(self.html_file, 'r', encoding='utf-8') as f:
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
            
            # 3. 새 날짜 콘텐츠 섹션 추가
            new_content_section = self.generate_content_section(new_date, new_images)
            
            # 첫 번째 date-content 섹션 앞에 삽입
            content = re.sub(r'(<div class="content-area">\s*)(<div class="date-content")', 
                            r'\1' + new_content_section + r'\n\n                \2', content)
            
            # 4. 파일 저장
            with open(self.html_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return True
            
        except Exception as e:
            print(f"HTML 업데이트 실패: {e}")
            return False
    
    def generate_content_section(self, date, images):
        """새 날짜의 콘텐츠 섹션 생성"""
        year = date[:4]
        month = date[4:6]
        day = date[6:8]
        
        # 이전 날짜 계산
        prev_date = self.get_previous_date(date)
        
        # 사업실별 게임 분류
        business_units = {
            "red": ["NewMatgo", "NewMatgoKakao", "Sudda", "SuddaKakao", "Original"],
            "blue": ["Poker", "PokerKakao", "ShowdownHoldem"],
            "brown": ["NewVegas"]
        }
        
        section = f'''                <div class="date-content" id="content-{date}" style="display: none;">
                    <div class="comparison-info">
                        <h3>📊 {year}년 {month}월 {day}일 리포트 (전주 대비)</h3>
                        <div class="comparison-dates">
                            <span class="prev-week-info">📅 전주: {prev_date[:4]}년 {prev_date[4:6]}월 {prev_date[6:8]}일</span>
                            <span class="current-week-info">📅 금주: {year}년 {month}월 {day}일</span>
                        </div>
                    </div>'''
        
        # 사업실별로 게임 그룹화
        for business_type, games in business_units.items():
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
                    section += self.generate_game_card(game, prev_date, date, business_type)
            
            section += '''
                        </div>
                    </div>'''
        
        section += '''
                </div>'''
        
        return section
    
    def generate_game_card(self, game, prev_date, current_date, business_type):
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
    
    def get_previous_date(self, current_date):
        """이전 날짜 계산"""
        folders = [f for f in os.listdir(self.base_dir) if os.path.isdir(os.path.join(self.base_dir, f)) and f.isdigit()]
        folders.sort(reverse=True)
        
        for folder in folders:
            if folder < current_date:
                return folder
        
        return current_date

def main():
    """메인 실행 함수"""
    base_dir = "D:\\aos review"
    html_file = os.path.join(base_dir, "구글 플레이_리뷰.html")
    
    if not os.path.exists(html_file):
        print(f"HTML 파일을 찾을 수 없습니다: {html_file}")
        return
    
    print(f"폴더 감시 시작: {base_dir}")
    print(f"HTML 파일: {html_file}")
    print("Ctrl+C로 종료")
    
    event_handler = FolderMonitor(base_dir, html_file)
    observer = Observer()
    observer.schedule(event_handler, base_dir, recursive=False)
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\n폴더 감시 종료")
    
    observer.join()

if __name__ == "__main__":
    main()




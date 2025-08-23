#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HTML 파일의 이미지 경로를 현재 폴더의 파일명으로 일괄 변경하는 스크립트
"""

import os
import re
from bs4 import BeautifulSoup

def update_html_images():
    """HTML 파일의 이미지 경로를 현재 폴더의 실제 파일명으로 업데이트"""
    
    # 파일명 매핑 (기존 파일명 -> 새로운 파일명)
    filename_mapping = {
        # 20250813 폴더 파일들
        'newmatgo_reviews_20250821_093324.png': 'NewMatgo_20250813.png',
        'newmatgo_kakao_reviews_20250821_093343.png': 'NewMatgoKakao_20250813.png',
        'original_reviews_20250821_093404.png': 'Original_20250813.png',
        'poker_reviews_20250821_093427.png': 'Poker_20250813.png',
        'poker_kakao_reviews_20250821_093451.png': 'PokerKakao_20250813.png',
        'seotda_reviews_20250821_093516.png': 'Sudda_20250813.png',
        'seotda_kakao_reviews_20250821_093536.png': 'SuddaKakao_20250813.png',
        'showdown_holdem_reviews_20250821_093556.png': 'ShowdownHoldem_20250813.png',
        'newvegas_reviews_20250821_093623.png': 'NewVegas_20250813.png',
        
        # 20250821 폴더 파일들
        'newmatgo_reviews_20250821_101132.png': 'NewMatgo_20250821.png',
        'newmatgo_kakao_reviews_20250821_101151.png': 'NewMatgoKakao_20250821.png',
        'original_reviews_20250821_101210.png': 'Original_20250821.png',
        'poker_reviews_20250821_101229.png': 'Poker_20250821.png',
        'poker_kakao_reviews_20250821_101249.png': 'PokerKakao_20250821.png',
        'seotda_reviews_20250821_101309.png': 'Sudda_20250821.png',
        'seotda_kakao_reviews_20250821_101329.png': 'SuddaKakao_20250821.png',
        'showdown_holdem_reviews_20250821_101347.png': 'ShowdownHoldem_20250821.png',
        'newvegas_reviews_20250821_101406.png': 'NewVegas_20250821.png',
        
        # 20250822 폴더 파일들 (이미 올바른 형식)
        'NewMatgo_20250822.png': 'NewMatgo_20250822.png',
        'NewMatgoKakao_20250822.png': 'NewMatgoKakao_20250822.png',
        'Original_20250822.png': 'Original_20250822.png',
        'Poker_20250822.png': 'Poker_20250822.png',
        'PokerKakao_20250822.png': 'PokerKakao_20250822.png',
        'Sudda_20250822.png': 'Sudda_20250822.png',
        'SuddaKakao_20250822.png': 'SuddaKakao_20250822.png',
        'ShowdownHoldem_20250822.png': 'ShowdownHoldem_20250822.png',
        'NewVegas_20250822.png': 'NewVegas_20250822.png'
    }
    
    html_file = '구글 플레이_리뷰.html'
    
    if not os.path.exists(html_file):
        print(f"오류: {html_file} 파일을 찾을 수 없습니다.")
        return
    
    try:
        # HTML 파일 읽기
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"HTML 파일을 읽었습니다: {html_file}")
        
        # 변경된 내용 추적
        changes_made = 0
        
        # 각 매핑에 대해 치환 수행
        for old_filename, new_filename in filename_mapping.items():
            # 정규식을 사용하여 경로 내의 파일명만 치환
            pattern = r'(["\'])([^"\']*' + re.escape(old_filename) + r')(["\'])'
            replacement = r'\1\2'.replace(old_filename, new_filename) + r'\3'
            
            new_content, count = re.subn(pattern, replacement, content)
            if count > 0:
                content = new_content
                changes_made += count
                print(f"변경됨: {old_filename} -> {new_filename} ({count}회)")
        
        # 변경사항이 있으면 파일에 저장
        if changes_made > 0:
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"\n총 {changes_made}개의 이미지 경로가 업데이트되었습니다.")
            print(f"파일이 저장되었습니다: {html_file}")
        else:
            print("변경할 이미지 경로가 없습니다.")
            
    except Exception as e:
        print(f"오류가 발생했습니다: {e}")

if __name__ == "__main__":
    print("HTML 이미지 경로 업데이트를 시작합니다...")
    update_html_images()
    print("완료되었습니다.")




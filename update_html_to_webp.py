#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HTML 파일에서 PNG 이미지 참조를 WebP로 변경하는 스크립트
"""

import re
import os
import logging

def setup_logging():
    """로깅 설정"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)

def update_html_to_webp(html_file):
    """HTML 파일에서 PNG 참조를 WebP로 변경"""
    try:
        # HTML 파일 읽기
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        logger.info(f"HTML 파일을 읽었습니다: {html_file}")
        
        # PNG를 WebP로 변경하는 정규식 패턴
        # 날짜 폴더 내의 PNG 파일들만 변경 (앱 아이콘은 제외)
        pattern = r'(src=")([^"]*\.png)(")'
        
        def replace_png_with_webp(match):
            full_path = match.group(2)
            # PNG를 WebP로 변경
            webp_path = full_path.replace('.png', '.webp')
            return f'{match.group(1)}{webp_path}{match.group(3)}'
        
        # 변경 수행
        new_content, count = re.subn(pattern, replace_png_with_webp, content)
        
        if count > 0:
            # 변경사항 저장
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            logger.info(f"총 {count}개의 PNG 참조를 WebP로 변경했습니다.")
            return True
        else:
            logger.info("변경할 PNG 참조가 없습니다.")
            return True
            
    except Exception as e:
        logger.error(f"HTML 업데이트 중 오류 발생: {e}")
        return False

def main():
    """메인 실행 함수"""
    global logger
    logger = setup_logging()
    
    html_file = '구글 플레이_리뷰.html'
    
    if not os.path.exists(html_file):
        logger.error(f"HTML 파일을 찾을 수 없습니다: {html_file}")
        return
    
    logger.info("HTML 파일의 PNG 참조를 WebP로 변경을 시작합니다.")
    
    success = update_html_to_webp(html_file)
    
    if success:
        logger.info("HTML 파일 업데이트가 완료되었습니다.")
    else:
        logger.error("HTML 파일 업데이트에 실패했습니다.")

if __name__ == "__main__":
    main()

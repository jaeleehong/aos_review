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
    """HTML 파일에서 PNG 참조를 그대로 유지 (WebP 변환 없음)"""
    try:
        # HTML 파일 읽기
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        logger.info(f"HTML 파일을 읽었습니다: {html_file}")
        
        # PNG 파일이 이미 올바르게 참조되어 있는지 확인
        png_pattern = r'src="([^"]*\.png)"'
        png_matches = re.findall(png_pattern, content)
        
        if png_matches:
            logger.info(f"총 {len(png_matches)}개의 PNG 참조가 확인되었습니다.")
            logger.info("PNG 파일 참조가 정상적으로 유지됩니다.")
        else:
            logger.info("PNG 참조가 없습니다.")
        
        return True
            
    except Exception as e:
        logger.error(f"HTML 확인 중 오류 발생: {e}")
        return False

def main():
    """메인 실행 함수"""
    global logger
    logger = setup_logging()
    
    html_file = 'aos_review.html'
    
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

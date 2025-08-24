#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
기존 PNG 파일들을 WebP로 변환하는 스크립트
"""

import os
import glob
from PIL import Image
import logging

def setup_logging():
    """로깅 설정"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)

def convert_png_to_webp(png_path, webp_path, quality=85):
    """PNG 파일을 WebP로 변환"""
    try:
        with Image.open(png_path) as img:
            # RGBA 모드인 경우 RGB로 변환 (WebP 호환성)
            if img.mode == 'RGBA':
                # 흰색 배경에 합성
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[-1])  # 알파 채널을 마스크로 사용
                img = background
            
            img.save(webp_path, 'WEBP', quality=quality)
            
        # 파일 크기 비교
        png_size = os.path.getsize(png_path)
        webp_size = os.path.getsize(webp_path)
        reduction = ((png_size - webp_size) / png_size) * 100
        
        return True, png_size, webp_size, reduction
    except Exception as e:
        return False, 0, 0, 0

def main():
    """메인 실행 함수"""
    logger = setup_logging()
    
    # 날짜별 폴더들 찾기
    date_folders = glob.glob("2025*")
    
    if not date_folders:
        logger.info("변환할 날짜 폴더를 찾을 수 없습니다.")
        return
    
    total_converted = 0
    total_size_reduction = 0
    
    for folder in date_folders:
        logger.info(f"처리 중: {folder}")
        
        # PNG 파일들 찾기
        png_files = glob.glob(os.path.join(folder, "*.png"))
        
        if not png_files:
            logger.info(f"{folder}에 PNG 파일이 없습니다.")
            continue
        
        folder_converted = 0
        folder_size_reduction = 0
        
        for png_file in png_files:
            # WebP 파일 경로 생성
            webp_file = png_file.replace('.png', '.webp')
            
            logger.info(f"변환 중: {png_file} -> {webp_file}")
            
            success, png_size, webp_size, reduction = convert_png_to_webp(png_file, webp_file)
            
            if success:
                folder_converted += 1
                folder_size_reduction += reduction
                logger.info(f"변환 성공: {png_size:,} bytes -> {webp_size:,} bytes ({reduction:.1f}% 감소)")
            else:
                logger.error(f"변환 실패: {png_file}")
        
        total_converted += folder_converted
        total_size_reduction += folder_size_reduction
        
        logger.info(f"{folder} 완료: {folder_converted}개 파일 변환, 평균 {folder_size_reduction/folder_converted:.1f}% 크기 감소")
    
    logger.info(f"전체 완료: {total_converted}개 파일 변환, 평균 {total_size_reduction/total_converted:.1f}% 크기 감소")

if __name__ == "__main__":
    main()

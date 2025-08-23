#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
매일 00시 10분에 자동 캡처를 실행하도록 스케줄러를 설정하는 스크립트
"""

import os
import subprocess
import sys

def setup_scheduler():
    """스케줄러 설정"""
    print("=" * 50)
    print("Google Play 리뷰 자동 캡처 스케줄러 설정")
    print("=" * 50)
    
    # 현재 디렉토리 경로
    current_dir = os.path.abspath(".")
    batch_file = os.path.join(current_dir, "daily_auto_capture.bat")
    
    # 배치 파일 존재 확인
    if not os.path.exists(batch_file):
        print(f"오류: {batch_file} 파일을 찾을 수 없습니다.")
        return False
    
    print(f"배치 파일 경로: {batch_file}")
    
    # 기존 스케줄러 작업 삭제 (있다면)
    try:
        print("기존 스케줄러 작업 삭제 중...")
        subprocess.run(["schtasks", "/delete", "/tn", "Google Play Review Auto Capture", "/f"], 
                      capture_output=True, text=True)
        print("기존 작업 삭제 완료")
    except:
        print("기존 작업이 없거나 삭제 실패 (무시)")
    
    # 새로운 스케줄러 작업 생성
    try:
        print("새로운 스케줄러 작업 생성 중...")
        
        # 스케줄러 명령어 구성
        cmd = [
            "schtasks", "/create", "/tn", "Google Play Review Auto Capture",
            "/tr", f'"{batch_file}"',
            "/sc", "daily",
            "/st", "00:10",
            "/f"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ 스케줄러 설정 성공!")
            print("=" * 50)
            print("설정된 작업:")
            print("- 작업 이름: Google Play Review Auto Capture")
            print("- 실행 시간: 매일 00:10")
            print("- 실행 파일: daily_auto_capture.bat")
            print("=" * 50)
            return True
        else:
            print("❌ 스케줄러 설정 실패")
            print(f"오류: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ 스케줄러 설정 중 오류 발생: {e}")
        return False

def check_scheduler():
    """스케줄러 상태 확인"""
    print("\n" + "=" * 50)
    print("현재 스케줄러 상태 확인")
    print("=" * 50)
    
    try:
        result = subprocess.run(["schtasks", "/query", "/tn", "Google Play Review Auto Capture"], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ 스케줄러 작업이 정상적으로 설정되어 있습니다.")
            print(result.stdout)
        else:
            print("❌ 스케줄러 작업을 찾을 수 없습니다.")
            
    except Exception as e:
        print(f"스케줄러 상태 확인 중 오류: {e}")

def main():
    """메인 함수"""
    print("Google Play 리뷰 자동 캡처 스케줄러 설정 도구")
    print("이 도구는 매일 00시 10분에 자동으로 리뷰를 캡처합니다.")
    print()
    
    # 관리자 권한 확인
    try:
        is_admin = subprocess.run(["net", "session"], capture_output=True).returncode == 0
        if not is_admin:
            print("⚠️  관리자 권한이 필요합니다.")
            print("관리자 권한으로 다시 실행해주세요.")
            input("계속하려면 Enter를 누르세요...")
    except:
        pass
    
    # 스케줄러 설정
    if setup_scheduler():
        # 상태 확인
        check_scheduler()
        
        print("\n" + "=" * 50)
        print("설정 완료!")
        print("=" * 50)
        print("이제 매일 00시 10분에 자동으로 실행됩니다.")
        print("로그는 logs 폴더에서 확인할 수 있습니다.")
        print("=" * 50)
    else:
        print("\n" + "=" * 50)
        print("설정 실패!")
        print("=" * 50)
        print("관리자 권한으로 다시 실행해보세요.")
        print("=" * 50)

if __name__ == "__main__":
    main()
    input("\nEnter를 누르면 종료됩니다...")

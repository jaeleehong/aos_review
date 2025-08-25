#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Windows 작업 스케줄러에 자동 캡처 작업을 등록하는 스크립트 (수정된 버전)
"""

import subprocess
import os
import sys
import getpass

def setup_windows_scheduler():
    """Windows 작업 스케줄러에 자동 캡처 작업을 등록"""
    
    # 현재 스크립트 경로
    current_dir = os.getcwd()
    batch_file = os.path.join(current_dir, "daily_auto_capture.bat")
    
    # 배치 파일이 존재하는지 확인
    if not os.path.exists(batch_file):
        print(f"오류: {batch_file} 파일을 찾을 수 없습니다.")
        return False
    
    # 현재 사용자 정보 가져오기
    current_user = getpass.getuser()
    
    # 작업 스케줄러 명령어 구성
    task_name = "AOS_Review_Auto_Capture"
    task_description = "매일 00:10에 AOS 리뷰 자동 캡처 및 GitHub 배포"
    
    # 기존 작업 삭제 (있다면)
    print("기존 작업 삭제 중...")
    subprocess.run([
        "schtasks", "/delete", "/tn", task_name, "/f"
    ], capture_output=True)
    
    # 새 작업 생성 (현재 사용자 계정으로)
    print("새 작업 생성 중...")
    cmd = [
        "schtasks", "/create", "/tn", task_name,
        "/tr", f'"{batch_file}"',
        "/sc", "daily",
        "/st", "00:10",
        "/ru", current_user,
        "/f"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ 작업 스케줄러 등록 성공!")
        print(f"작업 이름: {task_name}")
        print(f"실행 계정: {current_user}")
        print("실행 시간: 매일 00:10")
        print(f"실행 파일: {batch_file}")
        return True
    else:
        print("❌ 작업 스케줄러 등록 실패:")
        print(result.stderr)
        return False

def check_scheduler_status():
    """등록된 작업 상태 확인"""
    task_name = "AOS_Review_Auto_Capture"
    
    print("작업 스케줄러 상태 확인 중...")
    result = subprocess.run([
        "schtasks", "/query", "/tn", task_name
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ 등록된 작업 정보:")
        print(result.stdout)
        return True
    else:
        print("❌ 등록된 작업이 없습니다.")
        return False

def main():
    """메인 함수"""
    print("=" * 50)
    print("Windows 작업 스케줄러 설정 (수정된 버전)")
    print("=" * 50)
    
    # 관리자 권한 확인
    try:
        is_admin = subprocess.run([
            "net", "session"
        ], capture_output=True).returncode == 0
    except:
        is_admin = False
    
    if not is_admin:
        print("⚠️  관리자 권한이 필요합니다.")
        print("이 스크립트를 관리자 권한으로 실행해주세요.")
        return False
    
    # 작업 스케줄러 설정
    if setup_windows_scheduler():
        print("\n" + "=" * 50)
        check_scheduler_status()
        print("\n설정 완료! 매일 00:10에 자동으로 실행됩니다.")
        return True
    else:
        print("\n설정 실패!")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

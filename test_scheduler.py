#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
5분 후 테스트용 자동 캡처 스케줄러 설정
"""

import subprocess
import os
import sys
import getpass
from datetime import datetime, timedelta

def setup_test_scheduler():
    """5분 후에 테스트용 자동 캡처 작업을 등록"""
    
    # 현재 스크립트 경로
    current_dir = os.getcwd()
    batch_file = os.path.join(current_dir, "test_auto_capture.bat")
    
    # 배치 파일이 존재하는지 확인
    if not os.path.exists(batch_file):
        print(f"오류: {batch_file} 파일을 찾을 수 없습니다.")
        return False
    
    # 현재 사용자 정보 가져오기
    current_user = getpass.getuser()
    
    # 5분 후 시간 계산
    now = datetime.now()
    test_time = now + timedelta(minutes=5)
    test_time_str = test_time.strftime("%H:%M")
    
    # 작업 스케줄러 명령어 구성
    task_name = "AOS_Review_Test_Capture"
    task_description = f"테스트용 자동 캡처 - {test_time_str}에 실행"
    
    # 기존 작업 삭제 (있다면)
    print("기존 테스트 작업 삭제 중...")
    subprocess.run([
        "schtasks", "/delete", "/tn", task_name, "/f"
    ], capture_output=True)
    
    # 새 작업 생성 (5분 후 실행)
    print(f"새 테스트 작업 생성 중... (실행 시간: {test_time_str})")
    cmd = [
        "schtasks", "/create", "/tn", task_name,
        "/tr", f'"{batch_file}"',
        "/sc", "once",
        "/st", test_time_str,
        "/ru", current_user,
        "/f"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ 테스트 작업 스케줄러 등록 성공!")
        print(f"작업 이름: {task_name}")
        print(f"실행 계정: {current_user}")
        print(f"실행 시간: {test_time_str}")
        print(f"실행 파일: {batch_file}")
        return True
    else:
        print("❌ 테스트 작업 스케줄러 등록 실패:")
        print(result.stderr)
        return False

def check_test_scheduler_status():
    """등록된 테스트 작업 상태 확인"""
    task_name = "AOS_Review_Test_Capture"
    
    print("테스트 작업 스케줄러 상태 확인 중...")
    result = subprocess.run([
        "schtasks", "/query", "/tn", task_name
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ 등록된 테스트 작업 정보:")
        print(result.stdout)
        return True
    else:
        print("❌ 등록된 테스트 작업이 없습니다.")
        return False

def main():
    """메인 함수"""
    print("=" * 50)
    print("5분 후 테스트용 자동 캡처 스케줄러 설정")
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
    
    # 테스트 작업 스케줄러 설정
    if setup_test_scheduler():
        print("\n" + "=" * 50)
        check_test_scheduler_status()
        print("\n테스트 설정 완료! 5분 후에 자동으로 실행됩니다.")
        print("로그는 logs\\test_auto_deploy.log에서 확인할 수 있습니다.")
        return True
    else:
        print("\n테스트 설정 실패!")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

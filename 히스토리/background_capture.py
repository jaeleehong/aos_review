#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
백그라운드에서 실행되는 AOS 리뷰 캡처 스크립트
"""

import os
import sys
import subprocess
import time
from datetime import datetime

def run_background_capture():
    """백그라운드에서 캡처 실행"""
    
    # 현재 디렉토리 설정
    os.chdir("D:\\aos_review")
    
    # 로그 파일 설정
    log_file = f"logs/background_capture_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    os.makedirs("logs", exist_ok=True)
    
    try:
        # 백그라운드에서 캡처 실행
        print(f"[{datetime.now()}] 백그라운드 캡처 시작")
        
        # pythonw를 사용하여 백그라운드 실행
        process = subprocess.Popen([
            sys.executable.replace("python.exe", "pythonw.exe"),
            "auto_capture_and_update.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # 프로세스 완료 대기 (최대 30분)
        try:
            stdout, stderr = process.communicate(timeout=1800)
            print(f"[{datetime.now()}] 캡처 완료")
            
            # 로그 저장
            with open(log_file, "w", encoding="utf-8") as f:
                f.write(f"실행 시간: {datetime.now()}\n")
                f.write(f"종료 코드: {process.returncode}\n")
                if stdout:
                    f.write(f"출력: {stdout.decode('utf-8')}\n")
                if stderr:
                    f.write(f"오류: {stderr.decode('utf-8')}\n")
            
            return process.returncode == 0
            
        except subprocess.TimeoutExpired:
            process.kill()
            print(f"[{datetime.now()}] 캡처 시간 초과 (30분)")
            return False
            
    except Exception as e:
        print(f"[{datetime.now()}] 오류 발생: {e}")
        return False

def main():
    """메인 함수"""
    success = run_background_capture()
    
    if success:
        print("백그라운드 캡처 성공!")
    else:
        print("백그라운드 캡처 실패!")
    
    return success

if __name__ == "__main__":
    main()

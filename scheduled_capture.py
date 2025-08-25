#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
5분 후 자동 캡처, HTML 업데이트, GitHub 업데이트 스크립트
"""

import os
import datetime
import logging
import time
import subprocess
import sys
import shutil
import json

# ===== 설정 옵션 =====
CONFIG = {
    "wait_minutes": 5,           # 대기 시간 (분)
    "max_retries": 3,           # 최대 재시도 횟수
    "retry_delay": 30,          # 재시도 간격 (초)
    "create_backup": True,      # 백업 생성 여부
    "backup_dir": "backups",    # 백업 디렉토리
    "detailed_logging": True,   # 상세 로깅 여부
    "show_progress": True,      # 진행률 표시 여부
    "git_branch": "main",       # Git 브랜치
    "commit_prefix": "Auto update",  # 커밋 메시지 접두사
}

def setup_logging():
    """로깅 설정"""
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    
    log_file = os.path.join(log_dir, f"scheduled_capture_{datetime.datetime.now().strftime('%Y%m%d')}.log")
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def create_backup():
    """백업 생성"""
    logger = logging.getLogger(__name__)
    
    if not CONFIG["create_backup"]:
        return True
    
    try:
        backup_dir = CONFIG["backup_dir"]
        os.makedirs(backup_dir, exist_ok=True)
        
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f"backup_{timestamp}"
        backup_path = os.path.join(backup_dir, backup_name)
        
        # aos_review.html 백업
        if os.path.exists("aos_review.html"):
            shutil.copy2("aos_review.html", f"{backup_path}_aos_review.html")
            logger.info(f"aos_review.html 백업 생성: {backup_path}_aos_review.html")
        
        # 설정 백업
        config_backup = {
            "timestamp": timestamp,
            "config": CONFIG,
            "files": []
        }
        
        # 캡처된 이미지 파일들 백업
        for root, dirs, files in os.walk("."):
            for file in files:
                if file.endswith(('.png', '.jpg', '.jpeg')):
                    file_path = os.path.join(root, file)
                    backup_file_path = os.path.join(backup_path, file)
                    os.makedirs(os.path.dirname(backup_file_path), exist_ok=True)
                    shutil.copy2(file_path, backup_file_path)
                    config_backup["files"].append(file_path)
        
        # 설정 파일 저장
        with open(f"{backup_path}_config.json", 'w', encoding='utf-8') as f:
            json.dump(config_backup, f, ensure_ascii=False, indent=2)
        
        logger.info(f"백업 완료: {backup_path}")
        return True
        
    except Exception as e:
        logger.error(f"백업 생성 실패: {e}")
        return False

def run_auto_capture():
    """자동 캡처 및 HTML 업데이트 실행 (재시도 로직 포함)"""
    logger = logging.getLogger(__name__)
    
    for attempt in range(CONFIG["max_retries"]):
        try:
            logger.info("=" * 80)
            logger.info(f"자동 캡처 및 HTML 업데이트 시작 (시도 {attempt + 1}/{CONFIG['max_retries']})")
            logger.info("=" * 80)
            
            # auto_capture_and_update.py 실행
            result = subprocess.run([sys.executable, "auto_capture_and_update.py"], 
                                  capture_output=True, text=True, encoding='utf-8')
            
            if result.returncode == 0:
                logger.info("자동 캡처 및 HTML 업데이트 성공!")
                if CONFIG["detailed_logging"]:
                    logger.info("출력:")
                    logger.info(result.stdout)
                return True
            else:
                logger.error(f"자동 캡처 및 HTML 업데이트 실패! (시도 {attempt + 1})")
                logger.error("오류:")
                logger.error(result.stderr)
                
                if attempt < CONFIG["max_retries"] - 1:
                    logger.info(f"{CONFIG['retry_delay']}초 후 재시도...")
                    time.sleep(CONFIG["retry_delay"])
                else:
                    logger.error("최대 재시도 횟수 초과!")
                    return False
                    
        except Exception as e:
            logger.error(f"자동 캡처 실행 중 오류 발생 (시도 {attempt + 1}): {e}")
            if attempt < CONFIG["max_retries"] - 1:
                logger.info(f"{CONFIG['retry_delay']}초 후 재시도...")
                time.sleep(CONFIG["retry_delay"])
            else:
                return False
    
    return False

def git_update():
    """GitHub 업데이트 실행"""
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("=" * 80)
        logger.info("GitHub 업데이트 시작")
        logger.info("=" * 80)
        
        # 현재 시간으로 커밋 메시지 생성
        current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        commit_message = f"{CONFIG['commit_prefix']}: {current_time}"
        
        # Git 상태 확인
        logger.info("Git 상태 확인 중...")
        status_result = subprocess.run(["git", "status", "--porcelain"], 
                                     capture_output=True, text=True, encoding='utf-8')
        
        if not status_result.stdout.strip():
            logger.info("변경사항이 없습니다. GitHub 업데이트를 건너뜁니다.")
            return True
        
        # Git 명령어 실행
        commands = [
            ["git", "add", "."],
            ["git", "commit", "-m", commit_message],
            ["git", "push", "origin", CONFIG["git_branch"]]
        ]
        
        for cmd in commands:
            logger.info(f"실행 중: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
            
            if result.returncode == 0:
                logger.info(f"성공: {' '.join(cmd)}")
                if CONFIG["detailed_logging"] and result.stdout:
                    logger.info(f"출력: {result.stdout}")
            else:
                logger.error(f"실패: {' '.join(cmd)}")
                logger.error(f"오류: {result.stderr}")
                return False
        
        logger.info("GitHub 업데이트 완료!")
        return True
        
    except Exception as e:
        logger.error(f"GitHub 업데이트 중 오류 발생: {e}")
        return False

def show_progress_bar(current, total, prefix="진행률"):
    """진행률 표시"""
    if not CONFIG["show_progress"]:
        return
    
    bar_length = 50
    filled_length = int(round(bar_length * current / float(total)))
    percents = round(100.0 * current / float(total), 1)
    bar = '█' * filled_length + '-' * (bar_length - filled_length)
    
    print(f'\r{prefix}: |{bar}| {percents}% 완료', end='', flush=True)
    if current == total:
        print()

def main():
    """메인 실행 함수"""
    logger = setup_logging()
    
    logger.info("=" * 80)
    logger.info("자동 캡처 및 업데이트 스케줄러 시작")
    logger.info(f"설정: {json.dumps(CONFIG, ensure_ascii=False, indent=2)}")
    logger.info("=" * 80)
    
    # 대기 시간 설정
    wait_time = CONFIG["wait_minutes"] * 60
    logger.info(f"{CONFIG['wait_minutes']}분({wait_time}초) 대기 시작...")
    
    if CONFIG["show_progress"]:
        for i in range(wait_time, 0, -1):
            if i % 60 == 0:  # 1분마다 로그 출력
                minutes = i // 60
                logger.info(f"남은 시간: {minutes}분")
            show_progress_bar(wait_time - i, wait_time, "대기 중")
            time.sleep(1)
        print()  # 진행률 바 다음 줄
    else:
        for i in range(wait_time, 0, -1):
            if i % 60 == 0:  # 1분마다 로그 출력
                minutes = i // 60
                logger.info(f"남은 시간: {minutes}분")
            time.sleep(1)
    
    logger.info("대기 완료! 자동 캡처 및 업데이트 시작")
    
    # 0단계: 백업 생성
    if CONFIG["create_backup"]:
        logger.info("0단계: 백업 생성")
        backup_success = create_backup()
        if not backup_success:
            logger.warning("백업 생성 실패했지만 계속 진행합니다.")
    
    # 1단계: 자동 캡처 및 HTML 업데이트
    logger.info("1단계: 자동 캡처 및 HTML 업데이트")
    capture_success = run_auto_capture()
    
    if capture_success:
        # 2단계: GitHub 업데이트
        logger.info("2단계: GitHub 업데이트")
        git_success = git_update()
        
        if git_success:
            logger.info("=" * 80)
            logger.info("모든 작업 완료! 🎉")
            logger.info("=" * 80)
            
            # 완료 알림
            completion_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            logger.info(f"완료 시간: {completion_time}")
            
            # 요약 정보
            logger.info("작업 요약:")
            logger.info(f"- 대기 시간: {CONFIG['wait_minutes']}분")
            logger.info(f"- 캡처 성공: {'예' if capture_success else '아니오'}")
            logger.info(f"- GitHub 업데이트: {'성공' if git_success else '실패'}")
            logger.info(f"- 백업 생성: {'예' if CONFIG['create_backup'] else '아니오'}")
            
        else:
            logger.error("GitHub 업데이트 실패!")
    else:
        logger.error("자동 캡처 실패로 인해 GitHub 업데이트를 건너뜁니다.")

if __name__ == "__main__":
    main()

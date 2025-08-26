ㅛ#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
새벽 1시 자동 캡처 및 HTML 업데이트 스케줄러
"""

import os
import datetime
import logging
import time
import subprocess
import sys
import schedule
import signal
import atexit

def setup_logging():
    """로깅 설정"""
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    
    log_file = os.path.join(log_dir, f"daily_capture_{datetime.datetime.now().strftime('%Y%m%d')}.log")
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def signal_handler(signum, frame):
    """시그널 핸들러 - 안전한 종료"""
    logger = logging.getLogger(__name__)
    logger.info("스케줄러 종료 신호 수신. 안전하게 종료합니다...")
    sys.exit(0)

def cleanup():
    """정리 작업"""
    logger = logging.getLogger(__name__)
    logger.info("스케줄러 정리 작업 완료")

def run_daily_capture():
    """일일 캡처 및 HTML 업데이트 실행"""
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("=" * 80)
        logger.info("새벽 1시 자동 캡처 및 HTML 업데이트 시작")
        logger.info("=" * 80)
        
        # auto_capture_and_update.py 실행
        result = subprocess.run([sys.executable, "auto_capture_and_update.py"], 
                              capture_output=True, text=True, encoding='utf-8')
        
        if result.returncode == 0:
            logger.info("자동 캡처 및 HTML 업데이트 성공!")
            logger.info("출력:")
            logger.info(result.stdout)
            
            # GitHub 업데이트
            logger.info("GitHub 업데이트 시작")
            git_update_success = update_github()
            
            if git_update_success:
                logger.info("모든 작업 완료! 🎉")
            else:
                logger.error("GitHub 업데이트 실패!")
            
            return True
        else:
            logger.error("자동 캡처 및 HTML 업데이트 실패!")
            logger.error("오류:")
            logger.error(result.stderr)
            return False
            
    except Exception as e:
        logger.error(f"일일 캡처 실행 중 오류 발생: {e}")
        return False

def update_github():
    """GitHub 업데이트 실행"""
    logger = logging.getLogger(__name__)
    
    try:
        # 현재 시간으로 커밋 메시지 생성
        current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        commit_message = f"Daily auto update: {current_time}"
        
        # Git 명령어 실행
        commands = [
            ["git", "add", "aos_review.html"],
            ["git", "add", f"{datetime.datetime.now().strftime('%Y%m%d')}/"],
            ["git", "add", "auto_capture_and_update.py"],
            ["git", "commit", "-m", commit_message],
            ["git", "push", "origin", "master"]  # master 브랜치 사용
        ]
        
        for cmd in commands:
            logger.info(f"실행 중: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
            
            if result.returncode == 0:
                logger.info(f"성공: {' '.join(cmd)}")
                if result.stdout:
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

def check_next_run():
    """다음 실행 시간 확인 및 로깅"""
    logger = logging.getLogger(__name__)
    now = datetime.datetime.now()
    next_run = schedule.next_run()
    
    if next_run:
        time_until_next = next_run - now
        hours = int(time_until_next.total_seconds() // 3600)
        minutes = int((time_until_next.total_seconds() % 3600) // 60)
        logger.info(f"다음 실행까지 남은 시간: {hours}시간 {minutes}분")
    else:
        logger.warning("다음 실행 스케줄이 설정되지 않았습니다")

def main():
    """메인 실행 함수"""
    logger = setup_logging()
    
    # 시그널 핸들러 등록
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    atexit.register(cleanup)
    
    logger.info("=" * 80)
    logger.info("새벽 1시 자동 캡처 스케줄러 시작")
    logger.info(f"현재 시간: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 80)
    
    # 새벽 1시에 실행되도록 스케줄 등록
    schedule.every().day.at("01:00").do(run_daily_capture)
    
    logger.info("스케줄 등록 완료: 매일 새벽 1시 자동 캡처")
    check_next_run()
    logger.info("스케줄러가 백그라운드에서 실행 중입니다...")
    logger.info("종료하려면 Ctrl+C를 누르세요")
    
    # 스케줄러 실행
    while True:
        try:
            schedule.run_pending()
            time.sleep(60)  # 1분마다 체크
            
            # 매 시간마다 상태 로깅
            if datetime.datetime.now().minute == 0:
                logger.info(f"스케줄러 실행 중... 현재 시간: {datetime.datetime.now().strftime('%H:%M')}")
                check_next_run()
                
        except KeyboardInterrupt:
            logger.info("사용자에 의해 스케줄러가 중단되었습니다")
            break
        except Exception as e:
            logger.error(f"스케줄러 실행 중 오류 발생: {e}")
            time.sleep(60)  # 오류 발생 시 1분 대기 후 재시도

if __name__ == "__main__":
    main()



#!/usr/bin/env python3
"""
서버 로그 분석 대시보드 통합 실행 스크립트
- 로그 파일 자동 생성
- 실시간 로그 분석 (5초마다)
- Flask 웹 서버 실행
"""

import subprocess
import threading
import time
import sys
import os
import logging
import traceback
from pathlib import Path

# 로깅 설정
def setup_logging():
    """로깅 설정을 초기화합니다."""
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 통합 실행 로거 설정
    logger = logging.getLogger('dashboard_runner')
    logger.setLevel(logging.INFO)
    
    # 파일 핸들러 설정
    file_handler = logging.FileHandler(f'{log_dir}/dashboard_runner.log', encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    
    # 포맷터 설정
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    
    # 핸들러 추가
    logger.addHandler(file_handler)
    
    return logger

# 로거 초기화
logger = setup_logging()

# 전역 변수로 분석 중단 플래그 추가
analysis_running = True

def run_log_generator():
    """로그 파일 자동 생성 프로세스 실행"""
    try:
        logger.info("로그 파일 자동 생성 시작")
        print("🔄 로그 파일 자동 생성 시작...")
        
        subprocess.run([
            sys.executable, 
            "ServerLogAnalysis/generate_fresh_logs.py"
        ], check=True)
        
        logger.info("로그 파일 자동 생성 완료")
    except KeyboardInterrupt:
        logger.info("사용자에 의해 로그 생성이 중단되었습니다")
        print("⏹️ 로그 생성 중단됨")
    except subprocess.CalledProcessError as e:
        logger.error(f"로그 생성 프로세스 오류: {str(e)}\n{traceback.format_exc()}")
        print(f"❌ 로그 생성 오류: {e}")
    except Exception as e:
        logger.error(f"로그 생성 중 예상치 못한 오류: {str(e)}\n{traceback.format_exc()}")
        print(f"❌ 로그 생성 오류: {e}")

def run_continuous_analysis():
    """5초마다 지속적으로 로그 분석을 실행하는 함수"""
    global analysis_running
    try:
        logger.info("지속적 로그 분석 시작 (5초 간격)")
        print("�� 지속적 로그 분석 시작 (5초 간격)...")
        
        while analysis_running:
            try:
                logger.info("주기적 로그 분석 실행")
                subprocess.run([
                    sys.executable, 
                    "ServerLogAnalysis/log_analysis.py"
                ], check=True, timeout=10)  # 10초 타임아웃
                
                logger.info("주기적 로그 분석 완료")
                
                # 5초 대기
                time.sleep(5)
                
            except subprocess.TimeoutExpired:
                logger.warning("로그 분석 시간 초과, 다음 주기에서 재시도")
                continue
            except subprocess.CalledProcessError as e:
                logger.error(f"주기적 로그 분석 프로세스 오류: {str(e)}")
                time.sleep(5)  # 오류 발생 시에도 5초 대기
                continue
            except Exception as e:
                logger.error(f"주기적 로그 분석 중 예상치 못한 오류: {str(e)}")
                time.sleep(5)
                continue
                
    except KeyboardInterrupt:
        logger.info("사용자에 의해 지속적 로그 분석이 중단되었습니다")
        print("⏹️ 지속적 로그 분석 중단됨")
    except Exception as e:
        logger.error(f"지속적 로그 분석 중 치명적 오류: {str(e)}\n{traceback.format_exc()}")
        print(f"❌ 지속적 로그 분석 오류: {e}")

def run_log_analysis():
    """로그 분석 프로세스 실행 (단일 실행)"""
    try:
        logger.info("로그 분석 프로세스 시작")
        print("📊 로그 분석 프로세스 시작...")
        
        subprocess.run([
            sys.executable, 
            "ServerLogAnalysis/log_analysis.py"
        ], check=True)
        
        logger.info("로그 분석 프로세스 완료")
    except KeyboardInterrupt:
        logger.info("사용자에 의해 로그 분석이 중단되었습니다")
        print("⏹️ 로그 분석 중단됨")
    except subprocess.CalledProcessError as e:
        logger.error(f"로그 분석 프로세스 오류: {str(e)}\n{traceback.format_exc()}")
        print(f"❌ 로그 분석 오류: {e}")
    except Exception as e:
        logger.error(f"로그 분석 중 예상치 못한 오류: {str(e)}\n{traceback.format_exc()}")
        print(f"❌ 로그 분석 오류: {e}")

def run_flask_server():
    """Flask 웹 서버 실행"""
    try:
        logger.info("Flask 웹 서버 시작")
        print("🌐 Flask 웹 서버 시작...")
        
        subprocess.run([
            sys.executable, 
            "ServerLogAnalysis/app.py"
        ], check=True)
        
        logger.info("Flask 웹 서버 종료")
    except KeyboardInterrupt:
        logger.info("사용자에 의해 Flask 서버가 중단되었습니다")
        print("⏹️ Flask 서버 중단됨")
    except subprocess.CalledProcessError as e:
        logger.error(f"Flask 서버 프로세스 오류: {str(e)}\n{traceback.format_exc()}")
        print(f"❌ Flask 서버 오류: {e}")
    except Exception as e:
        logger.error(f"Flask 서버 중 예상치 못한 오류: {str(e)}\n{traceback.format_exc()}")
        print(f"❌ Flask 서버 오류: {e}")

def main():
    """메인 실행 함수"""
    global analysis_running
    try:
        logger.info("서버 로그 분석 대시보드 통합 실행 시작")
        print("🚀 서버 로그 분석 대시보드 통합 실행")
        print("=" * 50)
        
        # 현재 디렉토리 확인
        current_dir = Path.cwd()
        print(f"📁 현재 디렉토리: {current_dir}")
        logger.info(f"현재 디렉토리: {current_dir}")
        
        # 필요한 파일들 확인
        required_files = [
            "ServerLogAnalysis/generate_fresh_logs.py",
            "ServerLogAnalysis/log_analysis.py", 
            "ServerLogAnalysis/app.py"
        ]
        
        missing_files = []
        for file_path in required_files:
            if not Path(file_path).exists():
                missing_files.append(file_path)
                logger.error(f"필수 파일이 없습니다: {file_path}")
                print(f"❌ 필수 파일이 없습니다: {file_path}")
        
        if missing_files:
            logger.error(f"필수 파일 누락으로 인한 실행 중단: {missing_files}")
            return
        
        print("✅ 모든 필수 파일 확인 완료")
        logger.info("모든 필수 파일 확인 완료")
        
        # 로그 파일이 없으면 생성
        if not Path("server_sample.log").exists():
            logger.info("초기 로그 파일 생성 시작")
            print("📝 초기 로그 파일 생성 중...")
            try:
                subprocess.run([
                    sys.executable, 
                    "ServerLogAnalysis/generate_fresh_logs.py"
                ], check=True, timeout=30)  # 30초 타임아웃
                print("✅ 초기 로그 파일 생성 완료")
                logger.info("초기 로그 파일 생성 완료")
            except subprocess.TimeoutExpired:
                logger.error("로그 파일 생성 시간 초과")
                print("❌ 로그 파일 생성 시간 초과")
                return
            except subprocess.CalledProcessError as e:
                logger.error(f"로그 파일 생성 프로세스 오류: {str(e)}\n{traceback.format_exc()}")
                print(f"❌ 로그 파일 생성 오류: {e}")
                return
            except Exception as e:
                logger.error(f"로그 파일 생성 중 예상치 못한 오류: {str(e)}\n{traceback.format_exc()}")
                print(f"❌ 로그 파일 생성 오류: {e}")
                return
        
        print("\n🎯 서비스 시작 중...")
        print("📊 로그 자동 생성: 3초마다 새로운 로그 추가")
        print("🔍 실시간 분석: 5초마다 자동 로그 분석 및 그래프 갱신")
        print("🌐 웹 대시보드: http://127.0.0.1:5000/")
        print("\n⏹️ 중단하려면 Ctrl+C를 누르세요")
        print("=" * 50)
        logger.info("서비스 시작 준비 완료")
        
        try:
            # 백그라운드 스레드로 로그 생성 실행
            log_thread = threading.Thread(target=run_log_generator, daemon=True)
            log_thread.start()
            logger.info("로그 생성 스레드 시작")
            
            # 백그라운드 스레드로 지속적 분석 실행
            analysis_thread = threading.Thread(target=run_continuous_analysis, daemon=True)
            analysis_thread.start()
            logger.info("지속적 분석 스레드 시작")
            
            # 잠시 대기 후 Flask 서버 실행
            time.sleep(2)
            
            # Flask 서버 실행 (메인 스레드)
            run_flask_server()
            
        except KeyboardInterrupt:
            logger.info("사용자에 의해 프로그램이 중단되었습니다")
            print("\n\n⏹️ 프로그램 종료 중...")
            analysis_running = False  # 분석 중단 플래그 설정
            print("✅ 모든 프로세스가 안전하게 종료되었습니다.")
        except Exception as e:
            logger.error(f"서비스 실행 중 예상치 못한 오류: {str(e)}\n{traceback.format_exc()}")
            print(f"\n❌ 실행 중 오류 발생: {e}")
            
    except Exception as e:
        logger.error(f"메인 함수에서 치명적 오류: {str(e)}\n{traceback.format_exc()}")
        print(f"❌ 프로그램 실행 중 치명적 오류: {e}")

if __name__ == "__main__":
    main() 
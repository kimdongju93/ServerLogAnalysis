#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import random
import time
import logging
import os
import traceback
from datetime import datetime, timedelta

# 로깅 설정
def setup_logging():
    """로깅 설정을 초기화합니다."""
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 로그 생성 로거 설정
    logger = logging.getLogger('log_generator')
    logger.setLevel(logging.INFO)
    
    # 파일 핸들러 설정
    file_handler = logging.FileHandler(f'{log_dir}/log_generator.log', encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    
    # 포맷터 설정
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    
    # 핸들러 추가
    logger.addHandler(file_handler)
    
    return logger

# 로거 초기화
logger = setup_logging()

def generate_fresh_logs():
    """새로운 로그 파일을 생성하여 대시보드에서 변화를 명확히 볼 수 있도록 함"""
    
    try:
        logger.info("로그 생성 시작")
        
        # 로그 파일 경로
        log_file = "server_sample.log"
        
        # 엔드포인트 목록
        endpoints = [
            "/api/user/login",
            "/api/user/logout", 
            "/api/user/list",
            "/api/product/list",
            "/api/product/detail",
            "/api/order/create",
            "/api/order/cancel",
            "/api/admin/stats"
        ]
        
        # HTTP 메서드
        methods = ["GET", "POST", "PUT", "DELETE"]
        
        # 상태 코드 (더 다양한 에러 포함)
        status_codes = {
            "success": [200, 201, 204],
            "client_error": [400, 401, 403, 404],
            "server_error": [500, 502, 503]
        }
        
        print("새로운 로그 파일을 생성합니다...")
        print("대시보드에서 변화를 명확히 볼 수 있도록 다양한 패턴의 로그를 생성합니다.")
        logger.info("새로운 로그 파일 생성 시작")
        
        # 현재 시간부터 시작
        current_time = datetime.now()
        
        try:
            with open(log_file, 'w', encoding='utf-8') as f:
                # 초기 로그 생성 (100개)
                for i in range(100):
                    # 시간을 1분씩 증가
                    log_time = current_time + timedelta(minutes=i)
                    
                    endpoint = random.choice(endpoints)
                    method = random.choice(methods)
                    
                    # 상태 코드 분포 조정 (더 많은 에러 포함)
                    if random.random() < 0.7:  # 70% 성공
                        status = random.choice(status_codes["success"])
                        resp_time = random.randint(50, 300)
                    elif random.random() < 0.8:  # 20% 클라이언트 에러
                        status = random.choice(status_codes["client_error"])
                        resp_time = random.randint(50, 200)
                    else:  # 10% 서버 에러
                        status = random.choice(status_codes["server_error"])
                        resp_time = random.randint(200, 800)
                    
                    # 특정 엔드포인트는 더 느리게
                    if endpoint == "/api/admin/stats":
                        resp_time = random.randint(800, 1200)
                    
                    # 로그 라인 생성
                    log_line = f"{log_time.strftime('%Y-%m-%dT%H:%M:%SZ')} {method} {endpoint} {status} {resp_time}ms\n"
                    f.write(log_line)
            
            logger.info(f"초기 로그 100개 생성 완료: {log_file}")
            print(f"초기 로그 100개가 생성되었습니다: {log_file}")
        except Exception as e:
            logger.error(f"초기 로그 파일 생성 오류: {str(e)}\n{traceback.format_exc()}")
            raise
        
        print("이제 실시간 로그 추가를 시작합니다...")
        print("Ctrl+C를 눌러서 중단할 수 있습니다.")
        logger.info("실시간 로그 추가 시작")
        
        # 실시간 로그 추가
        try:
            while True:
                time.sleep(3)  # 3초마다 로그 추가
                
                log_time = datetime.now()
                endpoint = random.choice(endpoints)
                method = random.choice(methods)
                
                # 상태 코드 분포 조정
                if random.random() < 0.6:  # 60% 성공
                    status = random.choice(status_codes["success"])
                    resp_time = random.randint(50, 300)
                elif random.random() < 0.8:  # 25% 클라이언트 에러
                    status = random.choice(status_codes["client_error"])
                    resp_time = random.randint(50, 200)
                else:  # 15% 서버 에러
                    status = random.choice(status_codes["server_error"])
                    resp_time = random.randint(200, 800)
                
                # 특정 엔드포인트는 더 느리게
                if endpoint == "/api/admin/stats":
                    resp_time = random.randint(800, 1200)
                
                # 로그 라인 생성
                log_line = f"{log_time.strftime('%Y-%m-%dT%H:%M:%SZ')} {method} {endpoint} {status} {resp_time}ms\n"
                
                try:
                    with open(log_file, 'a', encoding='utf-8') as f:
                        f.write(log_line)
                    
                    print(f"추가: {log_time.strftime('%Y-%m-%dT%H:%M:%SZ')} {method} {endpoint} {status} {resp_time}ms")
                    logger.debug(f"로그 추가: {method} {endpoint} {status} {resp_time}ms")
                except Exception as e:
                    logger.error(f"로그 추가 중 오류: {str(e)}\n{traceback.format_exc()}")
                    print(f"로그 추가 중 오류: {str(e)}")
                
        except KeyboardInterrupt:
            logger.info("사용자에 의해 로그 생성이 중단되었습니다")
            print("\n로그 생성이 중단되었습니다.")
        except Exception as e:
            logger.error(f"실시간 로그 추가 중 오류: {str(e)}\n{traceback.format_exc()}")
            print(f"실시간 로그 추가 중 오류: {str(e)}")
            
    except Exception as e:
        logger.error(f"로그 생성 중 치명적 오류: {str(e)}\n{traceback.format_exc()}")
        print(f"로그 생성 중 오류가 발생했습니다: {str(e)}")

if __name__ == "__main__":
    generate_fresh_logs() 
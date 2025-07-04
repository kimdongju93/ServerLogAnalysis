import re
import pandas as pd
import traceback
import logging
import os
from datetime import datetime

# 로깅 설정
def setup_logging():
    """로깅 설정을 초기화합니다."""
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 로그 분석 로거 설정
    logger = logging.getLogger('log_analysis')
    logger.setLevel(logging.INFO)
    
    # 파일 핸들러 설정
    file_handler = logging.FileHandler(f'{log_dir}/log_analysis.log', encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    
    # 포맷터 설정
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    
    # 핸들러 추가
    logger.addHandler(file_handler)
    
    return logger

# 로거 초기화
logger = setup_logging()

# 로그 파일 경로
LOG_FILE = 'server_sample.log'

# 로그 파싱 함수
def parse_log_line(line):
    try:
        pattern = r"(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z) (\w+) (\S+) (\d{3}) (\d+)ms"
        match = re.match(pattern, line)
        if match:
            dt, method, endpoint, status, resp = match.groups()
            return {
                'datetime': pd.to_datetime(dt),
                'method': method,
                'endpoint': endpoint,
                'status': int(status),
                'resp_ms': int(resp)
            }
        return None
    except Exception as e:
        logger.error(f"로그 라인 파싱 오류: {line.strip()}, 오류: {str(e)}")
        return None

# 로그 파일 읽기 및 파싱
def load_log_to_df(log_file):
    try:
        if not os.path.exists(log_file):
            logger.error(f"로그 파일이 존재하지 않습니다: {log_file}")
            return pd.DataFrame()
        
        with open(log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        records = [parse_log_line(line) for line in lines]
        records = [r for r in records if r]
        df = pd.DataFrame(records)
        
        logger.info(f"로그 파일 로드 완료: {len(df)} 개의 레코드")
        return df
    except Exception as e:
        logger.error(f"로그 파일 로드 오류: {str(e)}\n{traceback.format_exc()}")
        return pd.DataFrame()

def main():
    try:
        logger.info("로그 분석 시작")
        print('로그 데이터 로드 중...')
        df = load_log_to_df(LOG_FILE)
        
        if df.empty:
            logger.warning("분석할 로그 데이터가 없습니다")
            print("분석할 로그 데이터가 없습니다")
            return
        
        print(f'총 요청 수: {len(df)}')
        logger.info(f"총 요청 수: {len(df)}")

        # 2. 트래픽 분포 분석 (시간별)
        try:
            df['hour'] = df['datetime'].dt.hour
            df['date'] = df['datetime'].dt.date
            hourly = df.groupby('hour').size()
            daily = df.groupby('date').size()

            print('\n[트래픽 분포]')
            print('시간별 요청 건수:')
            print(hourly)
            print('일별 요청 건수:')
            print(daily)
            logger.info("트래픽 분포 분석 완료")
        except Exception as e:
            logger.error(f"트래픽 분포 분석 오류: {str(e)}\n{traceback.format_exc()}")

        # 3. 엔드포인트별 사용 현황
        try:
            endpoint_stats = df.groupby('endpoint').agg(
                count=('endpoint', 'count'),
                avg_resp=('resp_ms', 'mean'),
                p90_resp=('resp_ms', lambda x: x.quantile(0.9))
            ).sort_values('count', ascending=False)

            print('\n[엔드포인트별 사용 현황]')
            print(endpoint_stats)
            logger.info("엔드포인트별 사용 현황 분석 완료")
        except Exception as e:
            logger.error(f"엔드포인트별 사용 현황 분석 오류: {str(e)}\n{traceback.format_exc()}")

        # 4. 상태 코드 분포
        try:
            status_cat = df['status'].apply(lambda x: f'{x//100}xx')
            df['status_cat'] = status_cat
            status_dist = status_cat.value_counts()

            print('\n[상태 코드 분포]')
            print(status_dist)
            logger.info("상태 코드 분포 분석 완료")
        except Exception as e:
            logger.error(f"상태 코드 분포 분석 오류: {str(e)}\n{traceback.format_exc()}")

        # 4xx, 5xx 집중 구간/엔드포인트
        try:
            for err_cat in ['4xx', '5xx']:
                err_df = df[df['status_cat'] == err_cat]
                if not err_df.empty:
                    print(f'\n[{err_cat} 에러 집중 구간/엔드포인트]')
                    print('시간대별:')
                    print(err_df.groupby('hour').size())
                    print('엔드포인트별:')
                    print(err_df['endpoint'].value_counts())
            logger.info("에러 집중 구간 분석 완료")
        except Exception as e:
            logger.error(f"에러 집중 구간 분석 오류: {str(e)}\n{traceback.format_exc()}")

        # 5. 성능 병목 분석
        try:
            slow_requests = df.sort_values('resp_ms', ascending=False).head(10)
            print('\n[응답시간 상위 10개 요청]')
            print(slow_requests[['datetime','method','endpoint','status','resp_ms']])

            slowest_ep = endpoint_stats['avg_resp'].idxmax()
            print(f'\n[가장 느린 엔드포인트] {slowest_ep}')
            print(endpoint_stats.loc[slowest_ep])
            logger.info("성능 병목 분석 완료")
        except Exception as e:
            logger.error(f"성능 병목 분석 오류: {str(e)}\n{traceback.format_exc()}")

        # 6. 추가 인사이트 예시: 특정 시간대 응답시간 급증
        try:
            hourly_resp = df.groupby('hour')['resp_ms'].mean()
            peak_hour = hourly_resp.idxmax()
            print(f'\n[추가 인사이트] 평균 응답시간이 가장 높은 시간대: {peak_hour}시, 평균 {hourly_resp[peak_hour]:.1f}ms')
            logger.info("추가 인사이트 분석 완료")
        except Exception as e:
            logger.error(f"추가 인사이트 분석 오류: {str(e)}\n{traceback.format_exc()}")

        # 7. 결과 요약 리포트 저장
        def save_report():
            try:
                # 1. 느린 엔드포인트
                slow_ep = slowest_ep
                slow_ep_stats = endpoint_stats.loc[slow_ep]
                slow_ep_avg = slow_ep_stats['avg_resp']
                slow_ep_p90 = slow_ep_stats['p90_resp']
                slow_ep_count = slow_ep_stats['count']

                # 2. 에러 집중 엔드포인트
                top_4xx_ep = df[df['status_cat'] == '4xx']['endpoint'].value_counts().head(3)
                top_5xx_ep = df[df['status_cat'] == '5xx']['endpoint'].value_counts().head(3)

                # 3. 트래픽 피크 시간대
                peak_hour = hourly_resp.idxmax()
                peak_hour_avg = hourly_resp.max()

                # 4. 에러율
                total = len(df)
                err_4xx = status_dist.get(4, 0) if isinstance(status_dist, dict) else status_dist.get('4xx', 0) if '4xx' in status_dist else status_dist.get(400, 0)
                err_5xx = status_dist.get(5, 0) if isinstance(status_dist, dict) else status_dist.get('5xx', 0) if '5xx' in status_dist else status_dist.get(500, 0)
                err_4xx_rate = (err_4xx / total * 100) if total else 0
                err_5xx_rate = (err_5xx / total * 100) if total else 0

                # 5. 인사이트 요약
                improvement_insight = (
                    f"- 가장 느린 엔드포인트: {slow_ep} (평균 {slow_ep_avg:.1f}ms, p90 {slow_ep_p90:.1f}ms, {slow_ep_count}건)\n"
                    f"  → DB 인덱스 추가, 캐싱, 쿼리 최적화, 비동기화 등을 고려하세요.\n"
                    f"- 4xx 에러 집중 엔드포인트: " + ', '.join([f"{ep}({cnt}건)" for ep, cnt in top_4xx_ep.items()]) + "\n"
                    f"  → 입력값 검증, 인증/권한 체크, API 사용법 안내 강화 필요\n"
                    f"- 5xx 에러 집중 엔드포인트: " + ', '.join([f"{ep}({cnt}건)" for ep, cnt in top_5xx_ep.items()]) + "\n"
                    f"  → 서버 예외처리, DB 연결/쿼리 오류, 외부 API 오류 등 점검 필요\n"
                    f"- 트래픽 피크 시간대: {peak_hour}시 (평균 응답 {peak_hour_avg:.1f}ms)\n"
                    f"- 4xx 에러율: {err_4xx_rate:.2f}% / 5xx 에러율: {err_5xx_rate:.2f}%\n"
                )

                with open('analysis_report.txt', 'w', encoding='utf-8') as f:
                    f.write('[개선 제안 및 인사이트]\n')
                    f.write('---\n')
                    f.write(f'{improvement_insight}\n')
                    f.write('\n')
                    # [LLM 활용 자연어 요약/이상탐지 프롬프트 샘플] 섹션만 기록
                    f.write('[LLM 활용 자연어 요약/이상탐지 프롬프트 샘플]\n')
                    f.write('---\n')
                    f.write('1. 리포트 자연어 요약 프롬프트:\n')
                    f.write('다음은 서버 로그 분석 결과 요약입니다.\n')
                    f.write('---\n')
                    f.write(f'{improvement_insight}\n')
                    f.write('---\n')
                    f.write('위 데이터를 바탕으로, 주요 문제점, 이상 징후, 개선 제안, 트래픽 특징을 관리자에게 보고하는 자연어 리포트를 작성해줘.\n')
                    f.write('\n')
                    f.write('2. 이상 패턴 탐지 프롬프트:\n')
                    f.write('아래는 최근 서버 로그 일부입니다.\n')
                    f.write('---\n')
                    f.write('로그 일부 샘플...\n')
                    f.write('---\n')
                    f.write('이 로그에서 평소와 다른 점, 이상 징후, 에러 집중 구간, 응답시간 급증 등 특이사항을 찾아서 요약해줘.\n')
                    f.write('\n')
                    f.write('3. 대시보드 자연어 설명 프롬프트:\n')
                    f.write('아래는 대시보드 주요 통계입니다.\n')
                    f.write('---\n')
                    f.write(f'{improvement_insight}\n')
                    f.write('---\n')
                    f.write('이 데이터를 바탕으로, 트래픽/에러/응답시간의 특징을 한눈에 알 수 있게 자연어로 설명해줘.\n')
            except Exception as e:
                logging.exception('리포트 저장 중 오류 발생: %s', e)
        
        save_report()

        print('\n분석 완료!')
        logger.info("로그 분석 완료")
        
    except Exception as e:
        err_msg = f"[분석 오류] {e}\n" + traceback.format_exc()
        print(err_msg)
        logger.error(f"로그 분석 중 치명적 오류: {str(e)}\n{traceback.format_exc()}")
        
        # 기존 오류 로그 파일에도 기록
        try:
            with open('analysis_error.log', 'a', encoding='utf-8') as f:
                f.write(f"{datetime.now()} - {err_msg}\n")
        except Exception as log_err:
            logger.error(f"오류 로그 파일 작성 실패: {str(log_err)}")

if __name__ == "__main__":
    main() 
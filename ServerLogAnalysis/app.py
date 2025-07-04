from flask import Flask, render_template, jsonify, send_from_directory
import re
import pandas as pd
from datetime import datetime
import os
import logging
import traceback

app = Flask(__name__, static_folder='static')

# 로깅 설정
def setup_logging():
    """로깅 설정을 초기화합니다."""
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Flask 앱 로거 설정
    app_logger = logging.getLogger('flask_app')
    app_logger.setLevel(logging.INFO)
    
    # 파일 핸들러 설정
    file_handler = logging.FileHandler(f'{log_dir}/flask_app.log', encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    
    # 포맷터 설정
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    
    # 핸들러 추가
    app_logger.addHandler(file_handler)
    
    return app_logger

# 로거 초기화
logger = setup_logging()

# 로그 파일 경로 (프로젝트 루트의 server_sample.log)
LOG_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'server_sample.log')

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
            logger.warning(f"로그 파일이 존재하지 않습니다: {log_file}")
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

@app.route('/')
def dashboard():
    try:
        logger.info("대시보드 페이지 요청")
        return render_template('dashboard.html')
    except Exception as e:
        logger.error(f"대시보드 렌더링 오류: {str(e)}\n{traceback.format_exc()}")
        return "대시보드를 불러올 수 없습니다.", 500

@app.route('/api/stats')
def get_stats():
    try:
        logger.info("통계 API 요청")
        df = load_log_to_df(LOG_FILE)
        
        if df.empty:
            logger.warning("통계 계산을 위한 데이터가 없습니다")
            return jsonify({
                'total_requests': 0,
                'avg_response_time': 0,
                'success_rate': 0,
                'error_rate': 0
            })
        
        # 기본 통계
        total_requests = len(df)
        avg_response_time = df['resp_ms'].mean()
        
        # 성공률과 에러율 계산
        status_cat = df['status'].apply(lambda x: f'{x//100}xx')
        status_dist = status_cat.value_counts()
        
        success_count = status_dist.get('2xx', 0)
        error_count = status_dist.get('4xx', 0) + status_dist.get('5xx', 0)
        
        success_rate = (success_count / total_requests * 100) if total_requests > 0 else 0
        error_rate = (error_count / total_requests * 100) if total_requests > 0 else 0
        
        logger.info(f"통계 계산 완료: 총 요청 {total_requests}개")
        return jsonify({
            'total_requests': total_requests,
            'avg_response_time': round(avg_response_time, 2),
            'success_rate': round(success_rate, 2),
            'error_rate': round(error_rate, 2)
        })
    except Exception as e:
        logger.error(f"통계 API 오류: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'error': '통계를 계산할 수 없습니다'}), 500

@app.route('/api/chart-data')
def get_chart_data():
    try:
        logger.info("차트 데이터 API 요청")
        df = load_log_to_df(LOG_FILE)
        if df.empty:
            logger.warning("차트 데이터를 위한 데이터가 없습니다")
            return jsonify({"error": "No data"})

        # 시간별 요청 건수
        hourly = df.groupby(df['datetime'].dt.hour).size()
        hourly_labels = [int(x) for x in hourly.index.tolist()]
        hourly_data = [int(x) for x in hourly.values.tolist()]

        # 상태 코드 분포
        status_counts = df['status'].apply(lambda x: f"{x//100}xx").value_counts().sort_index()
        status_labels = [str(x) for x in status_counts.index.tolist()]
        status_data = [int(x) for x in status_counts.values.tolist()]

        # 엔드포인트별 호출수
        endpoint_counts = df['endpoint'].value_counts()
        endpoint_labels = [str(x) for x in endpoint_counts.index.tolist()]
        endpoint_data = [int(x) for x in endpoint_counts.values.tolist()]

        # 엔드포인트별 평균 응답시간
        endpoint_avg_resp = df.groupby('endpoint')['resp_ms'].mean()
        endpoint_avg_labels = [str(x) for x in endpoint_avg_resp.index.tolist()]
        endpoint_avg_data = [float(x) for x in endpoint_avg_resp.values.tolist()]

        # 모든 값이 기본 타입인지 재확인 (혹시 모를 numpy 타입 방지)
        def to_py(val):
            if hasattr(val, 'item'):
                return val.item()
            return val
        hourly_labels = [to_py(x) for x in hourly_labels]
        hourly_data = [to_py(x) for x in hourly_data]
        status_labels = [to_py(x) for x in status_labels]
        status_data = [to_py(x) for x in status_data]
        endpoint_labels = [to_py(x) for x in endpoint_labels]
        endpoint_data = [to_py(x) for x in endpoint_data]
        endpoint_avg_labels = [to_py(x) for x in endpoint_avg_labels]
        endpoint_avg_data = [to_py(x) for x in endpoint_avg_data]

        logger.info("차트 데이터 생성 완료")
        return jsonify({
            "hourly": {"labels": hourly_labels, "data": hourly_data},
            "status": {"labels": status_labels, "data": status_data},
            "endpoint": {"labels": endpoint_labels, "data": endpoint_data},
            "endpoint_avg": {"labels": endpoint_avg_labels, "data": endpoint_avg_data}
        })
    except Exception as e:
        logger.error(f"차트 데이터 API 오류: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'error': '차트 데이터를 생성할 수 없습니다'}), 500

@app.route('/api/slow-requests')
def get_slow_requests():
    try:
        logger.info("느린 요청 API 요청")
        df = load_log_to_df(LOG_FILE)
        
        if df.empty:
            logger.warning("느린 요청 데이터가 없습니다")
            return jsonify([])
        
        # 느린 요청 (상위 5개)
        slow_requests = df.nlargest(5, 'resp_ms')[['datetime', 'method', 'endpoint', 'status', 'resp_ms']]
        slow_requests_list = []
        for _, row in slow_requests.iterrows():
            slow_requests_list.append({
                'datetime': row['datetime'].strftime('%H:%M:%S'),
                'method': row['method'],
                'endpoint': row['endpoint'],
                'status': row['status'],
                'resp_ms': row['resp_ms']
            })
        
        logger.info(f"느린 요청 데이터 생성 완료: {len(slow_requests_list)}개")
        return jsonify(slow_requests_list)
    except Exception as e:
        logger.error(f"느린 요청 API 오류: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'error': '느린 요청 데이터를 가져올 수 없습니다'}), 500

@app.route('/api/recent-requests')
def get_recent_requests():
    try:
        logger.info("최근 요청 API 요청")
        df = load_log_to_df(LOG_FILE)
        
        if df.empty:
            logger.warning("최근 요청 데이터가 없습니다")
            return jsonify([])
        
        # 최근 요청 (최근 10개)
        recent_requests = df.nlargest(10, 'datetime')[['datetime', 'method', 'endpoint', 'status']]
        recent_requests_list = []
        for _, row in recent_requests.iterrows():
            recent_requests_list.append({
                'datetime': row['datetime'].strftime('%H:%M:%S'),
                'method': row['method'],
                'endpoint': row['endpoint'],
                'status': row['status']
            })
        
        logger.info(f"최근 요청 데이터 생성 완료: {len(recent_requests_list)}개")
        return jsonify(recent_requests_list)
    except Exception as e:
        logger.error(f"최근 요청 API 오류: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'error': '최근 요청 데이터를 가져올 수 없습니다'}), 500

@app.route('/api/report')
def get_report():
    try:
        logger.info("리포트 API 요청")
        report_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'analysis_report.txt')
        if not os.path.exists(report_path):
            logger.warning("분석 리포트 파일이 존재하지 않습니다")
            return '분석 리포트가 아직 생성되지 않았습니다.'
        with open(report_path, 'r', encoding='utf-8') as f:
            content = f.read()
        logger.info("리포트 파일 읽기 완료")
        return content
    except Exception as e:
        logger.error(f"리포트 API 오류: {str(e)}\n{traceback.format_exc()}")
        return f'리포트 파일을 읽을 수 없습니다. 오류: {str(e)}'

if __name__ == '__main__':
    try:
        logger.info("Flask 서버를 시작합니다...")
        print("Flask 서버를 시작합니다...")
        print("대시보드 접속: http://127.0.0.1:5000/")
        app.run(debug=True, host='0.0.0.0', port=5000)
    except Exception as e:
        logger.error(f"Flask 서버 시작 오류: {str(e)}\n{traceback.format_exc()}")
        print(f"서버 시작 중 오류가 발생했습니다: {str(e)}") 
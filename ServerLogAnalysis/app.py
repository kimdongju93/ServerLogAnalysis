from flask import Flask, render_template, jsonify, send_from_directory
import re
import pandas as pd
from datetime import datetime
import os

app = Flask(__name__, static_folder='static')

# 로그 파일 경로
LOG_FILE = 'server_sample.log'

# 로그 파싱 함수
def parse_log_line(line):
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

# 로그 파일 읽기 및 파싱
def load_log_to_df(log_file):
    if not os.path.exists(log_file):
        return pd.DataFrame()
    
    with open(log_file, 'r') as f:
        lines = f.readlines()
    records = [parse_log_line(line) for line in lines]
    records = [r for r in records if r]
    df = pd.DataFrame(records)
    return df

@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/api/stats')
def get_stats():
    df = load_log_to_df(LOG_FILE)
    
    if df.empty:
        return jsonify({
            'total_requests': 0,
            'endpoint_stats': {},
            'status_distribution': {'2xx': 0, '4xx': 0, '5xx': 0},
            'slow_requests': [],
            'recent_requests': []
        })
    
    # 엔드포인트별 통계
    endpoint_stats = df.groupby('endpoint').agg(
        count=('endpoint', 'count'),
        avg_resp=('resp_ms', 'mean')
    ).to_dict('index')
    
    # 상태 코드 분포
    status_cat = df['status'].apply(lambda x: f'{x//100}xx')
    status_dist = status_cat.value_counts().to_dict()
    
    # 느린 요청 (상위 5개)
    slow_requests = df.nlargest(5, 'resp_ms')[['datetime', 'method', 'endpoint', 'status', 'resp_ms']]
    slow_requests_list = []
    for _, row in slow_requests.iterrows():
        slow_requests_list.append({
            'datetime': row['datetime'].strftime('%Y-%m-%d %H:%M:%S'),
            'method': row['method'],
            'endpoint': row['endpoint'],
            'status': row['status'],
            'resp_ms': row['resp_ms']
        })
    
    # 최근 요청 (최근 10개)
    recent_requests = df.nlargest(10, 'datetime')[['datetime', 'method', 'endpoint', 'status', 'resp_ms']]
    recent_requests_list = []
    for _, row in recent_requests.iterrows():
        recent_requests_list.append({
            'datetime': row['datetime'].strftime('%Y-%m-%d %H:%M:%S'),
            'method': row['method'],
            'endpoint': row['endpoint'],
            'status': row['status'],
            'resp_ms': row['resp_ms']
        })
    
    return jsonify({
        'total_requests': len(df),
        'endpoint_stats': endpoint_stats,
        'status_distribution': status_dist,
        'slow_requests': slow_requests_list,
        'recent_requests': recent_requests_list
    })

@app.route('/api/graphs')
def get_graphs():
    # 기존에 생성된 그래프 파일들의 경로를 반환
    return jsonify({
        'hourly_traffic': '/static/hourly_traffic.png',
        'status_distribution': '/static/status_code_pie.png',
        'endpoint_counts': '/static/endpoint_count.png',
        'endpoint_avg_resp': '/static/endpoint_avg_resp.png'
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 
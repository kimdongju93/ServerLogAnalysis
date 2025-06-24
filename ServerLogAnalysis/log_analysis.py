import re
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

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
    with open(log_file, 'r') as f:
        lines = f.readlines()
    records = [parse_log_line(line) for line in lines]
    records = [r for r in records if r]
    df = pd.DataFrame(records)
    return df

def plot_and_save(fig, filename):
    fig.tight_layout()
    fig.savefig(filename)
    plt.close(fig)

# 1. 데이터 로드
print('로그 데이터 로드 중...')
df = load_log_to_df(LOG_FILE)
print(f'총 요청 수: {len(df)}')

# 2. 트래픽 분포 분석 (시간별)
df['hour'] = df['datetime'].dt.hour
df['date'] = df['datetime'].dt.date
hourly = df.groupby('hour').size()
daily = df.groupby('date').size()

fig1, ax1 = plt.subplots()
hourly.plot(kind='bar', ax=ax1)
ax1.set_title('시간별 요청 건수')
ax1.set_xlabel('Hour')
ax1.set_ylabel('Request Count')
plot_and_save(fig1, 'hourly_traffic.png')

fig2, ax2 = plt.subplots()
daily.plot(kind='bar', ax=ax2)
ax2.set_title('일별 요청 건수')
ax2.set_xlabel('Date')
ax2.set_ylabel('Request Count')
plot_and_save(fig2, 'daily_traffic.png')

print('\n[트래픽 분포]')
print('시간별 요청 건수:')
print(hourly)
print('일별 요청 건수:')
print(daily)

# 3. 엔드포인트별 사용 현황
endpoint_stats = df.groupby('endpoint').agg(
    count=('endpoint', 'count'),
    avg_resp=('resp_ms', 'mean'),
    p90_resp=('resp_ms', lambda x: x.quantile(0.9))
).sort_values('count', ascending=False)

fig3, ax3 = plt.subplots(figsize=(10,5))
endpoint_stats['count'].plot(kind='bar', ax=ax3)
ax3.set_title('엔드포인트별 호출수')
ax3.set_ylabel('호출수')
plot_and_save(fig3, 'endpoint_count.png')

fig4, ax4 = plt.subplots(figsize=(10,5))
endpoint_stats['avg_resp'].plot(kind='bar', ax=ax4, color='orange')
ax4.set_title('엔드포인트별 평균 응답시간(ms)')
ax4.set_ylabel('평균 응답시간(ms)')
plot_and_save(fig4, 'endpoint_avg_resp.png')

print('\n[엔드포인트별 사용 현황]')
print(endpoint_stats)

# 4. 상태 코드 분포
status_cat = df['status'].apply(lambda x: f'{x//100}xx')
df['status_cat'] = status_cat
status_dist = status_cat.value_counts()

fig5, ax5 = plt.subplots()
status_dist.plot(kind='pie', autopct='%1.1f%%', ax=ax5)
ax5.set_ylabel('')
ax5.set_title('상태 코드 분포')
plot_and_save(fig5, 'status_code_pie.png')

print('\n[상태 코드 분포]')
print(status_dist)

# 4xx, 5xx 집중 구간/엔드포인트
for err_cat in ['4xx', '5xx']:
    err_df = df[df['status_cat'] == err_cat]
    if not err_df.empty:
        print(f'\n[{err_cat} 에러 집중 구간/엔드포인트]')
        print('시간대별:')
        print(err_df.groupby('hour').size())
        print('엔드포인트별:')
        print(err_df['endpoint'].value_counts())

# 5. 성능 병목 분석
slow_requests = df.sort_values('resp_ms', ascending=False).head(10)
print('\n[응답시간 상위 10개 요청]')
print(slow_requests[['datetime','method','endpoint','status','resp_ms']])

slowest_ep = endpoint_stats['avg_resp'].idxmax()
print(f'\n[가장 느린 엔드포인트] {slowest_ep}')
print(endpoint_stats.loc[slowest_ep])

# 6. 추가 인사이트 예시: 특정 시간대 응답시간 급증
hourly_resp = df.groupby('hour')['resp_ms'].mean()
peak_hour = hourly_resp.idxmax()
print(f'\n[추가 인사이트] 평균 응답시간이 가장 높은 시간대: {peak_hour}시, 평균 {hourly_resp[peak_hour]:.1f}ms')

# 7. (선택) 결과 요약 리포트 저장
def save_report():
    with open('analysis_report.txt', 'w', encoding='utf-8') as f:
        f.write('==== 서버 로그 분석 요약 ====' + '\n')
        f.write(f'총 요청 수: {len(df)}\n')
        f.write('\n[시간별 요청 건수]\n')
        f.write(str(hourly) + '\n')
        f.write('\n[엔드포인트별 통계]\n')
        f.write(str(endpoint_stats) + '\n')
        f.write('\n[상태 코드 분포]\n')
        f.write(str(status_dist) + '\n')
        f.write(f'\n[가장 느린 엔드포인트] {slowest_ep}\n')
        f.write(str(endpoint_stats.loc[slowest_ep]) + '\n')
        f.write(f'\n[평균 응답시간이 가장 높은 시간대] {peak_hour}시, 평균 {hourly_resp[peak_hour]:.1f}ms\n')
    print('분석 요약 리포트(analysis_report.txt) 저장 완료!')

save_report()

print('\n분석 및 시각화 결과가 파일로 저장되었습니다.') 
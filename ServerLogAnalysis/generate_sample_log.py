import random
from datetime import datetime, timedelta

methods = ['GET', 'POST', 'PUT', 'DELETE']
endpoints = [
    '/api/user/list', '/api/user/login', '/api/user/logout', '/api/product/list',
    '/api/product/detail', '/api/order/create', '/api/order/cancel', '/api/admin/stats'
]
status_codes = [200, 201, 204, 400, 401, 403, 404, 500, 502, 503]

start_time = datetime(2025, 5, 1, 0, 0, 0)
lines = []
for i in range(1000):
    # 시간은 1~3분 간격으로 증가
    dt = start_time + timedelta(minutes=random.randint(0, 3) * i)
    method = random.choice(methods)
    endpoint = random.choices(endpoints, weights=[20, 15, 5, 20, 10, 10, 5, 5])[0]
    status = random.choices(status_codes, weights=[60, 10, 5, 5, 3, 2, 5, 3, 1, 1])[0]
    # 엔드포인트별로 응답시간 분포 다르게
    if endpoint == '/api/user/list':
        resp = random.randint(80, 200)
    elif endpoint == '/api/order/create':
        resp = random.randint(150, 600)
    elif endpoint == '/api/admin/stats':
        resp = random.randint(300, 1200)
    else:
        resp = random.randint(50, 300)
    line = f"{dt.strftime('%Y-%m-%dT%H:%M:%SZ')} {method} {endpoint} {status} {resp}ms"
    lines.append(line)

with open('server_sample.log', 'w') as f:
    for line in lines:
        f.write(line + '\n')

print('샘플 로그(server_sample.log) 생성 완료!') 
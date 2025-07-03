import time
from datetime import datetime
import random

methods = ['GET', 'POST', 'PUT', 'DELETE']
endpoints = [
    '/api/user/list', '/api/user/login', '/api/user/logout', '/api/product/list',
    '/api/product/detail', '/api/order/create', '/api/order/cancel', '/api/admin/stats'
]
status_codes = [200, 201, 204, 400, 401, 403, 404, 500, 502, 503]

while True:
    now = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    method = random.choice(methods)
    endpoint = random.choices(endpoints, weights=[20, 15, 5, 20, 10, 10, 5, 5])[0]
    status = random.choices(status_codes, weights=[60, 10, 5, 5, 3, 2, 5, 3, 1, 1])[0]
    if endpoint == '/api/user/list':
        resp = random.randint(80, 200)
    elif endpoint == '/api/order/create':
        resp = random.randint(150, 600)
    elif endpoint == '/api/admin/stats':
        resp = random.randint(300, 1200)
    else:
        resp = random.randint(50, 300)
    line = f"{now} {method} {endpoint} {status} {resp}ms\n"
    with open('server_sample.log', 'a') as f:
        f.write(line)
    print(f"추가: {line.strip()}")
    time.sleep(2) 
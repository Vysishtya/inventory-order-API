import requests
import threading

URL = "http://127.0.0.1:8000/orders"

PAYLOAD = {
    "user_id": 1,
    "product_id":2,
    "store_id":1,
    "quantity":1
}

results = []
lock = threading.Lock()

def place_order():
    response = requests.post(URL,json = PAYLOAD)
    with lock:
        results.append(response.status_code)

threads = []
for i in range(50):
    t = threading.Thread(target = place_order)
    threads.append(t)

for t in threads:
    t.start()

for t in threads:
    t.join()

success_count = results.count(200)
failure_count = len(results) - success_count

print(f"Total requests: {len(results)}")
print(f"Successful orders (200): {success_count}")
print(f"Rejected orders (non-200): {failure_count}")
print(f"Status code breakdown: {dict((code, results.count(code)) for code in set(results))}")

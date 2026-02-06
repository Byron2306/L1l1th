import requests, json
r = requests.get('http://127.0.0.1:5000/debug/export_buffers?limit=200', timeout=10)
print('status', r.status_code)
try:
    print(json.dumps(r.json(), indent=2)[:2000])
except Exception as e:
    print('error parsing json', e)
    print(r.text[:2000])

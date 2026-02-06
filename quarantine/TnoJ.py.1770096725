import urllib.request, json, sys, time
url = 'http://127.0.0.1:5000/tape.json'
for i in range(3):
    try:
        with urllib.request.urlopen(url, timeout=5) as r:
            data = json.load(r)
            print(f"Attempt {i+1}:")
            print(json.dumps(data, indent=2))
    except Exception as e:
        print('ERROR:', e)
    if i < 2:
        time.sleep(2)

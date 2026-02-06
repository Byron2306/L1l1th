import csv, time, random, sys
from pathlib import Path
p = Path('logs')
p.mkdir(exist_ok=True)
path = p / 'trades.csv'
fieldnames = ['timestamp','symbol','side','quantity','price','venue','status','order_id']
N = int(sys.argv[1]) if len(sys.argv) > 1 else 1000
with path.open('a', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    if path.stat().st_size == 0:
        writer.writeheader()
    for i in range(N):
        ts = int(time.time() * 1000)
        qty = round(random.random() * 0.5, 6)
        price = round(2000 + random.random() * 2000, 2)
        side = random.choice(['BUY','SELL'])
        writer.writerow({'timestamp': ts, 'symbol': 'ETH/USDT', 'side': side, 'quantity': qty, 'price': price, 'venue': 'kraken', 'status': 'tape', 'order_id': f't{i}-{ts}'})
print(f'Wrote {N} rows to {path}')

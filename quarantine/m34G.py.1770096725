import sqlite3, json, os, sys

db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'swarm_data.db')
db_path = os.path.normpath(db_path)
if not os.path.exists(db_path):
    print('ERROR: DB not found:', db_path)
    sys.exit(0)
conn = sqlite3.connect(db_path)
c = conn.cursor()
try:
    c.execute('SELECT id,timestamp,symbol,side,quantity,price,status FROM trades ORDER BY id DESC LIMIT 50')
    rows = c.fetchall()
    out = []
    for r in rows:
        out.append({
            'id': r[0], 'timestamp': r[1], 'symbol': r[2], 'side': r[3],
            'quantity': r[4], 'price': r[5], 'status': r[6]
        })
    print(json.dumps(out, default=str, indent=2))
finally:
    conn.close()

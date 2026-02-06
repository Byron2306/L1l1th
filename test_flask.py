from flask import Flask
app = Flask(__name__)

@app.route('/status')
def status():
    return {'status': 'OK', 'model': 'openrouter-free'}

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=False)
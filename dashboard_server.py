"""Standalone Dashboard Server - LotoScope Analytics"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'web', 'backend'))
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

from flask import Flask, render_template, jsonify
from flask_cors import CORS
from analise_completa import analise_completa

app = Flask(__name__,
    template_folder=os.path.join(os.path.dirname(__file__), 'web', 'frontend', 'templates'),
    static_folder=os.path.join(os.path.dirname(__file__), 'web', 'frontend', 'static'))
CORS(app)

@app.route('/')
def index():
    return render_template('dashboard.html')

@app.route('/api/dashboard-data')
def dashboard_data():
    try:
        return jsonify(analise_completa())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print('Dashboard LotoScope rodando em http://localhost:5000')
    app.run(host='0.0.0.0', port=5000, debug=False)

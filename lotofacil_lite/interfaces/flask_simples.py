from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello():
    return '''
    <h1>🎯 Flask Teste Simples</h1>
    <p>Se você está vendo esta página, o Flask está funcionando!</p>
    <button onclick="window.location.href='/academico'">Teste Acadêmico</button>
    '''

@app.route('/academico')
def academico():
    try:
        from gerador_academico_dinamico import GeradorAcademicoDinamico
        return "<h2>✅ Módulo importado com sucesso!</h2><p>GeradorAcademicoDinamico está disponível.</p>"
    except Exception as e:
        return f"<h2>❌ Erro:</h2><p>{str(e)}</p>"

if __name__ == '__main__':
    print("🚀 Flask Simples Iniciando...")
    print("📱 URL: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)

"""
Teste simples usando apenas requests
"""
import requests

# Teste simples
try:
    print("Testando conexão...")
    response = requests.get("http://localhost:5000/api/health", timeout=5)
    print(f"Status: {response.status_code}")
    print(f"Resposta: {response.json()}")
except Exception as e:
    print(f"Erro: {e}")
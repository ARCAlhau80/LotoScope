#!/usr/bin/env python3
"""
🧪 Teste da funcionalidade de quantidade vazia
Testa se o sistema gera todas as combinações quando quantity=""
"""

import requests
import json

# Configuração
BASE_URL = "http://localhost:5000/api"

def teste_quantidade_especifica():
    """Testa geração com quantidade específica"""
    print("🧪 Teste 1: Quantidade específica (5 combinações)")
    
    data = {
        "fixed_numbers": [10],
        "game_size": 15,
        "quantity": 5
    }
    
    response = requests.post(f"{BASE_URL}/generate-combinations", json=data)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Sucesso: {result['count']} combinações geradas")
        print(f"📊 Solicitado: {result['requested']}")
        print(f"🎯 Primeira combinação: {result['combinations'][0] if result['combinations'] else 'Nenhuma'}")
    else:
        print(f"❌ Erro: {response.status_code}")

def teste_quantidade_vazia():
    """Testa geração com quantidade vazia (todas)"""
    print("\n🧪 Teste 2: Quantidade vazia (TODAS as combinações)")
    
    data = {
        "fixed_numbers": [10, 14],  # 2 números fixos para limitar o resultado
        "game_size": 15,
        "quantity": ""  # Campo vazio = TODAS
    }
    
    response = requests.post(f"{BASE_URL}/generate-combinations", json=data)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Sucesso: {result['count']} combinações geradas")
        print(f"📊 Solicitado: {result['requested']}")
        print(f"🎯 Primeiras 3 combinações:")
        for i, combo in enumerate(result['combinations'][:3]):
            print(f"   #{i+1}: {combo}")
        if result['count'] > 3:
            print(f"   ... e mais {result['count'] - 3} combinações")
    else:
        print(f"❌ Erro: {response.status_code}")

def teste_quantidade_zero():
    """Testa geração com quantidade = 0"""
    print("\n🧪 Teste 3: Quantidade zero (0)")
    
    data = {
        "fixed_numbers": [5, 15, 20],  # 3 números fixos
        "game_size": 15,
        "quantity": 0  # Zero = TODAS
    }
    
    response = requests.post(f"{BASE_URL}/generate-combinations", json=data)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Sucesso: {result['count']} combinações geradas")
        print(f"📊 Solicitado: {result['requested']}")
        print(f"🎯 Primeira combinação: {result['combinations'][0] if result['combinations'] else 'Nenhuma'}")
    else:
        print(f"❌ Erro: {response.status_code}")

def main():
    print("🎯 LotoScope - Teste de Quantidade Vazia")
    print("=" * 50)
    
    try:
        # Verificar se servidor está rodando
        health_response = requests.get(f"{BASE_URL}/health")
        if health_response.status_code != 200:
            print("❌ Servidor não está rodando. Inicie o Flask primeiro!")
            return
        
        print("✅ Servidor conectado")
        
        # Executar testes
        teste_quantidade_especifica()
        teste_quantidade_vazia()
        teste_quantidade_zero()
        
        print("\n🎉 Testes concluídos!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Erro: Não foi possível conectar ao servidor")
        print("💡 Certifique-se de que o Flask está rodando em http://localhost:5000")

if __name__ == "__main__":
    main()
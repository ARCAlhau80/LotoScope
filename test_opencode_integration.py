#!/usr/bin/env python3
"""
Teste de integração com OpenCode.
Verifica se o OpenCode está rodando e responde corretamente.
"""

import sys
import os

# Adicionar path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lotoscope_agents import AgentOrchestrator, OpenCodeClient


def test_opencode_connection():
    """Testa conexão com OpenCode."""
    print("=== Teste de Conexão com OpenCode ===\n")
    
    client = OpenCodeClient()
    
    print(f"Base URL: {client.base_url}")
    print(f"Modelo: {client.model}")
    print(f"API Key: {client.api_key[:10]}...")
    print()
    
    # Testar disponibilidade
    available = client.is_available()
    print(f"Status: {'DISPONÍVEL' if available else 'INDISPONÍVEL'}")
    
    if not available:
        print("\n[ERRO] OpenCode não está rodando.")
        print("\nPara iniciar:")
        print("  1. Execute: opencode web")
        print("  2. Ou use: .\\start-opencode.bat")
        print("\nDepois tente novamente.")
        return False
    
    print("\n[OK] OpenCode conectado com sucesso!")
    return True


def test_agent_llm_call():
    """Testa chamada de agente com LLM."""
    print("\n=== Teste de Chamada de Agente com LLM ===\n")
    
    orchestrator = AgentOrchestrator()
    
    if not orchestrator.opencode.is_available():
        print("[SKIP] OpenCode não disponível, pulando teste LLM.")
        return False
    
    # Testar chamada simples
    print("Chamando coordinator com LLM...")
    result = orchestrator.call_agent(
        "coordinator",
        "Explique brevemente o que é o LotoScope",
        use_llm=True
    )
    
    if "llm_response" in result and result["llm_response"]:
        print(f"\n[OK] Resposta do LLM:")
        print(f"  {result['llm_response'][:200]}...")
        return True
    else:
        print("\n[ERRO] LLM não retornou resposta.")
        return False


def test_delegation():
    """Testa delegação ao OpenCode."""
    print("\n=== Teste de Delegação ao OpenCode ===\n")
    
    orchestrator = AgentOrchestrator()
    
    if not orchestrator.opencode.is_available():
        print("[SKIP] OpenCode não disponível, pulando teste de delegação.")
        return False
    
    print("Delegando tarefa ao OpenCode...")
    result = orchestrator.delegate_to_opencode(
        "Qual é a estratégia Pool 23 e como funciona?",
        context={"agent": "test", "topic": "pool23"}
    )
    
    if result.get("status") == "completed" and result.get("response"):
        print(f"\n[OK] Delegação bem-sucedida!")
        print(f"  Resposta: {result['response'][:200]}...")
        return True
    else:
        print(f"\n[ERRO] Delegação falhou: {result.get('error', 'desconhecido')}")
        return False


def main():
    """Executa todos os testes."""
    print("=" * 60)
    print("  LotoScope - Teste de Integração com OpenCode")
    print("=" * 60)
    print()
    
    results = []
    
    # Teste 1: Conexão
    results.append(("Conexão OpenCode", test_opencode_connection()))
    
    # Teste 2: Chamada LLM
    results.append(("Chamada Agente+LLM", test_agent_llm_call()))
    
    # Teste 3: Delegação
    results.append(("Delegação OpenCode", test_delegation()))
    
    # Resumo
    print("\n" + "=" * 60)
    print("  Resumo dos Testes")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "[OK]" if passed else "[ERRO]"
        print(f"  {status} {test_name}")
    
    total = len(results)
    passed = sum(1 for _, p in results if p)
    
    print(f"\n  Total: {passed}/{total} testes passaram")
    print("=" * 60)
    
    if passed == total:
        print("\n[SUCCESS] Todos os testes passaram!")
        print("\nVocê pode usar os agentes com OpenCode:")
        print("  python lotoscope_agents.py call-llm analyst \"tarefa\"")
        print("  python lotoscope_agents.py delegate \"pergunta\"")
    else:
        print("\n[WARNING] Alguns testes falharam.")
        print("\nVerifique:")
        print("  1. OpenCode está rodando? (opencode web)")
        print("  2. Porta correta configurada?")
        print("  3. Modelo disponível?")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

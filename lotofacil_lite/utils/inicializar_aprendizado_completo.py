#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔄 INICIALIZADOR COMPLETO DO SISTEMA DE APRENDIZADO
Sistema para inicializar todos os componentes de aprendizado da IA
- Cria estrutura de pastas necessárias
- Inicializa arquivos de configuração
- Prepara sistema de monitoramento
- Configura pipeline de aprendizado

Autor: AR CALHAU
Data: 20 de Setembro de 2025
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path

def criar_estrutura_pastas():
    """Cria estrutura completa de pastas para o sistema de aprendizado"""
    print("📁 Criando estrutura de pastas...")
    
    pastas = [
        "ia_repetidos",
        "ia_repetidos/historico_versoes",
        "ia_repetidos/backups_modelos",
        "ia_repetidos/logs_aprendizado",
        "ia_repetidos/datasets_treinamento",
        "ia_repetidos/modelos_experimentais",
        "aprendizado_continuo",
        "aprendizado_continuo/dashboard",
        "aprendizado_continuo/metricas",
        "aprendizado_continuo/validacoes",
        "aprendizado_continuo/logs"
    ]
    
    for pasta in pastas:
        os.makedirs(pasta, exist_ok=True)
        print(f"  ✅ {pasta}")
    
    print("✅ Estrutura de pastas criada com sucesso!")

def inicializar_arquivos_configuracao():
    """Inicializa arquivos de configuração do sistema"""
    print("\n⚙️ Inicializando arquivos de configuração...")
    
    # Configuração do sistema de aprendizado
    config_aprendizado = {
        "sistema": {
            "nome": "Sistema de Aprendizado LotoScope",
            "versao": "1.0.0",
            "data_inicializacao": datetime.now().isoformat(),
            "ativo": True
        },
        "configuracoes": {
            "backup_automatico": True,
            "validacao_automatica": True,
            "dashboard_tempo_real": True,
            "log_detalhado": True
        },
        "metas": {
            "precisao_minima": 0.75,
            "acertos_11_plus_meta": 0.30,
            "tempo_maximo_treinamento": 300
        },
        "caminhos": {
            "modelos": "ia_repetidos/",
            "backups": "ia_repetidos/backups_modelos/",
            "logs": "ia_repetidos/logs_aprendizado/",
            "dashboard": "aprendizado_continuo/dashboard/"
        }
    }
    
    with open("aprendizado_continuo/config_sistema.json", 'w', encoding='utf-8') as f:
        json.dump(config_aprendizado, f, indent=2, ensure_ascii=False, default=str)
    
    # Estado inicial do sistema
    estado_inicial = {
        "status": {
            "sistema_ativo": True,
            "ultimo_treinamento": None,
            "modelos_carregados": False,
            "backup_disponivel": False
        },
        "estatisticas": {
            "total_treinamentos": 0,
            "total_previsoes": 0,
            "total_validacoes": 0,
            "precisao_atual": 0.0
        },
        "historico_execucoes": []
    }
    
    with open("aprendizado_continuo/estado_sistema.json", 'w', encoding='utf-8') as f:
        json.dump(estado_inicial, f, indent=2, ensure_ascii=False, default=str)
    
    # Log de inicialização
    log_inicial = {
        "data_inicializacao": datetime.now().isoformat(),
        "eventos": [
            {
                "timestamp": datetime.now().isoformat(),
                "tipo": "inicializacao",
                "descricao": "Sistema de aprendizado inicializado com sucesso",
                "status": "sucesso"
            }
        ]
    }
    
    with open("aprendizado_continuo/logs/log_sistema.json", 'w', encoding='utf-8') as f:
        json.dump(log_inicial, f, indent=2, ensure_ascii=False, default=str)
    
    print("  ✅ config_sistema.json")
    print("  ✅ estado_sistema.json")
    print("  ✅ log_sistema.json")
    print("✅ Arquivos de configuração criados!")

def verificar_dependencias():
    """Verifica se todas as dependências estão disponíveis"""
    print("\n🔍 Verificando dependências...")
    
    dependencias_ok = True
    
    try:
        import numpy as np
        print("  ✅ NumPy disponível")
    except ImportError:
        print("  ❌ NumPy não encontrado")
        dependencias_ok = False
    
    try:
        import pandas as pd
        print("  ✅ Pandas disponível")
    except ImportError:
        print("  ❌ Pandas não encontrado")
        dependencias_ok = False
    
    try:
        import pickle
        print("  ✅ Pickle disponível")
    except ImportError:
        print("  ❌ Pickle não encontrado")
        dependencias_ok = False
    
    # Verifica arquivos principais
    arquivos_principais = [
        "super_menu.py",
        "sistema_evolucao_documentada.py",
        "lotofacil.db"
    ]
    
    for arquivo in arquivos_principais:
        if os.path.exists(arquivo):
            print(f"  ✅ {arquivo}")
        else:
            print(f"  ❌ {arquivo} não encontrado")
            dependencias_ok = False
    
    return dependencias_ok

def criar_dashboard_inicial():
    """Cria dashboard inicial do sistema"""
    print("\n📊 Criando dashboard inicial...")
    
    os.makedirs("aprendizado_continuo/dashboard", exist_ok=True)
    
    dashboard_html = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard LotoScope - Sistema de Aprendizado</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; }
        .card { background: white; border-radius: 8px; padding: 20px; margin: 15px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .header { text-align: center; color: #333; }
        .status { display: flex; justify-content: space-around; }
        .metric { text-align: center; }
        .metric h3 { margin: 0; color: #666; }
        .metric .value { font-size: 2em; font-weight: bold; color: #007bff; }
        .success { color: #28a745; }
        .warning { color: #ffc107; }
        .danger { color: #dc3545; }
    </style>
</head>
<body>
    <div class="container">
        <div class="card">
            <div class="header">
                <h1>🎯 Dashboard LotoScope - Sistema de Aprendizado</h1>
                <p>Inicializado em: """ + datetime.now().strftime("%d/%m/%Y %H:%M:%S") + """</p>
            </div>
        </div>
        
        <div class="card">
            <h2>📊 Status do Sistema</h2>
            <div class="status">
                <div class="metric">
                    <h3>Sistema</h3>
                    <div class="value success">🟢 ATIVO</div>
                </div>
                <div class="metric">
                    <h3>Modelos</h3>
                    <div class="value warning">⚠️ AGUARDANDO</div>
                </div>
                <div class="metric">
                    <h3>Backup</h3>
                    <div class="value success">✅ CONFIGURADO</div>
                </div>
                <div class="metric">
                    <h3>Precisão</h3>
                    <div class="value">0.0%</div>
                </div>
            </div>
        </div>
        
        <div class="card">
            <h2>🚀 Próximos Passos</h2>
            <ul>
                <li>✅ Sistema inicializado com sucesso</li>
                <li>🔄 Aguardando primeiro treinamento</li>
                <li>📈 Dashboard será atualizado automaticamente</li>
                <li>🎯 Configure suas metas no sistema</li>
            </ul>
        </div>
    </div>
</body>
</html>
    """
    
    with open("aprendizado_continuo/dashboard/dashboard.html", 'w', encoding='utf-8') as f:
        f.write(dashboard_html)
    
    print("  ✅ dashboard.html criado")
    print("✅ Dashboard inicial pronto!")

def registrar_inicializacao():
    """Registra a inicialização no sistema de evolução"""
    print("\n📝 Registrando inicialização...")
    
    try:
        from sistema_evolucao_documentada import SistemaEvolucaoDocumentada
        
        sistema_evolucao = SistemaEvolucaoDocumentada()
        
        # Registra evento de inicialização
        sistema_evolucao.registrar_descoberta_importante(
            "Sistema de Aprendizado Completo Inicializado",
            {
                "data": datetime.now().isoformat(),
                "componentes": [
                    "Estrutura de pastas",
                    "Arquivos de configuração", 
                    "Dashboard inicial",
                    "Sistema de logs"
                ],
                "status": "operacional"
            },
            "medio"
        )
        
        print("  ✅ Evento registrado no sistema de evolução")
        
    except Exception as e:
        print(f"  ⚠️ Não foi possível registrar no sistema de evolução: {e}")

def main():
    """Função principal de inicialização"""
    print("INICIALIZADOR COMPLETO DO SISTEMA DE APRENDIZADO")
    print("=" * 60)
    print(f"Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print()
    
    try:
        # 1. Verificar dependências
        if not verificar_dependencias():
            print("\n❌ Dependências não atendidas. Verifique a instalação.")
            return False
        
        # 2. Criar estrutura
        criar_estrutura_pastas()
        
        # 3. Inicializar configurações
        inicializar_arquivos_configuracao()
        
        # 4. Criar dashboard
        criar_dashboard_inicial()
        
        # 5. Registrar inicialização
        registrar_inicializacao()
        
        print("\n" + "=" * 60)
        print("SISTEMA DE APRENDIZADO INICIALIZADO COM SUCESSO!")
        print("=" * 60)
        print()
        print("✅ Componentes inicializados:")
        print("   • Estrutura de pastas completa")
        print("   • Arquivos de configuração")
        print("   • Dashboard de monitoramento")
        print("   • Sistema de logs")
        print("   • Integração com evolução documentada")
        print()
        print("🎯 Próximos passos:")
        print("   1. Execute o treinamento da IA")
        print("   2. Configure suas metas de precisão")
        print("   3. Monitore o progresso no dashboard")
        print()
        
        return True
        
    except KeyboardInterrupt:
        print("\n⏹️ Inicialização cancelada pelo usuário")
        return False
        
    except Exception as e:
        print(f"\n❌ Erro durante a inicialização: {e}")
        return False

if __name__ == "__main__":
    sucesso = main()
    
    if sucesso:
        print("✅ Inicialização concluída com sucesso!")
        sys.exit(0)
    else:
        print("❌ Falha na inicialização")
        sys.exit(1)
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔧 APLICADOR DE CALIBRAÇÃO AUTOMÁTICA
====================================
Sistema que monitora configurações de calibração e aplica
automaticamente aos geradores durante execução.

Funciona como middleware que:
1. Detecta chamadas de geradores
2. Verifica configurações de calibração ativas
3. Aplica parâmetros automaticamente
4. Mantém log de aplicações

Autor: AR CALHAU
Data: 06 de Outubro de 2025
"""

import os
import json
import glob
from datetime import datetime
from typing import Dict, Optional, Any

class AplicadorCalibracao:
    """Aplica calibrações automaticamente aos geradores"""
    
    def __init__(self):
        self.pasta_calibracao = "calibracao_automatica"
        os.makedirs(self.pasta_calibracao, exist_ok=True)
        
        # Cache de configurações
        self._cache_configs = {}
        self._ultima_verificacao = None
        
        print("🔧 Aplicador de Calibração inicializado")
    
    def obter_configuracao_gerador(self, nome_gerador: str) -> Optional[Dict]:
        """Obtém configuração de calibração para um gerador específico"""
        # Remove extensão se presente
        if nome_gerador.endswith('.py'):
            nome_gerador = nome_gerador[:-3]
        
        arquivo_config = os.path.join(self.pasta_calibracao, f"config_{nome_gerador}.json")
        
        if os.path.exists(arquivo_config):
            try:
                with open(arquivo_config, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                return config.get('configuracao', {})
            except Exception as e:
                print(f"⚠️ Erro ao carregar config para {nome_gerador}: {e}")
        
        return None
    
    def aplicar_configuracao_zona_conforto(self, **kwargs) -> Dict:
        """Aplica configuração específica para gerador zona de conforto"""
        config = self.obter_configuracao_gerador('gerador_zona_conforto')
        
        if config:
            print(f"🎯 Aplicando calibração ao gerador zona de conforto")
            
            # Aplica configurações específicas
            kwargs.update({
                'zona_inicio': config.get('zona_conforto_inicio', 1),
                'zona_fim': config.get('zona_conforto_fim', 17),
                'peso_zona': config.get('peso_zona', 0.8),
                'permitir_sequencias': config.get('permitir_sequencias', True),
                'calibracao_ativa': True
            })
            
            self._log_aplicacao('gerador_zona_conforto', config)
        
        return kwargs
    
    def aplicar_configuracao_academico(self, **kwargs) -> Dict:
        """Aplica configuração específica para gerador acadêmico"""
        config = self.obter_configuracao_gerador('gerador_academico_dinamico')
        
        if config:
            print(f"🎓 Aplicando calibração ao gerador acadêmico")
            
            kwargs.update({
                'zona_foco': config.get('zona_foco', [1, 25]),
                'peso_correlacoes': config.get('peso_correlacoes', 0.6),
                'soma_alvo': config.get('soma_alvo', [180, 220]),
                'modo_inversao': config.get('modo_inversao', False),
                'calibracao_ativa': True
            })
            
            self._log_aplicacao('gerador_academico_dinamico', config)
        
        return kwargs
    
    def aplicar_configuracao_complementacao(self, **kwargs) -> Dict:
        """Aplica configuração específica para gerador de complementação"""
        config = self.obter_configuracao_gerador('gerador_complementacao_inteligente')
        
        if config:
            print(f"🧩 Aplicando calibração ao gerador de complementação")
            
            kwargs.update({
                'base_20_foco': config.get('base_20_foco', [1, 20]),
                'forca_extremos': config.get('forca_extremos', False),
                'peso_distribuicao': config.get('peso_distribuicao', 3.0),
                'soma_alvo': config.get('soma_alvo', [180, 220]),
                'calibracao_ativa': True
            })
            
            self._log_aplicacao('gerador_complementacao_inteligente', config)
        
        return kwargs
    
    def aplicar_configuracao_super_gerador(self, **kwargs) -> Dict:
        """Aplica configuração específica para super gerador IA"""
        config = self.obter_configuracao_gerador('super_gerador_ia')
        
        if config:
            print(f"🤖 Aplicando calibração ao super gerador IA")
            
            kwargs.update({
                'modo_adaptativo': config.get('modo_adaptativo', True),
                'cenario_detectado': config.get('cenario_detectado', 'equilibrio_normal'),
                'confianca_cenario': config.get('confianca_cenario', 0.5),
                'parametros_especiais': config.get('parametros_especiais', {}),
                'calibracao_ativa': True
            })
            
            self._log_aplicacao('super_gerador_ia', config)
        
        return kwargs
    
    def aplicar_configuracao_desdobramento(self, **kwargs) -> Dict:
        """Aplica configuração específica para sistema de desdobramento"""
        config = self.obter_configuracao_gerador('sistema_desdobramento_complementar')
        
        if config:
            print(f"🔄 Aplicando calibração ao sistema de desdobramento")
            
            kwargs.update({
                'cenario': config.get('cenario', 'equilibrio_normal'),
                'estrategia': config.get('estrategia', {}),
                'parametros': config.get('parametros', {}),
                'calibracao_ativa': True
            })
            
            self._log_aplicacao('sistema_desdobramento_complementar', config)
        
        return kwargs
    
    def _log_aplicacao(self, gerador: str, config: Dict):
        """Registra aplicação de configuração"""
        log_file = os.path.join(self.pasta_calibracao, "log_aplicacoes.json")
        
        entrada_log = {
            'timestamp': datetime.now().isoformat(),
            'gerador': gerador,
            'configuracao_aplicada': config,
            'status': 'aplicado'
        }
        
        # Carrega log existente ou cria novo
        logs = []
        if os.path.exists(log_file):
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    logs = json.load(f)
            except:
                logs = []
        
        logs.append(entrada_log)
        
        # Mantém apenas últimas 100 entradas
        logs = logs[-100:]
        
        # Salva log atualizado
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(logs, f, indent=2, ensure_ascii=False)
    
    def verificar_configuracoes_ativas(self) -> Dict:
        """Verifica quais configurações estão ativas"""
        configs_ativas = {}
        
        # Busca todos os arquivos de configuração
        pattern = os.path.join(self.pasta_calibracao, "config_*.json")
        arquivos_config = glob.glob(pattern)
        
        for arquivo in arquivos_config:
            nome_arquivo = os.path.basename(arquivo)
            gerador = nome_arquivo.replace('config_', '').replace('.json', '')
            
            try:
                with open(arquivo, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    configs_ativas[gerador] = {
                        'timestamp': config.get('timestamp'),
                        'configuracao': config.get('configuracao', {}),
                        'arquivo': arquivo
                    }
            except Exception as e:
                print(f"⚠️ Erro ao verificar {arquivo}: {e}")
        
        return configs_ativas
    
    def relatorio_status_calibracao(self):
        """Gera relatório do status atual de calibração"""
        print("\n" + "=" * 60)
        print("📊 RELATÓRIO DE STATUS DE CALIBRAÇÃO")
        print("=" * 60)
        
        configs = self.verificar_configuracoes_ativas()
        
        if not configs:
            print("⚠️ Nenhuma configuração de calibração ativa encontrada")
            return
        
        print(f"🔧 Configurações ativas: {len(configs)}")
        print()
        
        for gerador, info in configs.items():
            print(f"📝 {gerador}:")
            print(f"   ⏰ Aplicado em: {info['timestamp']}")
            print(f"   🎯 Configuração: {len(info['configuracao'])} parâmetros")
            
            # Mostra alguns parâmetros principais
            config = info['configuracao']
            if 'cenario' in config:
                print(f"   🎪 Cenário: {config['cenario']}")
            if 'zona_foco' in config:
                print(f"   🎯 Zona foco: {config['zona_foco']}")
            if 'soma_alvo' in config:
                print(f"   ➕ Soma alvo: {config['soma_alvo']}")
            print()
        
        print("=" * 60)

# Instância global para uso fácil
aplicador_calibracao = AplicadorCalibracao()

def aplicar_calibracao_automatica(nome_gerador: str, **kwargs) -> Dict:
    """Função utilitária para aplicar calibração a qualquer gerador"""
    return aplicador_calibracao.obter_configuracao_gerador(nome_gerador) or kwargs

if __name__ == "__main__":
    aplicador_calibracao.relatorio_status_calibracao()
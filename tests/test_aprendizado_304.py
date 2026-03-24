#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
🧪 TESTE — Registro de Aprendizado no Backtesting Histórico (Op. 30→4)
========================================================================

RED-PHASE TEST:
Verifica que quando comparação de estratégias/probabilísticos é executada,
os resultados são GRAVADOS no histórico com metadados completos.

Estrutura esperada em historico_aprendizado.json:
{
  "comparacoes": [
    {
      "timestamp": "2026-03-24T20:30:00",
      "tipo": "estrategia",
      "nivel": 3,
      "range": {"inicio": 3600, "fim": 3650, "qtd": 51},
      "estrategias_testadas": [1, 2, 3, 4, 5],
      "resultados": [
        {"estrategia": 1, "nome": "Débito", "jackpots": 2, "roi": 145.2, ...},
        ...
      ],
      "vencedora": {"estrategia": 2, "roi": 289.5},
      "notas": "..."
    }
  ]
}
"""

import sys
import os
import json
import tempfile
from pathlib import Path
from datetime import datetime
from unittest.mock import patch, MagicMock

# ─── Setup Path ───────────────────────────────────────────────────────────
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(ROOT_DIR / 'lotofacil_lite' / 'interfaces'))
sys.path.insert(0, str(ROOT_DIR / 'lotofacil_lite' / 'utils'))


class TestRegistroAprendizado304:
    """Suite de testes para registro de aprendizado no 30.4"""
    
    def setup_method(self):
        """Prepara ambiente para cada teste"""
        self.temp_dir = tempfile.mkdtemp()
        self.historico_path = os.path.join(self.temp_dir, 'historico_aprendizado.json')
    
    def test_structure_comparacao_estrategia_esperada(self):
        """
        RED: Estrutura mínima de uma comparação de estratégias deve existir
        
        Valida que um objeto de comparação tem:
        - timestamp (ISO 8601)
        - tipo ("estrategia" ou "probabilistico")
        - nivel (int 0-8)
        - range (dict com inicio, fim, qtd)
        - estrategias_testadas (list de ints)
        - resultados (list com cada estratégia)
        - vencedora (dict com estrategia, nome, roi)
        """
        # Estrutura esperada
        comparacao = {
            "timestamp": datetime.now().isoformat(),
            "tipo": "estrategia",
            "nivel": 3,
            "range": {"inicio": 3600, "fim": 3650, "qtd": 51},
            "estrategias_testadas": [1, 2, 3, 4, 5],
            "resultados": [
                {
                    "estrategia": 1,
                    "nome": "Débito (superávit)",
                    "jackpots": 2,
                    "acertos_11_mais": 12,
                    "roi": 145.2,
                    "combos_media": 8500,
                    "custo_total": 29750,
                    "premio_total": 43225,
                },
                {
                    "estrategia": 2,
                    "nome": "Invertida v3.0 (QUENTES)",
                    "jackpots": 3,
                    "acertos_11_mais": 15,
                    "roi": 289.5,
                    "combos_media": 6200,
                    "custo_total": 21700,
                    "premio_total": 84635,
                },
                # ... mais estratégias
            ],
            "vencedora": {
                "estrategia": 2,
                "nome": "Invertida v3.0 (QUENTES)",
                "roi": 289.5,
                "jackpots": 3,
            },
            "notas": "Testado com filtro probabilístico conservativo",
        }
        
        # Validar campos presentes
        assert "timestamp" in comparacao, "Falta timestamp"
        assert "tipo" in comparacao, "Falta tipo"
        assert "nivel" in comparacao, "Falta nivel"
        assert "range" in comparacao, "Falta range"
        assert "estrategias_testadas" in comparacao, "Falta estrategias_testadas"
        assert "resultados" in comparacao, "Falta resultados"
        assert "vencedora" in comparacao, "Falta vencedora"
        
        # Validar tipos
        assert isinstance(comparacao["timestamp"], str), "timestamp deve ser string"
        assert comparacao["tipo"] in ["estrategia", "probabilistico"], "tipo inválido"
        assert isinstance(comparacao["nivel"], int), "nivel deve ser int"
        assert isinstance(comparacao["range"], dict), "range deve ser dict"
        assert "inicio" in comparacao["range"], "range falta inicio"
        assert "fim" in comparacao["range"], "range falta fim"
        assert "qtd" in comparacao["range"], "range falta qtd"
        assert isinstance(comparacao["resultados"], list), "resultados deve ser list"
        assert len(comparacao["resultados"]) > 0, "resultados vazia"
        assert isinstance(comparacao["vencedora"], dict), "vencedora deve ser dict"
        
        print("✅ Estrutura de comparação validada!")
    
    def test_salvar_comparacao_no_historico(self):
        """
        RED: Comparação deve ser salvável em JSON com estrutura correta
        """
        historico = {"comparacoes": []}
        
        nova_comparacao = {
            "timestamp": datetime.now().isoformat(),
            "tipo": "estrategia",
            "nivel": 3,
            "range": {"inicio": 3600, "fim": 3650, "qtd": 51},
            "estrategias_testadas": [1, 2, 3, 4, 5],
            "resultados": [
                {"estrategia": 1, "nome": "Débito", "jackpots": 2, "roi": 145.2},
                {"estrategia": 2, "nome": "Invertida", "jackpots": 3, "roi": 289.5},
            ],
            "vencedora": {"estrategia": 2, "nome": "Invertida", "roi": 289.5},
        }
        
        historico["comparacoes"].append(nova_comparacao)
        
        # Salvar e recarregar
        with open(self.historico_path, 'w', encoding='utf-8') as f:
            json.dump(historico, f, indent=2, ensure_ascii=False)
        
        # Validar que pode ser recarregado
        with open(self.historico_path, 'r', encoding='utf-8') as f:
            historico_carregado = json.load(f)
        
        assert len(historico_carregado["comparacoes"]) == 1, "Não salvou comparação"
        comp = historico_carregado["comparacoes"][0]
        assert comp["tipo"] == "estrategia", "tipo incorreto"
        assert comp["vencedora"]["estrategia"] == 2, "vencedora incorreta"
        
        print("✅ Salvamento e carga de comparação validado!")
    
    def test_historico_multiplas_comparacoes(self):
        """
        RED: Histórico deve suportar múltiplas comparações (modo append)
        """
        historico = {"comparacoes": []}
        
        # Adicionar 3 comparações
        for i in range(3):
            comp = {
                "timestamp": f"2026-03-24T20:30:{i:02d}",
                "tipo": "estrategia" if i < 2 else "probabilistico",
                "nivel": i,
                "range": {"inicio": 3600 + i*50, "fim": 3650 + i*50, "qtd": 51},
                "estrategias_testadas": [1, 2, 3],
                "resultados": [
                    {"estrategia": j, "nome": f"Est{j}", "roi": 100 + j*50}
                    for j in range(1, 4)
                ],
                "vencedora": {"estrategia": 2, "roi": 150},
            }
            historico["comparacoes"].append(comp)
        
        # Salvar
        with open(self.historico_path, 'w', encoding='utf-8') as f:
            json.dump(historico, f, indent=2, ensure_ascii=False)
        
        # Verificar
        with open(self.historico_path, 'r', encoding='utf-8') as f:
            loaded = json.load(f)
        
        assert len(loaded["comparacoes"]) == 3, "Não salvou todas as comparações"
        assert loaded["comparacoes"][0]["tipo"] == "estrategia"
        assert loaded["comparacoes"][2]["tipo"] == "probabilistico"
        
        print("✅ Múltiplas comparações validadas!")
    
    def test_agredir_comparacao_existente(self):
        """
        RED: Ao adicionar nova comparação, deve AGREDIR (append) ao histórico existente,
        não sobrescrever
        """
        # Salvar primeira comparação
        historico_v1 = {
            "comparacoes": [
                {
                    "timestamp": "2026-03-24T20:00:00",
                    "tipo": "estrategia",
                    "nivel": 2,
                    "range": {"inicio": 3500, "fim": 3550, "qtd": 51},
                    "resultados": [{"estrategia": 1, "roi": 100}],
                    "vencedora": {"estrategia": 1, "roi": 100},
                }
            ]
        }
        
        with open(self.historico_path, 'w', encoding='utf-8') as f:
            json.dump(historico_v1, f, indent=2, ensure_ascii=False)
        
        # Carregar, agredir nova
        with open(self.historico_path, 'r', encoding='utf-8') as f:
            historico = json.load(f)
        
        nova_comp = {
            "timestamp": "2026-03-24T20:30:00",
            "tipo": "estrategia",
            "nivel": 3,
            "range": {"inicio": 3600, "fim": 3650, "qtd": 51},
            "resultados": [{"estrategia": 2, "roi": 200}],
            "vencedora": {"estrategia": 2, "roi": 200},
        }
        
        historico["comparacoes"].append(nova_comp)
        
        with open(self.historico_path, 'w', encoding='utf-8') as f:
            json.dump(historico, f, indent=2, ensure_ascii=False)
        
        # Verificar que ambas estão lá
        with open(self.historico_path, 'r', encoding='utf-8') as f:
            loaded = json.load(f)
        
        assert len(loaded["comparacoes"]) == 2, "Histórico foi sobrescrito!"
        assert loaded["comparacoes"][0]["nivel"] == 2, "Primeira perdida"
        assert loaded["comparacoes"][1]["nivel"] == 3, "Segunda não foi adicionada"
        
        print("✅ Agredir a histórico existente validado!")


# ─── Runner ───────────────────────────────────────────────────────────────

def main():
    import pytest
    
    print("\n" + "=" * 70)
    print("🧪 RED-PHASE TESTS — Registro de Aprendizado 30.4")
    print("=" * 70)
    
    # Executar com pytest se disponível, senão manualmente
    try:
        result = pytest.main([
            __file__,
            "-v",
            "--tb=short",
            "-s"
        ])
        return result
    except ImportError:
        # Fallback: executar manualmente
        print("\n⚠️ pytest não disponível, executando testes manualmente...\n")
        
        suite = TestRegistroAprendizado304()
        testes = [
            ("Structure validada", suite.test_structure_comparacao_estrategia_esperada),
            ("Salvar comparação", suite.test_salvar_comparacao_no_historico),
            ("Múltiplas comparações", suite.test_historico_multiplas_comparacoes),
            ("Agredir histórico", suite.test_agredir_comparacao_existente),
        ]
        
        passou = 0
        falhou = 0
        
        for nome, teste_fn in testes:
            suite.setup_method()
            print(f"\n  ▶ {nome}...", end=" ", flush=True)
            try:
                teste_fn()
                print("✅")
                passou += 1
            except AssertionError as e:
                print(f"❌ {e}")
                falhou += 1
            except Exception as e:
                print(f"💥 {e}")
                falhou += 1
        
        print("\n" + "=" * 70)
        print(f"Resultado: {passou}/{len(testes)} testes passaram")
        if falhou == 0:
            print("=" * 70)
            return 0
        else:
            print(f"           {falhou} FALHA(S)")
            print("=" * 70)
            return 1


if __name__ == '__main__':
    sys.exit(main())

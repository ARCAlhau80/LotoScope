"""
SISTEMA ASSIMÉTRICO PREMIUM - VERSÃO CORRIGIDA
==============================================
Foco na faixa 11-13 acertos com correções de serialização
"""

import json
from datetime import datetime
from gerador_academico_dinamico import GeradorAcademicoDinamico
from avaliador_faixa_premium import AvaliadorFaixaPremium

class SistemaAssimetricoPremiumCorrigido:
    def __init__(self):
        self.gerador = GeradorAcademicoDinamico()
        self.avaliador = AvaliadorFaixaPremium()
        
    def converter_tipos_json(self, obj):
        """Converte tipos para tipos Python nativos (sem NumPy)"""
        if isinstance(obj, dict):
            return {key: self.converter_tipos_json(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self.converter_tipos_json(item) for item in obj]
        # Para outros tipos, retorna como está (já são tipos Python nativos)
        return obj
    
    def gerar_combinacoes_premium_corrigido(self, quantidade=10, score_minimo=65.0):
        """
        Gera combinações premium para faixa 11-13 com correção de tipos
        """
        print(f"🚀 Gerando {quantidade} combinações premium (faixa 11-13)")
        print(f"📊 Score mínimo: {score_minimo}")
        
        combinacoes_aprovadas = []
        tentativas = 0
        max_tentativas = quantidade * 50
        
        while len(combinacoes_aprovadas) < quantidade and tentativas < max_tentativas:
            # Gera combinação base
            combinacao = self.gerador.gerar_combinacao_academica(15)
            tentativas += 1
            
            # Avalia com critérios premium
            avaliacao = self.avaliador.avaliar_combinacao_premium(combinacao)
            
            if avaliacao['score_total'] >= score_minimo:
                # Converte todos os tipos para JSON-serializáveis
                resultado_limpo = {
                    'numeros': [int(n) for n in sorted(combinacao)],
                    'score_total': float(avaliacao['score_total']),
                    'score_soma': float(avaliacao['scores']['soma']),
                    'score_regioes': float(avaliacao['scores']['distribuicao_regioes']),
                    'score_espacamento': float(avaliacao['scores']['espacamento']),
                    'score_densidade': float(avaliacao['scores']['densidade_regioes']),
                    'detalhes': {
                        'soma_total': int(sum(combinacao)),
                        'qtd_pares': int(sum(1 for n in combinacao if n % 2 == 0)),
                        'qtd_impares': int(sum(1 for n in combinacao if n % 2 == 1)),
                        'espacamento_medio': float(avaliacao['detalhes']['espacamento_medio']),
                        'distribuicao_regioes': [int(x) for x in avaliacao['detalhes']['distribuicao_regioes']]
                    },
                    'posicao': len(combinacoes_aprovadas) + 1,
                    'tentativa': tentativas
                }
                
                combinacoes_aprovadas.append(resultado_limpo)
                print(f"✅ Combinação {len(combinacoes_aprovadas):2d}: Score {avaliacao['score_total']:.1f} | {sorted(combinacao)}")
        
        print(f"📈 Processo concluído: {len(combinacoes_aprovadas)}/{quantidade} combinações geradas")
        print(f"🔄 Total de tentativas: {tentativas}")
        
        if combinacoes_aprovadas:
            score_medio = sum(c['score_total'] for c in combinacoes_aprovadas) / len(combinacoes_aprovadas)
            print(f"📊 Score médio: {score_medio:.1f}")
        
        return combinacoes_aprovadas
    
    def salvar_resultados_corrigido(self, combinacoes, nome_arquivo=None):
        """
        Salva resultados com garantia de serialização JSON
        """
        if not nome_arquivo:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nome_arquivo = f"premium_11_13_corrigido_{timestamp}.json"
        
        # Prepara dados para salvar
        dados_salvar = {
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'estrategia': 'assimetrica_premium_11_13',
            'versao': 'corrigida_v1.0',
            'quantidade_gerada': len(combinacoes),
            'parametros': {
                'faixa_alvo': '11-13 acertos',
                'score_minimo': 65.0,
                'tipo': 'premium'
            },
            'combinacoes': combinacoes
        }
        
        # Converte todos os tipos antes de salvar
        dados_limpos = self.converter_tipos_json(dados_salvar)
        
        try:
            with open(nome_arquivo, 'w', encoding='utf-8') as arquivo:
                json.dump(dados_limpos, arquivo, indent=2, ensure_ascii=False)
            
            print(f"💾 Resultados salvos em: {nome_arquivo}")
            return nome_arquivo
            
        except Exception as e:
            print(f"❌ Erro ao salvar: {e}")
            return None
    
    def executar_modo_premium_completo(self, quantidade=5):
        """
        Execução completa do modo premium corrigido
        """
        print("🎯 SISTEMA ASSIMÉTRICO PREMIUM - VERSÃO CORRIGIDA")
        print("=" * 60)
        print("🎮 Foco: Faixa 11-13 acertos (máximo valor)")
        print()
        
        # Gera combinações
        combinacoes = self.gerar_combinacoes_premium_corrigido(quantidade)
        
        if not combinacoes:
            print("❌ Nenhuma combinação gerada")
            return None
        
        # Salva resultados
        arquivo_salvo = self.salvar_resultados_corrigido(combinacoes)
        
        # Exibe resumo
        print(f"\n📊 RESUMO DA EXECUÇÃO")
        print("-" * 40)
        print(f"✅ Combinações geradas: {len(combinacoes)}")
        
        if combinacoes:
            scores = [c['score_total'] for c in combinacoes]
            score_medio = sum(scores) / len(scores)
            print(f"📈 Score médio: {score_medio:.1f}")
            print(f"🏆 Score máximo: {max(scores):.1f}")
            print(f"📉 Score mínimo: {min(scores):.1f}")
        
        print(f"💾 Arquivo: {arquivo_salvo}")
        
        return {
            'combinacoes': combinacoes,
            'arquivo': arquivo_salvo,
            'resumo': {
                'quantidade': len(combinacoes),
                'score_medio': float(sum(scores) / len(scores)) if combinacoes else 0,
                'score_max': float(max(scores)) if combinacoes else 0,
                'score_min': float(min(scores)) if combinacoes else 0
            }
        }

def main():
    """Demonstração do sistema corrigido"""
    print("🚀 Iniciando Sistema Assimétrico Premium Corrigido...")
    
    sistema = SistemaAssimetricoPremiumCorrigido()
    resultado = sistema.executar_modo_premium_completo(5)
    
    if resultado:
        print(f"\n🎯 SUAS COMBINAÇÕES PREMIUM:")
        print("=" * 50)
        
        for comb in resultado['combinacoes']:
            print(f"🎲 {comb['numeros']}")
            print(f"   Score: {comb['score_total']:.1f} | Soma: {comb['detalhes']['soma_total']}")
            print(f"   Pares: {comb['detalhes']['qtd_pares']}/Ímpares: {comb['detalhes']['qtd_impares']}")
            print()
        
        print("✅ Sistema premium funcionando perfeitamente!")
        print("🍀 Boa sorte nas suas apostas!")

if __name__ == "__main__":
    main()

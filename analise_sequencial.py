"""
🔍 Análise Sequencial de Padrões - LotoScope
Analisa comportamento histórico dos valores menor_que, maior_que e igual_ao_ultimo
"""
import sys
import os

# Adicionar o diretório do database ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'lotofacil_lite'))

try:
    from database_config import db_config

# 🚀 SISTEMA DE OTIMIZAÇÃO DE BANCO
try:
    from database_optimizer import DatabaseOptimizer
    _db_optimizer = DatabaseOptimizer()
except ImportError:
    _db_optimizer = None

    print("✅ Módulo database_config importado com sucesso")
except ImportError as e:
    print(f"❌ Erro ao importar database_config: {e}")
    sys.exit(1)

from collections import defaultdict, Counter
import statistics

class AnaliseSequencial:
    def __init__(self):
        self.dados_historicos = []
        self.ultimo_concurso = None
        
    def carregar_dados_completos(self):
        """Carrega todos os dados históricos para análise sequencial"""
        print("📊 CARREGANDO DADOS HISTÓRICOS COMPLETOS...")
        
        query = """
        SELECT 
            concurso,
            menor_que_ultimo,
            maior_que_ultimo,
            igual_ao_ultimo,
            SomaTotal
        FROM RESULTADOS_INT 
        WHERE menor_que_ultimo IS NOT NULL 
            AND maior_que_ultimo IS NOT NULL 
            AND igual_ao_ultimo IS NOT NULL
        ORDER BY concurso ASC
        """
        
        try:
            conn = db_config.get_connection()
            cursor = conn.cursor()
            cursor.execute(query)
            resultados = cursor.fetchall()
            
            if resultados:
                # Converter para lista de dicionários
                colunas = [desc[0] for desc in cursor.description]
                self.dados_historicos = [dict(zip(colunas, row)) for row in resultados]
                
                # Último concurso
                self.ultimo_concurso = self.dados_historicos[-1]
                
                print(f"✅ {len(resultados)} concursos carregados")
                print(f"📅 Período: {self.dados_historicos[0]['concurso']} → {self.ultimo_concurso['concurso']}")
                cursor.close()
                conn.close()
                return True
            else:
                print("❌ Nenhum dado histórico encontrado")
                return False
                
        except Exception as e:
            print(f"❌ Erro ao carregar dados: {e}")
            return False
    
    def analisar_padrao_sequencial(self, campo, valor_atual):
        """
        Analisa o comportamento sequencial de um campo específico
        
        Args:
            campo: 'menor_que_ultimo', 'maior_que_ultimo' ou 'igual_ao_ultimo'
            valor_atual: valor do campo no último sorteio
        """
        print(f"\n🔍 ANALISANDO PADRÃO: {campo} = {valor_atual}")
        
        # Encontrar todas as ocorrências do valor atual
        ocorrencias = []
        proximos_valores = []
        
        for i in range(len(self.dados_historicos) - 1):  # -1 porque precisamos do próximo
            concurso_atual = self.dados_historicos[i]
            proximo_concurso = self.dados_historicos[i + 1]
            
            if concurso_atual[campo] == valor_atual:
                ocorrencias.append({
                    'concurso': concurso_atual['concurso'],
                    'valor_atual': concurso_atual[campo],
                    'proximo_valor': proximo_concurso[campo],
                    'proximo_concurso': proximo_concurso['concurso']
                })
                proximos_valores.append(proximo_concurso[campo])
        
        if not ocorrencias:
            print(f"❌ Nenhuma ocorrência histórica encontrada para {campo} = {valor_atual}")
            return None
        
        # Análise estatística
        contador = Counter(proximos_valores)
        total_ocorrencias = len(proximos_valores)
        
        # Calcular estatísticas
        media = statistics.mean(proximos_valores)
        mediana = statistics.median(proximos_valores)
        
        # Criar distribuição de probabilidades
        distribuicao = {}
        for valor in range(0, 16):  # 0 a 15 possíveis
            count = contador.get(valor, 0)
            percentual = (count / total_ocorrencias) * 100 if total_ocorrencias > 0 else 0
            distribuicao[valor] = {
                'count': count,
                'percentual': percentual
            }
        
        # Encontrar faixa mais provável (valores com maior probabilidade)
        valores_ordenados = sorted(contador.items(), key=lambda x: x[1], reverse=True)
        
        # Calcular intervalo de confiança (80% dos casos)
        valores_acumulados = 0
        faixa_80_porcento = []
        
        for valor, count in valores_ordenados:
            valores_acumulados += count
            faixa_80_porcento.append(valor)
            if valores_acumulados >= total_ocorrencias * 0.8:
                break
        
        faixa_80_porcento.sort()
        
        resultado = {
            'campo': campo,
            'valor_atual': valor_atual,
            'total_ocorrencias': total_ocorrencias,
            'ocorrencias_detalhadas': ocorrencias,
            'proximos_valores': proximos_valores,
            'distribuicao': distribuicao,
            'estatisticas': {
                'media': round(media, 2),
                'mediana': mediana,
                'minimo': min(proximos_valores),
                'maximo': max(proximos_valores)
            },
            'mais_frequentes': valores_ordenados[:5],  # Top 5
            'faixa_80_porcento': {
                'valores': faixa_80_porcento,
                'minimo': min(faixa_80_porcento),
                'maximo': max(faixa_80_porcento)
            }
        }
        
        self._imprimir_analise(resultado)
        return resultado
    
    def _imprimir_analise(self, resultado):
        """Imprime a análise de forma formatada"""
        campo = resultado['campo']
        valor_atual = resultado['valor_atual']
        total = resultado['total_ocorrencias']
        
        print(f"📊 Total de ocorrências históricas: {total}")
        print(f"📈 Estatísticas dos próximos valores:")
        print(f"   └─ Média: {resultado['estatisticas']['media']}")
        print(f"   └─ Mediana: {resultado['estatisticas']['mediana']}")
        print(f"   └─ Amplitude: {resultado['estatisticas']['minimo']} → {resultado['estatisticas']['maximo']}")
        
        print(f"\n🎯 TOP 5 VALORES MAIS FREQUENTES:")
        for i, (valor, count) in enumerate(resultado['mais_frequentes'], 1):
            percentual = (count / total) * 100
            print(f"   {i}. Valor {valor}: {count} vezes ({percentual:.1f}%)")
        
        print(f"\n📋 DISTRIBUIÇÃO COMPLETA:")
        for valor in range(0, 16):
            data = resultado['distribuicao'][valor]
            if data['count'] > 0:
                barra = "█" * int(data['percentual'] / 5)  # Barra visual
                print(f"   Valor {valor:2d}: {data['count']:2d} vezes ({data['percentual']:5.1f}%) {barra}")
        
        faixa = resultado['faixa_80_porcento']
        print(f"\n🎯 PREVISÃO (80% dos casos):")
        print(f"   └─ Próximo {campo} provavelmente entre {faixa['minimo']} e {faixa['maximo']}")
        print(f"   └─ Valores mais prováveis: {', '.join(map(str, faixa['valores'][:5]))}")
    
    def analise_completa_ultimo_sorteio(self):
        """Executa análise completa baseada no último sorteio"""
        if not self.ultimo_concurso:
            print("❌ Dados do último concurso não carregados")
            return None
        
        print("="*80)
        print("🔍 ANÁLISE SEQUENCIAL DE PADRÕES - ÚLTIMO SORTEIO")
        print("="*80)
        
        ultimo = self.ultimo_concurso
        print(f"📅 Concurso analisado: {ultimo['concurso']}")
        print(f"📊 Valores atuais:")
        print(f"   └─ menor_que_ultimo = {ultimo['menor_que_ultimo']}")
        print(f"   └─ maior_que_ultimo = {ultimo['maior_que_ultimo']}")
        print(f"   └─ igual_ao_ultimo = {ultimo['igual_ao_ultimo']}")
        
        # Analisar cada campo
        resultados = {}
        
        for campo in ['menor_que_ultimo', 'maior_que_ultimo', 'igual_ao_ultimo']:
            valor_atual = ultimo[campo]
            resultado = self.analisar_padrao_sequencial(campo, valor_atual)
            if resultado:
                resultados[campo] = resultado
        
        # Resumo executivo
        print("\n" + "="*80)
        print("📋 RESUMO EXECUTIVO - PREVISÕES PARA PRÓXIMO CONCURSO")
        print("="*80)
        
        for campo, resultado in resultados.items():
            faixa = resultado['faixa_80_porcento']
            mais_freq = resultado['mais_frequentes'][0]  # Mais frequente
            
            print(f"🎯 {campo.upper()}:")
            print(f"   └─ Atual: {resultado['valor_atual']}")
            print(f"   └─ Previsão: {faixa['minimo']} a {faixa['maximo']} (80% confiança)")
            print(f"   └─ Mais provável: {mais_freq[0]} ({(mais_freq[1]/resultado['total_ocorrencias']*100):.1f}%)")
            print()
        
        return resultados
    
    def validar_previsao_anterior(self):
        """Valida as previsões com base no penúltimo sorteio"""
        if len(self.dados_historicos) < 2:
            print("❌ Dados insuficientes para validação")
            return None
        
        penultimo = self.dados_historicos[-2]
        ultimo = self.dados_historicos[-1]
        
        print("\n" + "="*60)
        print("✅ VALIDAÇÃO DA PREVISÃO ANTERIOR")
        print("="*60)
        
        print(f"📅 Concurso base: {penultimo['concurso']}")
        print(f"📅 Concurso real: {ultimo['concurso']}")
        
        acertos = 0
        total = 0
        
        for campo in ['menor_que_ultimo', 'maior_que_ultimo', 'igual_ao_ultimo']:
            valor_base = penultimo[campo]
            valor_real = ultimo[campo]
            
            # Simular previsão baseada no penúltimo
            print(f"\n🔍 {campo}:")
            print(f"   └─ Base ({penultimo['concurso']}): {valor_base}")
            print(f"   └─ Real ({ultimo['concurso']}): {valor_real}")
            
            # Para validação completa, seria necessário calcular a previsão
            # Por hora, apenas mostramos os valores
            total += 1
        
        print(f"\n📊 Próxima implementação: calcular precisão das previsões")

def main():
    """Função principal"""
    print("🚀 INICIANDO ANÁLISE SEQUENCIAL DE PADRÕES...")
    
    analise = AnaliseSequencial()
    
    # Carregar dados
    if not analise.carregar_dados_completos():
        print("❌ Falha ao carregar dados")
        return
    
    # Executar análise completa
    resultados = analise.analise_completa_ultimo_sorteio()
    
    # Validação (demonstrativa)
    analise.validar_previsao_anterior()
    
    print("\n" + "="*80)
    print("✅ ANÁLISE SEQUENCIAL CONCLUÍDA!")
    print("="*80)

if __name__ == "__main__":
    main()
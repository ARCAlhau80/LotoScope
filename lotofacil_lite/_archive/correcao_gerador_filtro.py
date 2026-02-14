#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🎯 CORREÇÃO DO GERADOR ACADÊMICO - FILTRO CORRETO
================================================

PROBLEMA IDENTIFICADO:
• O gerar_multiplas_combinacoes não respeita os filtros corretamente
• Ele para em "quantidade * 3" tentativas, mesmo que poucos passem pelo filtro
• Retorna combinações inválidas quando esgota as tentativas

SOLUÇÃO:
• Tentar até max_tentativas para encontrar combinações que passam pelo filtro
• Retornar APENAS as combinações que passam pelo filtro
• Se pedir 100.000 e só 19 passam pelo filtro, retornar apenas 19

Autor: AR CALHAU
Data: 14 de Setembro 2025
"""

def criar_metodo_gerar_multiplas_combinacoes_corrigido():
    """
    Cria a versão corrigida do método gerar_multiplas_combinacoes
    """
    
    codigo_corrigido = '''
    def gerar_multiplas_combinacoes(self, quantidade: int = 10, qtd_numeros: int = 15, max_tentativas: int = 1000) -> List[List[int]]:
        """Gera múltiplas combinações com insights dinâmicos - VERSÃO CORRIGIDA
        
        Args:
            quantidade: Número MÁXIMO de combinações a gerar
            qtd_numeros: Quantidade de números por combinação (15-20) 
            max_tentativas: Máximo de tentativas TOTAIS para encontrar combinações válidas (1-3268760)
            
        Returns:
            List[List[int]]: Lista com APENAS as combinações que passam pelo filtro
            
        CORREÇÃO APLICADA:
        • Se filtro está ativo, retorna APENAS combinações que passam pelo filtro
        • Se pedir 100.000 mas só 19 passam pelo filtro, retorna apenas 19
        • Usa max_tentativas como limite TOTAL de tentativas, não por combinação
        """
        print(f"\\n🎯 GERADOR ACADÊMICO DINÂMICO - {qtd_numeros} NÚMEROS (CORRIGIDO)")
        print("=" * 70)
        
        # Validação do parâmetro max_tentativas
        if not 1 <= max_tentativas <= 3268760:
            raise ValueError(f"max_tentativas deve estar entre 1 e 3.268.760. Valor informado: {max_tentativas}")
        
        print(f"⚙️  Máximo de tentativas TOTAIS: {max_tentativas:,}")
        print(f"🎯 Quantidade máxima solicitada: {quantidade:,}")
        
        if self.usar_filtro_validado:
            print(f"🔍 FILTRO ATIVO: Acertos entre {self.min_acertos_filtro}-{self.max_acertos_filtro}")
            print(f"📊 Combinações de referência: Jogo 1 e Jogo 2")
        else:
            print(f"⚠️  FILTRO DESABILITADO: Todas as combinações serão aceitas")
        
        # Mostra status de aprendizado da IA se disponível
        if self.monitor_aprendizado:
            print("\\n🧠 STATUS DE APRENDIZADO DA IA:")
            print("-" * 40)
            self.monitor_aprendizado.mostrar_status_aprendizado()
        
        # Calcula insights se necessário
        if not self.dados_carregados:
            if not self.calcular_insights_dinamicos():
                print("❌ Falha ao carregar dados da base")
                return []
        
        # Mostra informações da aposta
        config = self.configuracoes_aposta[qtd_numeros]
        print(f"\\n💰 CONFIGURAÇÃO DA APOSTA:")
        print(f"   • Números por jogo: {qtd_numeros}")
        print(f"   • Custo unitário: R$ {config['custo']:.2f}")
        
        # Mostra insights calculados dinamicamente
        self._mostrar_insights_dinamicos()
        
        # VARIÁVEIS DE CONTROLE CORRIGIDAS
        combinacoes_validas = []
        combinacoes_set = set()
        tentativas_totais = 0
        combinacoes_rejeitadas = 0
        
        print(f"\\n🔬 Gerando com metodologia acadêmica dinâmica (CORRIGIDO)...")
        
        # 🎯 LOOP PRINCIPAL CORRIGIDO
        while len(combinacoes_validas) < quantidade and tentativas_totais < max_tentativas:
            tentativas_totais += 1
            
            # 🔺 Decide se usa método da pirâmide ou acadêmico padrão
            if self.usar_piramide and tentativas_totais % 3 == 0:  # 33% das vezes usa pirâmide
                # Para a pirâmide, usa tentativas menores para evitar loops
                max_tent_piramide = min(1000, max_tentativas // 10)
                combinacao = self.gerar_combinacao_piramide(qtd_numeros, max_tent_piramide)
            else:
                # Para acadêmico, usa tentativas menores para evitar loops
                max_tent_academico = min(1000, max_tentativas // 10)
                combinacao = self.gerar_combinacao_academica(qtd_numeros, max_tent_academico)
            
            combinacao_tuple = tuple(sorted(combinacao))
            
            # Evita duplicatas
            if combinacao_tuple in combinacoes_set:
                continue
            
            # 🎯 VALIDAÇÃO DO FILTRO CORRIGIDA
            if self.usar_filtro_validado:
                if self.validar_combinacao_filtro(combinacao):
                    # ✅ Combinação passou no filtro
                    combinacoes_validas.append(combinacao)
                    combinacoes_set.add(combinacao_tuple)
                    
                    if len(combinacoes_validas) % 5 == 0:
                        taxa_sucesso = len(combinacoes_validas) / tentativas_totais * 100
                        print(f"   ✅ {len(combinacoes_validas)} válidas encontradas (Taxa: {taxa_sucesso:.3f}%)")
                else:
                    # ❌ Combinação rejeitada pelo filtro
                    combinacoes_rejeitadas += 1
                    
                    if combinacoes_rejeitadas % 1000 == 0:
                        acertos = self.calcular_acertos_filtros(combinacao)
                        taxa_rejeicao = combinacoes_rejeitadas / tentativas_totais * 100
                        print(f"   🔍 {combinacoes_rejeitadas} rejeitadas | "
                              f"Última: J1:{acertos['jogo_1']}, J2:{acertos['jogo_2']} | "
                              f"Taxa rejeição: {taxa_rejeicao:.1f}%")
            else:
                # 🔓 Filtro desabilitado - aceita todas
                combinacoes_validas.append(combinacao)
                combinacoes_set.add(combinacao_tuple)
                
                if len(combinacoes_validas) % 100 == 0:
                    print(f"   ✅ {len(combinacoes_validas)} combinações geradas (sem filtro)")
        
        # 📊 ESTATÍSTICAS FINAIS
        print(f"\\n📊 ESTATÍSTICAS FINAIS:")
        print(f"   • Tentativas totais: {tentativas_totais:,}")
        print(f"   • Combinações válidas encontradas: {len(combinacoes_validas):,}")
        print(f"   • Combinações rejeitadas: {combinacoes_rejeitadas:,}")
        
        if tentativas_totais > 0:
            taxa_sucesso = len(combinacoes_validas) / tentativas_totais * 100
            print(f"   • Taxa de sucesso: {taxa_sucesso:.4f}%")
        
        # 📈 ANÁLISE DO RESULTADO
        if len(combinacoes_validas) == 0:
            print(f"\\n❌ NENHUMA COMBINAÇÃO VÁLIDA ENCONTRADA!")
            print(f"   • Filtro muito restritivo ou dados insuficientes")
            print(f"   • Considere aumentar max_tentativas ou ajustar filtros")
        elif len(combinacoes_validas) < quantidade:
            print(f"\\n⚠️  QUANTIDADE LIMITADA PELO FILTRO:")
            print(f"   • Solicitado: {quantidade:,}")
            print(f"   • Encontrado: {len(combinacoes_validas):,}")
            print(f"   • Esgotadas {tentativas_totais:,} tentativas")
            print(f"   • Apenas {len(combinacoes_validas)} combinações passam pelo filtro")
        else:
            print(f"\\n✅ QUANTIDADE COMPLETA GERADA:")
            print(f"   • {len(combinacoes_validas):,} combinações válidas")
            print(f"   • Todas passaram pelo filtro acadêmico")
        
        # Calcular custo real
        custo_real = config['custo'] * len(combinacoes_validas)
        print(f"\\n💰 CUSTO REAL: R$ {custo_real:.2f}")
        
        if len(combinacoes_validas) > 0:
            print(f"\\n✅ RETORNANDO {len(combinacoes_validas)} COMBINAÇÕES VALIDADAS")
            self._analisar_combinacoes_geradas(combinacoes_validas, qtd_numeros)
        
        # 🔗 INTEGRAÇÃO DE APRENDIZADO: Registra combinações para validação futura
        try:
            if self.monitor_aprendizado and hasattr(self.monitor_aprendizado, 'sistema_continuo') and len(combinacoes_validas) > 0:
                # Estima próximos 2 concursos para validação
                from datetime import datetime, timedelta
                hoje = datetime.now()
                
                # Calcula próximos concursos (terça/quinta/sábado)
                proximos_concursos = []
                data_atual = hoje
                for _ in range(10):  # Verifica próximos 10 dias
                    weekday = data_atual.weekday()  # 0=segunda, 1=terça, 2=quarta, etc
                    if weekday in [1, 3, 5]:  # Terça(1), Quinta(3), Sábado(5)
                        # Estima número do concurso (aproximação baseada em datas)
                        dias_desde_inicio_2025 = (data_atual - datetime(2025, 1, 1)).days
                        concurso_estimado = 3400 + (dias_desde_inicio_2025 // 2)  # ~3 por semana
                        proximos_concursos.append(concurso_estimado)
                        if len(proximos_concursos) >= 2:
                            break
                    data_atual += timedelta(days=1)
                
                # Registra as combinações para validação futura
                for i, combinacao in enumerate(combinacoes_validas):
                    self.monitor_aprendizado.sistema_continuo.registrar_predicao(
                        concurso=proximos_concursos[0] if proximos_concursos else 9999,
                        combinacao=combinacao,
                        confianca=0.8,  # Confiança baseada na validação acadêmica
                        origem=f"gerador_academico_dinamico_corrigido_{i+1}"
                    )
                
                print(f"\\n🧠 {len(combinacoes_validas)} combinações registradas no sistema de aprendizado")
        
        except Exception as e:
            print(f"\\n⚠️ Erro no sistema de aprendizado: {e}")
        
        return combinacoes_validas
    '''
    
    return codigo_corrigido

def main():
    """
    Mostra o código corrigido para aplicar no gerador acadêmico
    """
    print("🎯 CORREÇÃO DO GERADOR ACADÊMICO - FILTRO CORRETO")
    print("=" * 60)
    print()
    print("🔍 PROBLEMA IDENTIFICADO:")
    print("• gerar_multiplas_combinacoes não respeita filtros corretamente")
    print("• Para em 'quantidade * 3' tentativas mesmo que poucos passem pelo filtro")
    print("• Retorna combinações inválidas quando esgota tentativas")
    print()
    print("✅ SOLUÇÃO:")
    print("• Usar max_tentativas como limite TOTAL de tentativas")
    print("• Retornar APENAS combinações que passam pelo filtro")
    print("• Se pedir 100.000 e só 19 passam, retornar apenas 19")
    print()
    print("🚀 RESULTADO ESPERADO:")
    print("• Se existem apenas 19 combinações que passam pelo filtro,")
    print("  retorna apenas 19, independente da quantidade solicitada")
    print("• Sistema honesto e matematicamente correto")
    print()
    
    codigo = criar_metodo_gerar_multiplas_combinacoes_corrigido()
    
    print("💾 Código corrigido gerado!")
    print("📋 Para aplicar:")
    print("1. Substitua o método gerar_multiplas_combinacoes no arquivo:")
    print("   C:\\Users\\AR CALHAU\\source\\repos\\LotoScope\\lotofacil_lite\\gerador_academico_dinamico.py")
    print("2. Substitua a partir da linha ~1109 até o final do método")
    print("3. Teste com quantidade pequena primeiro (ex: 100)")
    print()
    
    print("🎯 TESTE SUGERIDO:")
    print("• Gere 100.000 combinações com filtro ativo")
    print("• Veja quantas realmente passam pelo filtro")
    print("• Deve retornar apenas as válidas")

if __name__ == "__main__":
    main()
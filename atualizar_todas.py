import sys
sys.path.insert(0, '.')

from shared.loterias.atualizador_lotofacil import AtualizadorLotofacil
from shared.loterias.atualizador_megasena import AtualizadorMegaSena
from shared.loterias.atualizador_quina import AtualizadorQuina
from shared.loterias.atualizador_duplasena import AtualizadorDuplaSena
from shared.loterias.atualizador_lotomania import AtualizadorLotomania
from shared.loterias.atualizador_diadesorte import AtualizadorDiaDeSorte
from shared.loterias.atualizador_timemania import AtualizadorTimemania
from shared.loterias.atualizador_supersete import AtualizadorSuperSete
from shared.loterias.atualizador_milionaria import AtualizadorMilionaria

loterias = [
    ("Lotofácil", AtualizadorLotofacil),
    ("Mega-Sena", AtualizadorMegaSena),
    ("Quina", AtualizadorQuina),
    ("Dupla Sena", AtualizadorDuplaSena),
    ("Lotomania", AtualizadorLotomania),
    ("Dia de Sorte", AtualizadorDiaDeSorte),
    ("Timemania", AtualizadorTimemania),
    ("Super Sete", AtualizadorSuperSete),
    ("Mais Milionária", AtualizadorMilionaria),
]

for nome, cls in loterias:
    try:
        print(f"\n=== Atualizando {nome} ===")
        cls().atualizar_completo(qtde_por_vez=5)
        print(f"OK: {nome}")
    except Exception as e:
        print(f"Erro na {nome}: {e}")

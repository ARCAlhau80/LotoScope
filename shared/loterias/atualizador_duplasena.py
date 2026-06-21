from typing import List, Dict, Optional
from .atualizador_base import AtualizadorBase
from .config_base import LotteryRegistry


class AtualizadorDuplaSena(AtualizadorBase):
    def __init__(self, get_connection=None):
        config = LotteryRegistry.get("duplasena")
        if not config:
            raise ValueError("Dupla Sena não registrada no registry")
        super().__init__(config, get_connection)

    def extra_campos_estatisticos(self, concurso: int, numeros: List[int], data_sorteio: str, dados_api: Optional[dict] = None) -> Dict:
        if not dados_api:
            return {}
        dezenas2 = [int(n) for n in dados_api.get("listaDezenasSegundoSorteio", [])]
        if len(dezenas2) != 6:
            print(f"⚠️ 2º sorteio inválido concurso {concurso}: {len(dezenas2)} números")
            return {}
        return {f"S2_N{i}": n for i, n in enumerate(sorted(dezenas2), 1)}

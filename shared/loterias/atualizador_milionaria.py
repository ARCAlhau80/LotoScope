from typing import List, Dict, Optional
from .atualizador_base import AtualizadorBase
from .config_base import LotteryRegistry


class AtualizadorMilionaria(AtualizadorBase):
    def __init__(self, get_connection=None):
        config = LotteryRegistry.get("maismilionaria")
        if not config:
            raise ValueError("Mais Milionária não registrada no registry")
        super().__init__(config, get_connection)

    def extra_campos_estatisticos(self, concurso: int, numeros: List[int], data_sorteio: str, dados_api: Optional[dict] = None) -> Dict:
        if not dados_api:
            return {}
        trevos = dados_api.get("trevosSorteados") or dados_api.get("trevos") or []
        trevos_int = [int(t) for t in trevos if str(t).isdigit()]
        if len(trevos_int) != 2:
            return {}
        return {"T1": trevos_int[0], "T2": trevos_int[1]}

from typing import Dict, List, Optional

from .atualizador_base import AtualizadorBase
from .config_base import LotteryRegistry
from .mes_sorte import mes_por_nome


class AtualizadorDiaDeSorte(AtualizadorBase):
    def __init__(self, get_connection=None):
        config = LotteryRegistry.get("diadesorte")
        if not config:
            raise ValueError("Dia de Sorte não registrada no registry")
        super().__init__(config, get_connection)

    def extra_campos_estatisticos(
        self,
        concurso: int,
        numeros: List[int],
        data_sorteio: str,
        dados_api: Optional[dict] = None,
    ) -> Dict:
        """Guarda o Mês da Sorte (1-12) devolvido pela API da Caixa.

        A API expõe o mês em `nomeTimeCoracaoMesSorte` (ex.: "Outubro").
        Sem ele, o conferidor não consegue pagar o bônus de R$ 2,50.
        """
        dados = dados_api or {}
        mes = mes_por_nome(dados.get("nomeTimeCoracaoMesSorte"))
        return {"Mes_Sorte": mes} if mes is not None else {}

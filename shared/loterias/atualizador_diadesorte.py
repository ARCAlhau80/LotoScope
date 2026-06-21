from .atualizador_base import AtualizadorBase
from .config_base import LotteryRegistry


class AtualizadorDiaDeSorte(AtualizadorBase):
    def __init__(self, get_connection=None):
        config = LotteryRegistry.get("diadesorte")
        if not config:
            raise ValueError("Dia de Sorte não registrada no registry")
        super().__init__(config, get_connection)

from .atualizador_base import AtualizadorBase
from .config_base import LotteryRegistry


class AtualizadorMegaSena(AtualizadorBase):
    def __init__(self, get_connection=None):
        config = LotteryRegistry.get("megasena")
        if not config:
            raise ValueError("Mega-Sena não registrada no registry")
        super().__init__(config, get_connection)

from .atualizador_base import AtualizadorBase
from .config_base import LotteryRegistry


class AtualizadorQuina(AtualizadorBase):
    def __init__(self, get_connection=None):
        config = LotteryRegistry.get("quina")
        if not config:
            raise ValueError("Quina não registrada no registry")
        super().__init__(config, get_connection)

from .atualizador_base import AtualizadorBase
from .config_base import LotteryRegistry


class AtualizadorLotomania(AtualizadorBase):
    def __init__(self, get_connection=None):
        config = LotteryRegistry.get("lotomania")
        if not config:
            raise ValueError("Lotomania não registrada no registry")
        super().__init__(config, get_connection)

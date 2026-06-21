from .atualizador_base import AtualizadorBase
from .config_base import LotteryRegistry


class AtualizadorTimemania(AtualizadorBase):
    def __init__(self, get_connection=None):
        config = LotteryRegistry.get("timemania")
        if not config:
            raise ValueError("Timemania não registrada no registry")
        super().__init__(config, get_connection)

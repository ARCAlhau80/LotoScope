from .atualizador_base import AtualizadorBase
from .config_base import LotteryRegistry


class AtualizadorSuperSete(AtualizadorBase):
    def __init__(self, get_connection=None):
        config = LotteryRegistry.get("supersete")
        if not config:
            raise ValueError("Super Sete não registrada no registry")
        super().__init__(config, get_connection)

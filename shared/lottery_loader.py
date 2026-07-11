from typing import List, Optional
from shared.loterias import (
    CONFIG_LOTOFACIL,
    CONFIG_MEGASENA,
    CONFIG_QUINA,
    CONFIG_DUPLASENA,
    CONFIG_LOTOMANIA,
    CONFIG_DIADESORTE,
    CONFIG_TIMEMANIA,
    CONFIG_SUPERSETE,
    CONFIG_MILIONARIA,
)
from shared.loterias.config_base import LotteryConfig, LotteryRegistry

_TODAS_AS_LOTERIAS = [
    CONFIG_LOTOFACIL,
    CONFIG_MEGASENA,
    CONFIG_QUINA,
    CONFIG_DUPLASENA,
    CONFIG_LOTOMANIA,
    CONFIG_DIADESORTE,
    CONFIG_TIMEMANIA,
    CONFIG_SUPERSETE,
    CONFIG_MILIONARIA,
]


def carregar_todas_loterias() -> List[LotteryConfig]:
    return _TODAS_AS_LOTERIAS


def get_loteria(lottery_id: str) -> Optional[LotteryConfig]:
    return LotteryRegistry.get(lottery_id)


def listar_ids_loterias() -> List[str]:
    return LotteryRegistry.ids_disponiveis()

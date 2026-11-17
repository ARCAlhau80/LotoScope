"""Mês da Sorte do Dia de Sorte (1 = Janeiro ... 12 = Dezembro)."""

import unicodedata
from typing import Optional

MESES_SORTE = [
    "Janeiro",
    "Fevereiro",
    "Março",
    "Abril",
    "Maio",
    "Junho",
    "Julho",
    "Agosto",
    "Setembro",
    "Outubro",
    "Novembro",
    "Dezembro",
]

MES_SORTE_MIN = 1
MES_SORTE_MAX = 12


def _normalizar(texto: str) -> str:
    sem_acento = unicodedata.normalize("NFKD", texto or "")
    return "".join(c for c in sem_acento if not unicodedata.combining(c)).strip().lower()


_MAPA_NOMES = {_normalizar(nome): i for i, nome in enumerate(MESES_SORTE, start=1)}


def mes_por_nome(nome: Optional[str]) -> Optional[int]:
    """Converte o nome vindo da API da Caixa ("Outubro") no número 1-12."""
    if not nome:
        return None
    chave = _normalizar(str(nome))
    # A API pode devolver prefixos como "Mês de Outubro".
    if chave not in _MAPA_NOMES:
        for parte in chave.split():
            if parte in _MAPA_NOMES:
                return _MAPA_NOMES[parte]
        return None
    return _MAPA_NOMES[chave]


def nome_mes(mes: Optional[int]) -> Optional[str]:
    if mes is None:
        return None
    try:
        numero = int(mes)
    except (TypeError, ValueError):
        return None
    if MES_SORTE_MIN <= numero <= MES_SORTE_MAX:
        return MESES_SORTE[numero - 1]
    return None

"""Parser e validação de jogos para o módulo Apostador.

Suporta arquivos TXT/CSV (números separados por ';' ou ',', um jogo por linha)
e XLSX (1ª coluna, mesmas regras do Apostador C# original).
"""

from pathlib import Path
from typing import List, Dict, Any


class JogoInvalidoError(Exception):
    """Linha do arquivo não pôde ser interpretada como jogo."""


class FormatoNaoSuportadoError(Exception):
    """Extensão de arquivo sem suporte."""


def _split_jogo(linha: str) -> List[int]:
    import re
    partes = re.split(r"[;,]", linha.strip())
    numeros: List[int] = []
    for parte in partes:
        texto = parte.strip()
        if not texto:
            continue
        try:
            numeros.append(int(texto))
        except ValueError:
            raise JogoInvalidoError(f"Número inválido: '{texto}'")
    return sorted(numeros)


def parse_jogos_texto(texto: str) -> List[List[int]]:
    """Interpreta o conteúdo de um arquivo de texto/CSV.

    Cada linha não vazia representa um jogo. Números separados por ';' ou ','.
    Uma linha que não seja numérica e não pareça jogo (ex.: header) é ignorada.
    """
    jogos: List[List[int]] = []
    for linha in texto.splitlines():
        linha_limpa = linha.strip()
        if not linha_limpa:
            continue
        if not any(c.isdigit() for c in linha_limpa):
            continue
        numeros = _split_jogo(linha_limpa)
        if not numeros:
            continue
        jogos.append(numeros)
    return jogos


def parse_jogos_xlsx(caminho: str) -> List[List[int]]:
    """Lê jogos de uma planilha .xlsx (1ª coluna, números separados por ';')."""
    try:
        from openpyxl import load_workbook
    except ImportError as exc:
        raise FormatoNaoSuportadoError(
            "openpyxl não instalado. Instale com: pip install openpyxl"
        ) from exc

    wb = load_workbook(caminho, read_only=True, data_only=True)
    jogos: List[List[int]] = []
    try:
        ws = wb.active
        for linha in ws.iter_rows(min_col=1, max_col=1, values_only=True):
            valor = linha[0]
            if valor is None:
                continue
            texto = str(valor).strip()
            if not texto:
                continue
            if not any(c.isdigit() for c in texto):
                continue
            numeros = _split_jogo(texto)
            if numeros:
                jogos.append(numeros)
    finally:
        wb.close()
    return jogos


def parse_arquivo_jogos(caminho: str) -> List[List[int]]:
    """Interpreta um arquivo de jogos pela extensão (.txt/.csv/.xlsx)."""
    ext = Path(caminho).suffix.lower()
    if ext in (".txt", ".csv"):
        texto = Path(caminho).read_text(encoding="utf-8", errors="replace")
        return parse_jogos_texto(texto)
    if ext == ".xlsx":
        return parse_jogos_xlsx(caminho)
    raise FormatoNaoSuportadoError(f"Extensão não suportada: '{ext}'")


def validar_jogos(
    cfg: Any,
    jogos: List[List[int]],
) -> Dict[str, Any]:
    """Valida uma lista de jogos contra a config da loteria.

    cfg deve expor: numero_minimo, numero_maximo, numeros_por_jogo.

    Retorna:
        {"validos": [{"id", "numeros"}], "invalids": [{"id", "numeros", "mensagem"}]}
    """
    validos: List[Dict[str, Any]] = []
    invalidos: List[Dict[str, Any]] = []

    for idx, jogo in enumerate(jogos, start=1):
        numeros = sorted(jogo)
        erro = _validar_jogo(cfg, numeros)
        item = {"id": idx, "numeros": numeros}
        if erro:
            item["mensagem"] = erro
            invalidos.append(item)
        else:
            validos.append(item)

    return {"validos": validos, "invalids": invalidos}


def _validar_jogo(cfg: Any, numeros: List[int]) -> str | None:
    min_dezenas = cfg.numeros_por_jogo
    max_dezenas = getattr(cfg, "max_dezenas", None) or cfg.numeros_por_jogo
    min_val = cfg.numero_minimo
    max_val = cfg.numero_maximo

    qtd = len(numeros)
    if qtd < min_dezenas or qtd > max_dezenas:
        faixa = (
            f"{min_dezenas}" if min_dezenas == max_dezenas
            else f"{min_dezenas}-{max_dezenas}"
        )
        return f"Esperado {faixa} dezenas, recebido {qtd}"
    if len(set(numeros)) != len(numeros):
        return "Número duplicado no jogo"
    fora = [n for n in numeros if n < min_val or n > max_val]
    if fora:
        return f"Número fora da faixa ({min_val}-{max_val}): {fora[0]}"
    return None
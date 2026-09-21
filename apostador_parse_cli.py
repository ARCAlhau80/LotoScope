"""CLI do módulo Apostador: parse + validação de jogos.

Uso:
    python apostador_parse_cli.py <caminho_arquivo> --loteria <id> [--json]
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from shared.apostador.parser import parse_arquivo_jogos, validar_jogos, FormatoNaoSuportadoError, JogoInvalidoError
from shared.lottery_loader import get_loteria


def main() -> int:
    parser = argparse.ArgumentParser(description="Parse e validação de jogos para o módulo Apostador")
    parser.add_argument("caminho", help="Caminho do arquivo (txt/csv/xlsx)")
    parser.add_argument("--loteria", default="lotofacil", help="ID da loteria (default: lotofacil)")
    parser.add_argument("--json", action="store_true", help="Saída em JSON")
    args = parser.parse_args()

    cfg = get_loteria(args.loteria)
    if cfg is None:
        return _erro(f"Loteria desconhecida: {args.loteria}")

    try:
        jogos = parse_arquivo_jogos(args.caminho)
    except (FormatoNaoSuportadoError, JogoInvalidoError) as e:
        return _erro(str(e))
    except FileNotFoundError:
        return _erro(f"Arquivo não encontrado: {args.caminho}")

    resultado = validar_jogos(cfg, jogos)

    saida = {
        "success": True,
        "loteria": args.loteria,
        "total_jogos": len(jogos),
        "validos": resultado["validos"],
        "invalids": resultado["invalids"],
        "preco_base": None,
    }
    if args.json:
        print(json.dumps(saida, ensure_ascii=False))
    else:
        _print_humano(saida)
    return 0


def _erro(msg: str) -> int:
    print(json.dumps({"success": False, "error": msg}, ensure_ascii=False))
    return 1


def _print_humano(saida: dict) -> None:
    print(f"Loteria: {saida['loteria']}")
    print(f"Total de jogos: {saida['total_jogos']}")
    print(f"Válidos: {len(saida['validos'])} | Inválidos: {len(saida['invalids'])}")
    for jogo in saida["validos"]:
        print(f"  Jogo {jogo['id']}: {jogo['numeros']}")


if __name__ == "__main__":
    sys.exit(main())
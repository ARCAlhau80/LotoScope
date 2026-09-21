"""CLI do módulo Apostador: automação de preenchimento de volantes na Caixa.

Uso:
    python apostador_automacao_cli.py <caminho_arquivo> --loteria <id> [--headless] [--dry-run] [--json]

--dry-run  valida os jogos e simula o fluxo sem abrir o navegador (útil para teste).
"""
import argparse
import json
import sys
import time
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).resolve().parent))

from shared.apostador.parser import parse_arquivo_jogos, validar_jogos, FormatoNaoSuportadoError, JogoInvalidoError
from shared.apostador.automacao import AutomacaoCaixa, LoteriaNaoSuportadaError, SemJogosError
from shared.lottery_loader import get_loteria


def main() -> int:
    parser = argparse.ArgumentParser(description="Automação de preenchimento de volantes no Portal Loterias CAIXA")
    parser.add_argument("caminho", help="Caminho do arquivo com jogos (txt/csv/xlsx)")
    parser.add_argument("--loteria", default="lotofacil", help="ID da loteria (default: lotofacil)")
    parser.add_argument("--headless", action="store_true", help="Chrome em modo headless (ATENÇÃO: o anti-bot da Caixa bloqueia headless; use apenas para testes)")
    parser.add_argument("--dry-run", action="store_true", help="Simula o fluxo sem abrir o navegador")
    parser.add_argument("--user-data-dir", default=None, help="Perfil Chrome persistente (mantém o login). Default: workflow-graph/chrome-profile")
    parser.add_argument("--fechar-ao-final", action="store_true", help="Fecha o navegador ao final (default: mantém aberto para conferir/finalizar)")
    parser.add_argument("--attach", action="store_true", help="Anexa a um Chrome JÁ ABERTO e logado via CDP (não abre janela nova, não fecha o seu navegador)")
    parser.add_argument("--debug-port", type=int, default=None, help="Porta do remote-debugging do Chrome já aberto (ex.: 9222)")
    parser.add_argument("--json", action="store_true", help="Saída em JSON")
    args = parser.parse_args()

    cfg = get_loteria(args.loteria)
    if cfg is None:
        return _saida(args.json, success=False, error=f"Loteria desconhecida: {args.loteria}")

    try:
        jogos_brutos = parse_arquivo_jogos(args.caminho)
    except (FormatoNaoSuportadoError, JogoInvalidoError) as e:
        return _saida(args.json, success=False, error=str(e))
    except FileNotFoundError:
        return _saida(args.json, success=False, error=f"Arquivo não encontrado: {args.caminho}")

    resultado = validar_jogos(cfg, jogos_brutos)
    invalidos = resultado["invalids"]
    jogos_validos = [jogo["numeros"] for jogo in resultado["validos"]]

    if invalidos:
        return _saida(
            args.json,
            success=False,
            error=f"{len(invalidos)} jogo(s) inválido(s). Corrija e tente novamente.",
            invalids=invalidos,
        )

    if not jogos_validos:
        return _saida(args.json, success=False, error="Nenhum jogo válido no arquivo.")

    if args.dry_run:
        return _saida(
            args.json,
            success=True,
            dry_run=True,
            loteria=args.loteria,
            total_jogos=len(jogos_validos),
            mensagem=f"Dry-run OK: {len(jogos_validos)} jogos seriam preenchidos no volante.",
        )

    try:
        from shared.apostador.automacao import criar_driver_attach, criar_driver_novo

        if args.attach:
            # Anexa a um Chrome JÁ ABERTO e logado (CDP).
            if not args.debug_port:
                return _saida(args.json, success=False, error="--attach requer --debug-port (ex.: 9222)")
            driver = criar_driver_attach(porta=args.debug_port)
        else:
            user_data_dir = args.user_data_dir or str(
                Path(__file__).resolve().parent / "workflow-graph" / "chrome-profile"
            )
            driver = criar_driver_novo(user_data_dir=user_data_dir, headless=args.headless)

        auto = AutomacaoCaixa(driver)
        erro: Optional[str] = None
        try:
            auto.abrir_portal()
            progresso = []
            auto.realizar_apostas(
                args.loteria,
                jogos_validos,
                progresso_callback=lambda p: progresso.append(p),
            )
        except Exception as e:
            erro = f"Erro na automação: {e}"
        finally:
            if erro:
                print(json.dumps({
                    "success": False,
                    "error": erro,
                    "navegador_aberto": True,
                    "mensagem": (
                        "Erro ao preencher (provavelmente não está logado). "
                        "Navegador mantido ABERTO — faça login no portal da Caixa "
                        "e finalize a compra manualmente."
                    ),
                }, ensure_ascii=False))
                _aguardar(args)
                return 1
            # Sucesso: mantém o navegador ABERTO para o usuário conferir/finalizar.
            print(json.dumps({
                "success": True,
                "loteria": args.loteria,
                "total_jogos": len(jogos_validos),
                "progresso": progresso,
                "navegador_aberto": True,
                "mensagem": (
                    f"{len(jogos_validos)} jogo(s) preenchido(s). "
                    "Navegador mantido ABERTO — faça login e finalize a compra no site da Caixa."
                ),
            }, ensure_ascii=False))
            if args.fechar_ao_final:
                auto.fechar()
            else:
                _aguardar(args)
            return 0
    except LoteriaNaoSuportadaError as e:
        return _saida(args.json, success=False, error=str(e))
    except SemJogosError as e:
        return _saida(args.json, success=False, error=str(e))
    except Exception as e:
        return _saida(args.json, success=False, error=f"Erro na automação: {e}")


def _saida(json_mode: bool, **kwargs) -> int:
    saida = {"success": kwargs.pop("success", True)}
    saida.update(kwargs)
    print(json.dumps(saida, ensure_ascii=False))
    return 0 if saida["success"] else 1


def _aguardar(args) -> None:
    """Mantém o processo vivo para o navegador (Selenium) não ser encerrado.

    Após preencher os volantes, o usuário precisa fazer login/finalizar no
    navegador aberto. Enquanto este processo rodar, o driver não fecha.
    Encerre o processo (Ctrl+C / fechar o terminal) quando terminar.
    """
    print(json.dumps({
        "status": "aguardando",
        "mensagem": "Aguardando você finalizar no navegador aberto (login + confirmação). Encerre o processo quando terminar.",
    }, ensure_ascii=False))
    try:
        while True:
            time.sleep(3600)
    except KeyboardInterrupt:
        return


if __name__ == "__main__":
    sys.exit(main())
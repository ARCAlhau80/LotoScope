import requests
import time
from typing import Optional, List, Dict, Tuple, Callable

from .config_base import LotteryConfig


class AtualizadorBase:
    def __init__(self, config: LotteryConfig, get_connection: Optional[Callable] = None):
        self.config = config
        self.api_url = f"https://servicebus2.caixa.gov.br/portaldeloterias/api/{config.id}/"
        self.max_retries = 3
        self.retry_delay = 2
        self._get_connection = get_connection

    def _obter_conexao(self):
        if self._get_connection:
            return self._get_connection()
        try:
            from lotofacil_lite.utils.database_config import db_config
            return db_config.get_connection()
        except ImportError:
            raise RuntimeError(
                "Nenhuma conexão configurada. Passe `get_connection` "
                "no construtor ou instale o módulo database_config."
            )

    # ─── hooks (override in subclass) ────────────────────────────

    def extra_campos_estatisticos(self, concurso: int, numeros: List[int], data_sorteio: str, dados_api: Optional[dict] = None) -> Dict:
        return {}

    def pos_upsert(self, concurso: int, numeros: List[int]) -> None:
        pass

    def pos_atualizacao(self, ultimo_concurso: int) -> None:
        pass

    # ─── Caixa API ──────────────────────────────────────────────

    def _api_request_with_retry(self, concurso: int) -> Optional[dict]:
        url = f"{self.api_url}{concurso}"
        for attempt in range(self.max_retries):
            try:
                print(f"🌐 Buscando concurso {concurso} ({self.config.nome_jogo}, tentativa {attempt + 1})")
                resp = requests.get(url, timeout=30)
                if resp.status_code == 200:
                    print(f"✅ Concurso {concurso} obtido")
                    return resp.json()
                elif resp.status_code in (502, 503, 504):
                    print(f"⚠️ Erro temporário: {resp.status_code}")
                    if attempt < self.max_retries - 1:
                        time.sleep(self.retry_delay)
                    continue
                else:
                    print(f"❌ Erro API: {resp.status_code}")
                    return None
            except requests.exceptions.RequestException as e:
                print(f"❌ Erro conexão: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
        print(f"❌ Falha concurso {concurso} após {self.max_retries} tentativas")
        return None

    def obter_ultimo_concurso_api(self) -> Optional[int]:
        try:
            resp = requests.get(self.api_url, timeout=30)
            if resp.status_code == 200:
                data = resp.json()
                if data and 'numero' in data:
                    return int(data['numero'])
            else:
                print(f"❌ Erro ao obter último concurso: {resp.status_code}")
        except Exception as e:
            print(f"❌ Erro ao consultar API: {e}")
        return None

    # ─── SQL helpers ────────────────────────────────────────────

    def _colunas_n(self) -> List[str]:
        return self.config.colunas_resultado

    def _colunas_s(self) -> List[str]:
        return [f"S{i}" for i in range(1, self.config.numeros_por_jogo + 1)]

    def _sql_upsert(self, extra_cols: List[str] = None) -> Tuple[str, str]:
        n_cols = self._colunas_n()
        cols = ["Concurso", "Data_Sorteio"] + n_cols + (extra_cols or [])
        placeholders = ", ".join(["?" for _ in cols])
        set_clause = ", ".join([f"{c} = ?" for c in cols if c != "Concurso"])
        col_names = ", ".join(cols)
        table = self.config.tabela_resultados
        sql_upd = f"UPDATE {table} SET {set_clause} WHERE Concurso = ?"
        sql_ins = f"INSERT INTO {table} ({col_names}) VALUES ({placeholders})"
        return sql_upd, sql_ins

    # ─── core update ────────────────────────────────────────────

    def atualizar_concurso_individual(self, concurso: int) -> bool:
        print(f"\n📊 [{self.config.nome_jogo}] Atualizando concurso {concurso}...")
        data = self._api_request_with_retry(concurso)
        if not data:
            return False

        try:
            dezenas = data.get("listaDezenas", [])
            numeros = [int(n) for n in dezenas]
            if len(numeros) != self.config.numeros_por_jogo:
                print(f"❌ Dados inválidos: {len(numeros)} números (esperado {self.config.numeros_por_jogo})")
                return False

            data_sorteio = data.get("dataApuracao", "")

            ordem = data.get("dezenasSorteadasOrdemSorteio", [])
            ordem_nums = [int(n) for n in ordem] if ordem and len(ordem) == self.config.numeros_por_jogo else []

            extras = self.extra_campos_estatisticos(concurso, numeros, data_sorteio, data)
            extra_col_names = list(extras.keys())

            sql_upd, sql_ins = self._sql_upsert(extra_col_names)

            # UPDATE params: [Data_Sorteio, N1..Nn, extras..., Concurso]
            upd_vals = [data_sorteio]
            upd_vals.extend(numeros)
            upd_vals.extend(extras.values())
            upd_vals.append(concurso)

            # INSERT params: [Concurso, Data_Sorteio, N1..Nn, extras...]
            ins_vals = [concurso, data_sorteio]
            ins_vals.extend(numeros)
            ins_vals.extend(extras.values())

            conn = self._obter_conexao()
            try:
                cursor = conn.cursor()
                affected = cursor.execute(sql_upd, upd_vals).rowcount
                if affected == 0:
                    cursor.execute(sql_ins, ins_vals)
                conn.commit()
            finally:
                cursor.close()
                conn.close()

            print(f"✅ [{self.config.nome_jogo}] Concurso {concurso} atualizado")
            self.pos_upsert(concurso, numeros)
            return True

        except Exception as e:
            print(f"❌ Erro concurso {concurso}: {e}")
            return False

    def atualizar_range_concursos(self, inicio: int, fim: int) -> Tuple[int, int]:
        sucesso = 0
        falha = 0
        for c in range(inicio, fim + 1):
            if self.atualizar_concurso_individual(c):
                sucesso += 1
            else:
                falha += 1
            time.sleep(1)
        print(f"\n📊 Range {inicio}-{fim}: {sucesso} ok, {falha} falha")
        return sucesso, falha

    def atualizar_completo(self, qtde_por_vez: int = 5) -> int:
        try:
            conn = self._obter_conexao()
            try:
                cursor = conn.cursor()
                cursor.execute(f"SELECT MAX(Concurso) FROM {self.config.tabela_resultados}")
                row = cursor.fetchone()
                ultimo_db = row[0] if row and row[0] else 0
            finally:
                cursor.close()
                conn.close()
        except Exception:
            ultimo_db = 0

        ultimo_api = self.obter_ultimo_concurso_api()
        if not ultimo_api:
            print("❌ Não foi possível obter último concurso da API")
            return 0

        if ultimo_db >= ultimo_api:
            print(f"✅ [{self.config.nome_jogo}] Já atualizado (DB: {ultimo_db}, API: {ultimo_api})")
            return 0

        pendentes = list(range(ultimo_db + 1, ultimo_api + 1))
        print(f"🔄 [{self.config.nome_jogo}] {len(pendentes)} concursos pendentes ({ultimo_db} → {ultimo_api})")

        total_ok = 0
        for i in range(0, len(pendentes), qtde_por_vez):
            bloco = pendentes[i:i + qtde_por_vez]
            for c in bloco:
                if self.atualizar_concurso_individual(c):
                    total_ok += 1
                time.sleep(0.5)

        if total_ok > 0:
            self.pos_atualizacao(ultimo_api)

        print(f"✅ [{self.config.nome_jogo}] Atualização completa: {total_ok} concursos")
        return total_ok

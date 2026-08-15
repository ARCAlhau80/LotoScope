from typing import List, Dict, Optional
from .atualizador_base import AtualizadorBase
from .config_base import LotteryRegistry


class AtualizadorLotofacil(AtualizadorBase):
    def __init__(self, get_connection=None):
        config = LotteryRegistry.get("lotofacil")
        if not config:
            raise ValueError("Lotofácil não registrada no registry")
        super().__init__(config, get_connection)
        self.primos = {2, 3, 5, 7, 11, 13, 17, 19, 23}
        self.fibonacci = {1, 2, 3, 5, 8, 13, 21}

    def _obter_concurso_anterior(self, concurso: int) -> Optional[Dict]:
        try:
            conn = self._obter_conexao()
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT N1,N2,N3,N4,N5,N6,N7,N8,N9,N10,N11,N12,N13,N14,N15
                    FROM Resultados_INT WHERE Concurso = ?
                """, (concurso - 1,))
                row = cursor.fetchone()
                if row:
                    return dict(zip([f"N{i}" for i in range(1, 16)], row))
                return None
            finally:
                cursor.close()
                conn.close()
        except Exception as e:
            print(f"⚠️ Erro ao buscar concurso anterior {concurso-1}: {e}")
            return None

    def extra_campos_estatisticos(self, concurso: int, numeros: List[int], data_sorteio: str, dados_api: Optional[dict] = None) -> Dict:
        nums = sorted(numeros)
        pares = [n for n in nums if n % 2 == 0]

        qtde_impares = sum(1 for n in nums if n % 2 == 1)
        soma_total = sum(nums)
        consecutivos = sum(1 for i in range(len(nums) - 1) if nums[i+1] - nums[i] == 1)
        amplitude = max(nums) - min(nums)
        qtde_mult3 = sum(1 for n in nums if n % 3 == 0)

        qtde_gaps = sum(1 for i in range(len(nums) - 1) if nums[i+1] - nums[i] > 1)

        pares_sequencia = sum(1 for i in range(len(pares) - 1) if pares[i+1] - pares[i] == 2)
        pares_saltados = sum(1 for i in range(len(pares) - 1) if pares[i+1] - pares[i] == 4)

        campos = {
            "QtdePrimos": sum(1 for n in nums if n in self.primos),
            "QtdeFibonacci": sum(1 for n in nums if n in self.fibonacci),
            "QtdeImpares": qtde_impares,
            "SomaTotal": soma_total,
            "Quintil1": sum(1 for n in nums if 1 <= n <= 5),
            "Quintil2": sum(1 for n in nums if 6 <= n <= 10),
            "Quintil3": sum(1 for n in nums if 11 <= n <= 15),
            "Quintil4": sum(1 for n in nums if 16 <= n <= 20),
            "Quintil5": sum(1 for n in nums if 21 <= n <= 25),
            "QtdeGaps": qtde_gaps,
            "SEQ": float(consecutivos),
            "DistanciaExtremos": amplitude,
            "ParesSequencia": pares_sequencia,
            "QtdeMultiplos3": qtde_mult3,
            "ParesSaltados": pares_saltados,
            "Faixa_Baixa": sum(1 for n in nums if 1 <= n <= 8),
            "Faixa_Media": sum(1 for n in nums if 9 <= n <= 17),
            "Faixa_Alta": sum(1 for n in nums if 18 <= n <= 25),
            "Acumulou": False,
        }

        ant = self._obter_concurso_anterior(concurso)
        if ant:
            ant_nums = [ant[f"N{i}"] for i in range(1, 16)]
            repetidos = len(set(nums) & set(ant_nums))
            campos["QtdeRepetidos"] = repetidos
            mesma = sum(1 for i in range(15) if numeros[i] == ant_nums[i])
            campos["RepetidosMesmaPosicao"] = mesma
        else:
            campos["QtdeRepetidos"] = 0
            campos["RepetidosMesmaPosicao"] = 0

        return campos

    def pos_atualizacao(self, ultimo_concurso: int) -> None:
        print(f"\n🔄 [{self.config.nome_jogo}] PROCEDURES PÓS-ATUALIZAÇÃO...")
        try:
            conn = self._obter_conexao()
            try:
                cursor = conn.cursor()
                procs = [
                    "PROC_ATUALIZAR_COMBIN_10",
                    "sp_AtualizarAcertos_LF15",
                    "AtualizaNumerosCiclos",
                    "PROC_ATUALIZAR_QUINA",
                    "SP_AtualizarCamposComparacao",
                    "SP_AtualizarCombinacoesComparacao",
                ]
                for proc in procs:
                    try:
                        print(f"   ▶ Executando {proc}...")
                        cursor.execute(f"EXEC {proc}")
                        conn.commit()
                        print(f"   ✅ {proc} OK")
                    except Exception as e:
                        print(f"   ⚠️ {proc}: {e}")
            finally:
                cursor.close()
                conn.close()
            print(f"✅ Procedures concluídas")
        except Exception as e:
            print(f"❌ Erro procedures: {e}")

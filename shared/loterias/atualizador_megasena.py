from .atualizador_base import AtualizadorBase
from .config_base import LotteryRegistry


class AtualizadorMegaSena(AtualizadorBase):
    def __init__(self, get_connection=None):
        config = LotteryRegistry.get("megasena")
        if not config:
            raise ValueError("Mega-Sena não registrada no registry")
        super().__init__(config, get_connection)

    def pos_atualizacao(self, ultimo_concurso: int) -> None:
        print(f"\n🔄 [{self.config.nome_jogo}] PROCEDURES PÓS-ATUALIZAÇÃO...")
        try:
            conn = self._obter_conexao()
            try:
                cursor = conn.cursor()
                proc = "AtualizaNumerosCiclosMega"
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

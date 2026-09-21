import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


class FakeDriver:
    """Driver fake com memória de interações para testar a automação."""

    def __init__(self):
        self.current_url = ""
        self.clicked = []
        self.visited = []
        self.by = {}
        self.scrolled = []

    def get(self, url):
        self.visited.append(url)
        self.current_url = url

    def find_element(self, by, value):
        return self.by.get((by, value))

    def execute_script(self, script, arg=None):
        if arg is not None:
            self.scrolled.append(getattr(arg, "id_", None))
        return None

    def quit(self):
        self.quit_called = True


class FakeElement:
    def __init__(self, id_, driver):
        self.id_ = id_
        self.driver = driver
        self._text = None
        self._displayed = True

    def click(self):
        self.driver.clicked.append(self.id_)

    def scroll_into_view(self):
        self.driver.scrolled.append(self.id_)

    def is_displayed(self):
        return self._displayed

    @property
    def text(self):
        return self._text if self._text is not None else self.id_


class TestAutomacaoCaixa:
    def test_abrir_portal(self):
        from shared.apostador.automacao import AutomacaoCaixa
        driver = FakeDriver()
        auto = AutomacaoCaixa(driver)
        auto.abrir_portal()
        assert "loteriasonline.caixa.gov.br" in driver.visited[0]

    def test_navegar_para_loteria_lotofacil(self):
        from shared.apostador.automacao import AutomacaoCaixa
        driver = FakeDriver()
        auto = AutomacaoCaixa(driver)
        auto.navegar_para_loteria("lotofacil")
        assert "#/lotofacil" in driver.visited[-1]

    def test_navegar_para_loteria_duplasena(self):
        from shared.apostador.automacao import AutomacaoCaixa
        driver = FakeDriver()
        auto = AutomacaoCaixa(driver)
        auto.navegar_para_loteria("duplasena")
        assert "#/dupla-sena" in driver.visited[-1]

    def test_preencher_volante_seleciona_cada_numero(self):
        from shared.apostador.automacao import AutomacaoCaixa
        driver = FakeDriver()
        for i in range(1, 26):
            driver.by[("id", f"n{i:02d}")] = FakeElement(f"n{i:02d}", driver)
        auto = AutomacaoCaixa(driver)
        auto.preencher_volante("lotofacil", [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15])
        assert driver.clicked == [f"n{i:02d}" for i in range(1, 16)]

    def test_preencher_volante_respeita_id_com_zero(self):
        from shared.apostador.automacao import AutomacaoCaixa
        driver = FakeDriver()
        for i in range(1, 10):
            driver.by[("id", f"n0{i}")] = FakeElement(f"n0{i}", driver)
        auto = AutomacaoCaixa(driver)
        auto.preencher_volante("lotofacil", [5])
        assert driver.clicked == ["n05"]

    def test_adicionar_ao_carrinho(self):
        from shared.apostador.automacao import AutomacaoCaixa
        driver = FakeDriver()
        driver.by[("id", "colocarnocarrinho")] = FakeElement("colocarnocarrinho", driver)
        auto = AutomacaoCaixa(driver)
        auto.adicionar_ao_carrinho("lotofacil")
        assert driver.clicked == ["colocarnocarrinho"]

    def test_limpar_volante(self):
        from shared.apostador.automacao import AutomacaoCaixa
        driver = FakeDriver()
        driver.by[("id", "limparvolante")] = FakeElement("limparvolante", driver)
        auto = AutomacaoCaixa(driver)
        auto.limpar_volante("lotofacil")
        assert driver.clicked == ["limparvolante"]

    def test_realizar_apostas_itera_jogos_e_reporta_progresso(self):
        from shared.apostador.automacao import AutomacaoCaixa
        driver = FakeDriver()
        for i in range(1, 26):
            driver.by[("id", f"n{i:02d}")] = FakeElement(f"n{i:02d}", driver)
        driver.by[("id", "limparvolante")] = FakeElement("limparvolante", driver)
        driver.by[("id", "colocarnocarrinho")] = FakeElement("colocarnocarrinho", driver)

        jogos = [list(range(1, 16)), list(range(2, 17))]
        progresso = []
        auto = AutomacaoCaixa(driver)
        auto.realizar_apostas("lotofacil", jogos, progresso_callback=lambda p: progresso.append(p))

        assert progresso == [{"jogo": 1, "total": 2, "status": "preenchido"}, {"jogo": 2, "total": 2, "status": "preenchido"}]
        assert "colocarnocarrinho" in driver.clicked
        assert driver.clicked.count("limparvolante") == 2

    def test_realizar_apostas_sem_jogos_lanca_erro(self):
        from shared.apostador.automacao import AutomacaoCaixa, SemJogosError
        auto = AutomacaoCaixa(FakeDriver())
        with pytest.raises(SemJogosError):
            auto.realizar_apostas("lotofacil", [])

    def test_selector_numero_loteria(self):
        from shared.apostador.automacao import AutomacaoCaixa
        assert AutomacaoCaixa._id_numero("lotofacil", 1) == "n01"
        assert AutomacaoCaixa._id_numero("lotofacil", 25) == "n25"

    def test_selector_carrinho_loteria(self):
        from shared.apostador.automacao import AutomacaoCaixa
        assert AutomacaoCaixa._id_carrinho("lotofacil") == "colocarnocarrinho"

    def test_url_loteria_desconhecida_lanca_erro(self):
        from shared.apostador.automacao import AutomacaoCaixa, LoteriaNaoSuportadaError
        auto = AutomacaoCaixa(FakeDriver())
        with pytest.raises(LoteriaNaoSuportadaError):
            auto.navegar_para_loteria("loteria_fantasma")

    def test_rota_lotofacil_usa_especial(self):
        from shared.apostador.automacao import AutomacaoCaixa, PORTAL_URL
        driver = FakeDriver()
        auto = AutomacaoCaixa(driver)
        auto.navegar_para_loteria("lotofacil")
        assert driver.visited[-1] == PORTAL_URL.split("#/")[0] + "#/lotofacil/especial"

    def test_resolver_age_gate_clica_sim(self):
        from shared.apostador.automacao import AutomacaoCaixa
        driver = FakeDriver()
        driver.by[("id", "botaosim")] = FakeElement("botaosim", driver)
        auto = AutomacaoCaixa(driver)
        auto.resolver_age_gate()
        assert driver.clicked == ["botaosim"]

    def test_resolver_age_gate_sem_botao_nao_quebra(self):
        from shared.apostador.automacao import AutomacaoCaixa
        driver = FakeDriver()
        auto = AutomacaoCaixa(driver)
        auto.resolver_age_gate()
        assert driver.clicked == []

    def test_navegar_renavega_apos_age_gate(self):
        from shared.apostador.automacao import AutomacaoCaixa, PORTAL_BASE
        driver = FakeDriver()
        driver.by[("id", "botaosim")] = FakeElement("botaosim", driver)
        auto = AutomacaoCaixa(driver)
        auto.navegar_para_loteria("lotofacil")
        assert driver.visited.count(PORTAL_BASE + "#/lotofacil/especial") == 2

    def test_preencher_volante_espera_por_elemento(self):
        from shared.apostador.automacao import AutomacaoCaixa
        driver = FakeDriver()
        driver.by[("id", "n01")] = FakeElement("n01", driver)
        auto = AutomacaoCaixa(driver)
        auto.preencher_volante("lotofacil", [1])
        assert driver.clicked == ["n01"]

    def test_preencher_volante_rola_ate_elemento(self):
        from shared.apostador.automacao import AutomacaoCaixa
        driver = FakeDriver()
        driver.by[("id", "n01")] = FakeElement("n01", driver)
        auto = AutomacaoCaixa(driver)
        auto.preencher_volante("lotofacil", [1])
        assert "n01" in driver.scrolled

    def test_fechar_alertas_clica_fechar(self):
        from shared.apostador.automacao import AutomacaoCaixa
        driver = FakeDriver()
        fechar = FakeElement("close_btn", driver)
        fechar.is_displayed = lambda: True
        driver.find_elements = lambda by, value: [fechar] if value == ".alert .close" else []
        auto = AutomacaoCaixa(driver)
        auto.fechar_alertas()
        assert "close_btn" in driver.clicked

    def test_fechar_alertas_sem_alerta_nao_quebra(self):
        from shared.apostador.automacao import AutomacaoCaixa
        driver = FakeDriver()
        driver.find_elements = lambda by, value: []
        auto = AutomacaoCaixa(driver)
        auto.fechar_alertas()
        assert driver.clicked == []

    def test_nao_fecha_navegador_apos_preencher(self):
        from shared.apostador.automacao import AutomacaoCaixa
        driver = FakeDriver()
        for i in range(1, 26):
            driver.by[("id", f"n{i:02d}")] = FakeElement(f"n{i:02d}", driver)
        driver.by[("id", "colocarnocarrinho")] = FakeElement("colocarnocarrinho", driver)
        driver.by[("id", "limparvolante")] = FakeElement("limparvolante", driver)
        auto = AutomacaoCaixa(driver)
        auto.realizar_apostas("lotofacil", [list(range(1, 16))])
        assert not getattr(driver, "quit_called", False)

    def test_adicionar_ao_carrinho_nao_interage_com_login(self):
        from shared.apostador.automacao import AutomacaoCaixa
        driver = FakeDriver()
        # Sem carrinho disponível (não logado) e sem login a clicar
        auto = AutomacaoCaixa(driver)
        try:
            auto.adicionar_ao_carrinho("lotofacil")
        except Exception:
            pass
        # Nenhum clique em elementos de login
        assert "botaosim" not in driver.clicked
        assert driver.clicked == []


class TestAjustarQtdDezenas:
    def _setup_volante(self, valor_atual, driver):
        valor = FakeElement("valor_atual", driver)
        valor._text = str(valor_atual)
        driver.by[("css selector", ".input-mais-menos > span")] = valor
        mais = FakeElement("aumentarnumero", driver)
        menos = FakeElement("diminuirnumero", driver)
        driver.by[("id", "aumentarnumero")] = mais
        driver.by[("id", "diminuirnumero")] = menos
        return mais, menos

    def test_nao_clica_quando_qtd_ja_igual(self):
        from shared.apostador.automacao import AutomacaoCaixa
        driver = FakeDriver()
        self._setup_volante(15, driver)
        auto = AutomacaoCaixa(driver)
        auto.ajustar_qtd_dezenas("lotofacil", 15)
        assert driver.clicked == []

    def test_aumenta_ate_a_qtd_desejada(self):
        from shared.apostador.automacao import AutomacaoCaixa
        driver = FakeDriver()
        mais, menos = self._setup_volante(15, driver)
        # Simula que cada clique no + incrementa o valor
        def fake_click():
            driver.clicked.append(mais.id_)
            valor = driver.by[("css selector", ".input-mais-menos > span")]
            valor._text = str(int(valor._text) + 1)
        mais.click = fake_click
        auto = AutomacaoCaixa(driver)
        auto.ajustar_qtd_dezenas("lotofacil", 17)
        assert driver.clicked == ["aumentarnumero", "aumentarnumero"]

    def test_diminui_ate_a_qtd_desejada(self):
        from shared.apostador.automacao import AutomacaoCaixa
        driver = FakeDriver()
        mais, menos = self._setup_volante(20, driver)
        def fake_click():
            driver.clicked.append(menos.id_)
            valor = driver.by[("css selector", ".input-mais-menos > span")]
            valor._text = str(int(valor._text) - 1)
        menos.click = fake_click
        auto = AutomacaoCaixa(driver)
        auto.ajustar_qtd_dezenas("lotofacil", 18)
        assert driver.clicked == ["diminuirnumero", "diminuirnumero"]

    def test_preencher_volante_ajusta_qtd_antes_de_clicar(self):
        from shared.apostador.automacao import AutomacaoCaixa
        driver = FakeDriver()
        mais, menos = self._setup_volante(15, driver)
        def fake_click():
            driver.clicked.append(mais.id_)
            valor = driver.by[("css selector", ".input-mais-menos > span")]
            valor._text = str(int(valor._text) + 1)
        mais.click = fake_click
        for i in range(1, 18):
            driver.by[("id", f"n{i:02d}")] = FakeElement(f"n{i:02d}", driver)
        auto = AutomacaoCaixa(driver)
        auto.preencher_volante("lotofacil", list(range(1, 17)))
        assert driver.clicked.count("aumentarnumero") == 1
        assert "n01" in driver.clicked and "n16" in driver.clicked


class TestModoAttach:
    def test_criar_driver_attach_usa_debugger_address(self):
        from shared.apostador.automacao import criar_driver_attach
        import types
        capturado = {}

        def fake_chrome(**kwargs):
            capturado["kwargs"] = kwargs
            return "FAKE_DRIVER"

        fake_cls = types.SimpleNamespace(Chrome=fake_chrome)
        driver = criar_driver_attach(porta=9222, _chrome_cls=fake_cls.Chrome, _opts_cls=None)
        assert driver == "FAKE_DRIVER"

    def test_criar_driver_attach_configura_debugger_address(self):
        from shared.apostador.automacao import criar_driver_attach
        import types

        chamadas = {}

        class FakeOpts:
            def __init__(self):
                self.exp = []
                self.args = []

            def add_experimental_option(self, k, v):
                self.exp.append((k, v))

            def add_argument(self, a):
                self.args.append(a)

        def fake_chrome(options=None, **kwargs):
            chamadas["options"] = options
            return "FAKE_DRIVER"

        fake_cls = types.SimpleNamespace(Chrome=fake_chrome)
        criar_driver_attach(porta=9222, _chrome_cls=fake_cls.Chrome, _opts_cls=FakeOpts)
        opts = chamadas["options"]
        assert ("debuggerAddress", "127.0.0.1:9222") in opts.exp

    def test_criar_driver_novo_usa_user_data_dir(self):
        from shared.apostador.automacao import criar_driver_novo
        import types

        chamadas = {}

        class FakeOpts:
            def __init__(self):
                self.args = []

            def add_argument(self, a):
                self.args.append(a)

        def fake_chrome(options=None, **kwargs):
            chamadas["options"] = options
            return "FAKE_DRIVER"

        fake_cls = types.SimpleNamespace(Chrome=fake_chrome)
        criar_driver_novo(user_data_dir=r"C:\temp\perfil", _chrome_cls=fake_cls.Chrome, _opts_cls=FakeOpts, headless=False)
        opts = chamadas["options"]
        assert any("user-data-dir=C:\\temp\\perfil" in a for a in opts.args)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
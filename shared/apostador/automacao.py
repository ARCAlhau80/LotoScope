"""Automação de preenchimento de volantes no Portal Loterias CAIXA.

Fluxo: abrir o portal, navegar para a loteria (resolvendo age-gate e cookies),
e para cada jogo preencher os números no volante e adicionar ao carrinho —
PARANDO antes do pagamento e mantendo o navegador ABERTO para o usuário
conferir e finalizar a compra.

Requisitos:
- Usar um perfil Chrome persistente (user-data-dir) para manter a sessão
  logada do usuário. Sem login, o portal redireciona para a página de acesso.
- Rodar com JANELA VISÍVEL (o anti-bot ShieldSquare da Caixa bloqueia headless).
- O driver (Selenium) é injetável para permitir testes com driver fake.
"""

from typing import Any, Callable, Dict, List, Optional

PORTAL_URL = "https://www.loteriasonline.caixa.gov.br/silce-web/#/home"
PORTAL_BASE = PORTAL_URL.split("#/")[0]

# Mapeamento id da loteria -> rota do volante no SPA do portal.
# Observado no site real (2026-09): Lotofácil usa /especial (concurso da Independência);
# as demais usam a rota direta da modalidade.
LOTERIAS_ROTA: Dict[str, str] = {
    "lotofacil": "lotofacil/especial",
    "megasena": "mega-sena",
    "quina": "quina",
    "duplasena": "dupla-sena",
    "lotomania": "lotomania",
    "timemania": "timemania",
    "diadesorte": "dia-de-sorte",
    "supersete": "super-sete",
    "maismilionaria": "mais-milionaria",
}

DEFAULT_TIMEOUT = 30.0


class LoteriaNaoSuportadaError(Exception):
    """Loteria sem rota mapeada no portal."""


class SemJogosError(Exception):
    """Nenhum jogo fornecido para aposta."""


def _criar_driver(attach_porta: Optional[int] = None, user_data_dir: Optional[str] = None,
                  headless: bool = False, _chrome_cls=None, _opts_cls=None):
    """Cria um driver Selenium, anexando a um Chrome já aberto ou abrindo um novo.

    attach_porta: se informado, conecta via CDP a um Chrome já aberto
                  (iniciado com --remote-debugging-port=<porta>), reutilizando
                  a sessão logada e NÃO fechando o navegador do usuário.
    user_data_dir: perfil persistente para abrir uma nova instância.
    """
    if _opts_cls is None:
        from selenium.webdriver.chrome.options import Options as ChromeOptions
        _opts_cls = ChromeOptions
    if _chrome_cls is None:
        from selenium import webdriver
        _chrome_cls = webdriver.Chrome

    if attach_porta:
        options = _opts_cls()
        options.add_experimental_option("debuggerAddress", f"127.0.0.1:{attach_porta}")
        return _chrome_cls(options=options)

    options = _opts_cls()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    if user_data_dir:
        from pathlib import Path
        Path(user_data_dir).mkdir(parents=True, exist_ok=True)
        options.add_argument(f"--user-data-dir={user_data_dir}")
    return _chrome_cls(options=options)


def criar_driver_attach(porta: int, _chrome_cls=None, _opts_cls=None):
    """Conecta a um Chrome já aberto/logado via CDP (remote-debugging-port)."""
    return _criar_driver(attach_porta=porta, _chrome_cls=_chrome_cls, _opts_cls=_opts_cls)


def criar_driver_novo(user_data_dir: Optional[str] = None, headless: bool = False,
                      _chrome_cls=None, _opts_cls=None):
    """Abre uma nova instância do Chrome (com perfil persistente opcional)."""
    return _criar_driver(user_data_dir=user_data_dir, headless=headless,
                         _chrome_cls=_chrome_cls, _opts_cls=_opts_cls)


class AutomacaoCaixa:
    def __init__(self, driver: Any, timeout: float = DEFAULT_TIMEOUT):
        """driver: objeto com get(), find_element(by, value), quit() (ex.: selenium WebDriver)."""
        self.driver = driver
        self.timeout = timeout

    def abrir_portal(self) -> None:
        self.driver.get(PORTAL_URL)

    def navegar_para_loteria(self, loteria: str) -> None:
        rota = LOTERIAS_ROTA.get(loteria)
        if not rota:
            raise LoteriaNaoSuportadaError(f"Loteria não suportada: {loteria}")
        url = PORTAL_BASE + f"#/{rota}"
        self.driver.get(url)
        if self.resolver_age_gate():
            # O portal redireciona para a home após confirmar a idade;
            # é preciso navegar novamente para a loteria.
            self.driver.get(url)
        self.resolver_cookies()

    def resolver_age_gate(self) -> bool:
        """Clica em 'Sim' na tela de maior de 18 anos, se presente.

        Retorna True se o botão existia e foi clicado (portanto houve redirect).
        """
        try:
            el = self.driver.find_element("id", "botaosim")
            el.click()
            return True
        except Exception:
            return False

    def resolver_cookies(self) -> None:
        """Aceita o aviso de cookies, se presente."""
        try:
            from selenium.webdriver.common.by import By
            for candidato in ("Aceitar", "Aceito"):
                try:
                    el = self.driver.find_element(By.XPATH, f"//button[normalize-space()='{candidato}']")
                    el.click()
                    return
                except Exception:
                    continue
        except Exception:
            pass

    def fechar_alertas(self) -> None:
        """Fecha banners de alerta que sobrepõem o volante (#mensagem_alert e .alert)."""
        try:
            from selenium.webdriver.common.by import By
            for seletor in ("#mensagem_alert", ".alert .close", ".alert button.close"):
                try:
                    els = self.driver.find_elements(By.CSS_SELECTOR, seletor)
                    for el in els:
                        try:
                            if el.is_displayed():
                                el.click()
                        except Exception:
                            pass
                except Exception:
                    continue
        except Exception:
            pass

    def _esperar_elemento(self, by: str, value: str) -> Any:
        """Aguarda o elemento existir no DOM (SPA carrega dinamicamente).

        Tenta localizar diretamente primeiro (rápido p/ drivers fake/testes);
        se não encontrar e for um driver Selenium real (tem session_id),
        usa WebDriverWait como fallback.
        """
        try:
            el = self.driver.find_element(by, value)
            if el is not None:
                return el
        except Exception:
            pass
        if not hasattr(self.driver, "session_id"):
            return None
        try:
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC

            return WebDriverWait(self.driver, self.timeout).until(
                EC.presence_of_element_located((by, value))
            )
        except Exception:
            pass
        return self.driver.find_element(by, value)

    def _rolar_ate_elemento(self, el: Any) -> None:
        """Rola até o elemento e espera ficar clicável (evita 'element click intercepted')."""
        try:
            el.scroll_into_view()
        except Exception:
            pass
        try:
            self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
        except Exception:
            pass
        try:
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC

            WebDriverWait(self.driver, self.timeout).until(EC.element_to_be_clickable(el))
        except Exception:
            pass

    @staticmethod
    def _id_numero(loteria: str, numero: int) -> str:
        return f"n{numero:02d}"

    @staticmethod
    def _id_carrinho(loteria: str) -> str:
        return "colocarnocarrinho"

    @staticmethod
    def _id_limpar(loteria: str) -> str:
        return "limparvolante"

    @staticmethod
    def _id_aumentar(loteria: str) -> str:
        return "aumentarnumero"

    @staticmethod
    def _id_diminuir(loteria: str) -> str:
        return "diminuirnumero"

    def _ler_qtd_dezenas(self) -> Optional[int]:
        """Lê a quantidade de dezenas ativa do volante (span dentro de .input-mais-menos)."""
        try:
            from selenium.webdriver.common.by import By
            el = self._esperar_elemento(By.CSS_SELECTOR, ".input-mais-menos > span")
            return int(el.text.strip())
        except Exception:
            return None

    def ajustar_qtd_dezenas(self, loteria: str, quantidade: int) -> None:
        """Ajusta o seletor de quantidade de dezenas do volante até o desejado."""
        from selenium.webdriver.common.by import By

        atual = self._ler_qtd_dezenas()
        if atual is None or atual == quantidade:
            return
        if quantidade > atual:
            el = self._esperar_elemento(By.ID, self._id_aumentar(loteria))
            for _ in range(quantidade - atual):
                el.click()
                novo = self._ler_qtd_dezenas()
                if novo is None or novo <= atual:
                    break
                atual = novo
        else:
            el = self._esperar_elemento(By.ID, self._id_diminuir(loteria))
            for _ in range(atual - quantidade):
                el.click()
                novo = self._ler_qtd_dezenas()
                if novo is None or novo >= atual:
                    break
                atual = novo

    def preencher_volante(self, loteria: str, numeros: List[int]) -> None:
        from selenium.webdriver.common.by import By

        self.fechar_alertas()
        self.ajustar_qtd_dezenas(loteria, len(numeros))
        for num in numeros:
            el = self._esperar_elemento(By.ID, self._id_numero(loteria, num))
            self._rolar_ate_elemento(el)
            el.click()

    def adicionar_ao_carrinho(self, loteria: str) -> None:
        from selenium.webdriver.common.by import By

        el = self._esperar_elemento(By.ID, self._id_carrinho(loteria))
        self._rolar_ate_elemento(el)
        el.click()

    def limpar_volante(self, loteria: str) -> None:
        from selenium.webdriver.common.by import By

        el = self._esperar_elemento(By.ID, self._id_limpar(loteria))
        self._rolar_ate_elemento(el)
        el.click()

    def realizar_apostas(
        self,
        loteria: str,
        jogos: List[List[int]],
        progresso_callback: Optional[Callable[[Dict], None]] = None,
        apagar_antes_de_cada_jogo: bool = True,
    ) -> None:
        """Preenche cada jogo no volante e adiciona ao carrinho.

        Para ANTES do pagamento/conferência e mantém o navegador ABERTO para o
        usuário conferir e finalizar. Exige sessão logada no perfil do Chrome.
        """
        if not jogos:
            raise SemJogosError("Nenhum jogo fornecido para aposta")

        self.navegar_para_loteria(loteria)
        for idx, jogo in enumerate(jogos, start=1):
            if apagar_antes_de_cada_jogo:
                try:
                    self.limpar_volante(loteria)
                except Exception:
                    pass
            self.preencher_volante(loteria, jogo)
            self.adicionar_ao_carrinho(loteria)
            if progresso_callback:
                progresso_callback({"jogo": idx, "total": len(jogos), "status": "preenchido"})

    def fechar(self) -> None:
        """Fecha o navegador. Use apenas para abortar/limpar, não após sucesso."""
        try:
            self.driver.quit()
        except Exception:
            pass
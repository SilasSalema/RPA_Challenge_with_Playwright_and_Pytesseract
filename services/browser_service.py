import os
import time
import ctypes
from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page
from urllib3.exceptions import ProtocolError


class BrowserService:

    def __init__(self) -> None:
        self.playwright = None
        self.browser: Browser = None
        self.context: BrowserContext = None
        self.page: Page = None

    # =========================
    # CONFIGURAÇÕES
    # =========================

    def _get_environment(self):
        return os.getenv("Environment") or "local"

    def _get_browser(self):
        return os.getenv("Browser") or "chrome"

    def _start_playwright(self):
        if not self.playwright:
            self.playwright = sync_playwright().start()

    # =========================
    # LANÇAMENTO DO BROWSER
    # =========================

    def _launch_browser(self):

        self._start_playwright()

        browser_type = self._get_browser()
        environment = self._get_environment()

        if browser_type == "firefox":
            browser_launcher = self.playwright.firefox
        else:
            browser_launcher = self.playwright.chromium

        # =========================
        # LOCAL (JANELA VISÍVEL)
        # =========================
        if environment == "local":
            user32 = ctypes.windll.user32
            user32.SetProcessDPIAware()

            screen_width = user32.GetSystemMetrics(0)
            screen_height = user32.GetSystemMetrics(1)

            self.browser = browser_launcher.launch(headless=False)

            # viewport inicial padrão
            self.context = self.browser.new_context(
                accept_downloads=True,
                locale="pt-BR",
                viewport={"width": screen_width, "height": screen_height},
            )

        # =========================
        # DOCKER / HEADLESS
        # =========================
        else:

            self.browser = browser_launcher.launch(
                headless=True,
                args=[
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                ],
            )

            self.context = self.browser.new_context(
                accept_downloads=True,
                locale="en-US",
                viewport=None,
            )

        # =========================
        # BLOQUEAR IMAGENS (performance)
        # =========================
        self.context.route(
            "**/*",
            lambda route, request: (
                route.abort() if request.resource_type == "image" else route.continue_()
            ),
        )

    # =========================
    # MAXIMIZAÇÃO REAL WINDOWS
    # =========================

    def _maximizar_janela_windows(self):

        time.sleep(1)  # aguarda janela abrir

        user32 = ctypes.windll.user32
        SW_MAXIMIZE = 3

        hwnd = user32.GetForegroundWindow()

        if hwnd:
            user32.ShowWindow(hwnd, SW_MAXIMIZE)

    # =========================
    # CRIAR / OBTER ABA
    # =========================

    def _create_page(self):

        if self.context.pages:
            self.page = self.context.pages[0]
        else:
            self.page = self.context.new_page()

        self.page.set_default_navigation_timeout(120000)

        # 🔥 Maximizar somente no ambiente local
        if self._get_environment() == "local":
            self._maximizar_janela_windows()

    # =========================
    # RETRY COM BACKOFF
    # =========================

    def _launch_with_retry(self, max_retries=3, backoff_factor=1):

        for attempt in range(max_retries):
            try:
                self._launch_browser()
                self._create_page()
                return self.page
            except ProtocolError as e:
                print(f"Tentativa {attempt + 1} falhou: {e}")
                time.sleep(backoff_factor * (2**attempt))
            except Exception as e:
                print(f"Erro inesperado: {e}")
                break

        raise Exception("Falha ao iniciar navegador Playwright")

    # =========================
    # MÉTODOS PÚBLICOS
    # =========================

    def abrir_navegador(self) -> Page:
        return self._launch_with_retry()

    def abrir_nova_aba(self) -> Page:
        return self.context.new_page()

    def focar_na_aba(self, numero_aba: int) -> Page:
        return self.context.pages[numero_aba]

    def fechar_aba(self, page: Page) -> None:
        page.close()

    def fechar_navegador(self) -> None:
        if self.context:
            self.context.close()
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()

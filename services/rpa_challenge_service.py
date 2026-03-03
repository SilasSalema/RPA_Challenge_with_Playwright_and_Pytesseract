from concurrent.futures import *
from dotenv import load_dotenv

from services.browser_service import BrowserService
from helpers.criar_arquivo_log_helper import configurar_arquivo_log
from helpers.playwright_helper import *
from helpers.invoice_helper import *
from helpers.tratar_erro_helper import *


class RpaChallengeService(BrowserService):

    @tratar_erro
    def __init__(self) -> None:
        super().__init__()
        load_dotenv()
        self.logging = configurar_arquivo_log()
        self.logging.info("Iniciou Execução")

        try:
            self.execucao()
        finally:
            self.logging.info("Fechando a janela do navegador")
            self.fechar_navegador()

        self.logging.info("Terminou Execução")

    def execucao(self) -> None:
        self.logging.info("Abrindo janela do navegador")
        page = self.abrir_navegador()
        self.logging.info("Navegando para a página do RPA Challenge")
        navegar_site_rpa_challenge(page)
        self.logging.info("Obtendo o data frame da página web")
        data_frame_web = obter_tabela_web(page)
        lista_dados_extraidos = []
        for linha, _ in data_frame_web.iterrows():
            linha = linha + 1
            self.logging.info(f"Baixando o invoice da linha: {linha}")
            baixar_invoice(page, linha)
            self.logging.info(f"Extraindo os dados do invoice: {linha}")
            dados_extraidos = extrair_dados_invoice(f"invoice_{linha}.jpg")
            lista_dados_extraidos.append(dados_extraidos)
        data_frame_dados_extraidos = pd.DataFrame(lista_dados_extraidos)
        self.logging.info(
            "Exportando os dados obtidos de todas as invoices para o arquivo .csv"
        )
        data_frame_dados_extraidos.to_csv("dados_invoices.csv", sep=";", index=False)

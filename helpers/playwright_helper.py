import requests
import pandas as pd
from io import StringIO

from playwright.sync_api import Page
from helpers.tratar_erro_helper import *


def navegar_site_rpa_challenge(page: Page) -> None:
    page.goto("https://rpachallengeocr.azurewebsites.net/", timeout=60000)
    page.evaluate("document.body.style.zoom = '80%'")


def obter_tabela_web(page: Page) -> pd:
    html_tabela = page.locator(
        "//html/body/div/div/div[2]/div/div[1]/div[1]/table"
    ).inner_html()

    html_completo = f"<table>{html_tabela}</table>"
    df = pd.read_html(StringIO(html_completo))[0]

    return df


def baixar_invoice(page: Page, linha: int) -> None:
    with page.context.expect_page() as new_page_info:
        page.locator(
            f"//html/body/div/div/div[2]/div/div[1]/div[1]/table/tbody/tr[{linha}]/td[4]/a"
        ).click()

    nota_page = new_page_info.value
    nota_page.wait_for_load_state()

    print(nota_page.url)

    response = requests.get(nota_page.url)
    with open(f"invoice_{linha}.jpg", "wb") as f:
        f.write(response.content)

    nota_page.close()
    page.bring_to_front()

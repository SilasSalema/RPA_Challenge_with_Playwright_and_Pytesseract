import os
import time
import traceback
import pyautogui
from datetime import datetime


def tratar_erro(func):
    def interna(*args, **kwargs):
        args = list(args)
        try:
            resultado = func(*args, **kwargs)
        except Exception as exception_erro:
            try:
                capturar_screenshot_do_erro_web(args)
            except Exception as erro:
                tirar_print_do_desktop()

            tb = traceback.format_exc()
            mensagem_erro = f"{tb}"

            raise Exception(mensagem_erro)

        else:
            return resultado

    return interna


def capturar_screenshot_do_erro_web(args):
    caminho_arquivo_erro = os.getenv("Caminho_Evidencias")
    caminho_arquivo_erro = caminho_arquivo_erro.replace("'", "")
    if caminho_arquivo_erro:
        momento_arquivo_erro = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        img_erro = os.path.join(
            caminho_arquivo_erro,
            rf"exec_{momento_arquivo_erro}.png",
        )

        diretorio = caminho_arquivo_erro
        if not os.path.exists(diretorio):
            os.makedirs(diretorio)

        img_erro = img_erro.replace("'", "")
        try:
            driver = args[1]
            resultado = driver.save_screenshot(img_erro)
            if resultado:
                if not os.path.isfile(img_erro):
                    raise Exception(
                        f"Não foi possível encontrar o arquivo salvo do screenshot do navegador"
                    )
            else:
                raise Exception(f"Apresentou erro ao salvar o screenshot do navegador")
        except Exception as exception_etapa_screenshot:
            raise Exception(f"Apresentou o seguinte erro: {exception_etapa_screenshot}")
    else:
        raise Exception(
            "Apresentou erro para encontrar a variável de ambiente: caminho_evidencias"
        )


def tirar_print_do_desktop():
    caminho_arquivo_erro = os.getenv("caminho_evidencias")
    caminho_arquivo_erro = caminho_arquivo_erro.replace("'", "")

    momento_arquivo_erro = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    img_erro = os.path.join(
        caminho_arquivo_erro,
        rf"exec_{momento_arquivo_erro}.png",
    )

    diretorio = caminho_arquivo_erro
    if not os.path.exists(diretorio):
        os.makedirs(diretorio)

    screenshot = pyautogui.screenshot()

    screenshot.save(img_erro)

import logging
import os

from datetime import date

def configurar_arquivo_log() -> logging:
    data_hoje = date.today().strftime("%Y_%m_%d")
    try:
        os.makedirs(f"logs\\{data_hoje}")
    except:
        pass
    logging.basicConfig(
        format="%(asctime)s - %(levelname)s - %(message)s",
        filename=f"logs\\{data_hoje}\\execucao.log",
        encoding="utf-8",
        level=logging.INFO,
    )
    return logging
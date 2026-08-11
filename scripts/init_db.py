import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aplicacao.core.banco_dados import Base, engine
from aplicacao.core.config import config
from aplicacao.utils.logger import log_info

def init_database():
    """Inicializa o banco de dados"""
    log_info(" Inicializando banco de dados...")
    

    Base.metadata.create_all(engine)
    
    log_info(f" Banco de dados criado em: {config.CAMINHO_BANCO_SQL}")
    log_info(f" Banco vetorial criado em: {config.CAMINHO_BANCO_VETORIAL}")

if __name__ == "__main__":
    init_database()
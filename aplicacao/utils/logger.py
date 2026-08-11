"""
Sistema de logging centralizado
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from ..core.config import config

def setup_logger(nome: str = "rag_app") -> logging.Logger:
    """
    Configura e retorna um logger
    
    Parâmetros:
    - nome: Nome do logger
    
    Retorna:
    - Logger configurado
    """
    logger = logging.getLogger(nome)
    
    # Evita duplicação de handlers
    if logger.handlers:
        return logger
    
    logger.setLevel(getattr(logging, config.NIVEL_LOG.upper()))

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
  
    log_file = Path(config.CAMINHO_LOGS) / f"{datetime.now().strftime('%Y%m%d')}_app.log"
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger

logger = setup_logger()

def log_info(mensagem: str):
    """Log de informação"""
    logger.info(mensagem)

def log_erro(mensagem: str, erro: Exception = None):
    """Log de erro"""
    if erro:
        logger.error(f"{mensagem} - {str(erro)}", exc_info=True)
    else:
        logger.error(mensagem)

def log_debug(mensagem: str):
    """Log de debug"""
    logger.debug(mensagem)

def log_warning(mensagem: str):
    """Log de aviso"""
    logger.warning(mensagem)
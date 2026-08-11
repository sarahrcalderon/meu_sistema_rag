"""
Configurações centralizadas do sistema
Carrega variáveis de ambiente com valores padrão
"""

import os
from pathlib import Path
from urllib.parse import urlparse
from dotenv import load_dotenv
from dataclasses import dataclass


load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent.parent

@dataclass
class Config:
    """Configurações do sistema"""

    OLLAMA_URL: str = os.getenv('OLLAMA_URL', 'http://localhost:11434')
    MODELO_OLLAMA: str = os.getenv('MODELO_OLLAMA', 'tinyllama')
    
    CAMINHO_BANCO_SQL: str = os.getenv(
        'CAMINHO_BANCO_SQL',
        str(BASE_DIR / 'dados' / 'bancosistemarag')
    )
    CAMINHO_BANCO_VETORIAL: str = os.getenv(
        'CAMINHO_BANCO_VETORIAL',
        str(BASE_DIR / 'dados' / 'chroma_db')
    )
    

    MODELO_EMBEDDING: str = os.getenv('MODELO_EMBEDDING', 'all-MiniLM-L6-v2')
    TAMANHO_EMBEDDING: int = 384  # Dimensão do vetor

    TAMANHO_CHUNK: int = int(os.getenv('TAMANHO_CHUNK', 500))
    TOP_K_PADRAO: int = int(os.getenv('TOP_K_PADRAO', 5))
    MAX_CHUNKS_CONTEXTO: int = 3  # Limite para o TinyLlama
    
    TEMPERATURA: float = float(os.getenv('TEMPERATURA', 0.3))
    MAX_TOKENS: int = int(os.getenv('MAX_TOKENS', 500))
    TIMEOUT: int = 120  # Segundos
    
    NIVEL_LOG: str = os.getenv('NIVEL_LOG', 'INFO')
    CAMINHO_LOGS: str = str(BASE_DIR / 'logs')
    

    TITULO_API: str = "Sistema RAG com TinyLlama"
    VERSAO_API: str = "1.0.0"
    HOST_API: str = "0.0.0.0"
    PORTA_API: int = 8000


config = Config()

os.makedirs(config.CAMINHO_LOGS, exist_ok=True)

def _criar_diretorio_sql_if_necessario(caminho_sql: str) -> None:
    """Cria o diretório do banco apenas quando o valor for um caminho local."""
    if caminho_sql.startswith("sqlite:///"):
        parsed = urlparse(caminho_sql)
        if parsed.path in ("/:memory:", ":memory:"):
            return

        caminho_arquivo = parsed.path.lstrip("/")
        if caminho_arquivo:
            os.makedirs(os.path.dirname(caminho_arquivo), exist_ok=True)
        return

    diretorio = os.path.dirname(caminho_sql)
    if diretorio:
        os.makedirs(diretorio, exist_ok=True)


_criar_diretorio_sql_if_necessario(config.CAMINHO_BANCO_SQL)
os.makedirs(config.CAMINHO_BANCO_VETORIAL, exist_ok=True)
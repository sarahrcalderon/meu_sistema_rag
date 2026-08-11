import os
from pathlib import Path
from dotenv import load_dotenv
from dataclasses import dataclass


load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent.parent

@dataclass
class Config:
    """Configurações do sistema"""
    
    OLLAMA_URL: str = os.getenv('OLLAMA_URL', 'http://localhost:11434')
    MODELO_OLLAMA: str = os.getenv('MODELO_OLLAMA', 'llama3.2')  

    CAMINHO_BANCO_SQL: str = os.getenv(
        'CAMINHO_BANCO_SQL',
        str(BASE_DIR / '.database' / 'bancosistemarag.db')
    )
    CAMINHO_BANCO_VETORIAL: str = os.getenv(
        'CAMINHO_BANCO_VETORIAL',
        str(BASE_DIR / '.database' / 'chroma_db')
    )
    
    MODELO_EMBEDDING: str = os.getenv('MODELO_EMBEDDING', 'all-MiniLM-L6-v2')
    TAMANHO_EMBEDDING: int = 384

    TAMANHO_CHUNK: int = int(os.getenv('TAMANHO_CHUNK', 500))
    TOP_K_PADRAO: int = int(os.getenv('TOP_K_PADRAO', 3))  
    MAX_CHUNKS_CONTEXTO: int = 3

    TEMPERATURA: float = float(os.getenv('TEMPERATURA', 0.3))
    MAX_TOKENS: int = int(os.getenv('MAX_TOKENS', 1000)) 
    TIMEOUT: int = 120
    
    NIVEL_LOG: str = os.getenv('NIVEL_LOG', 'INFO')
    CAMINHO_LOGS: str = str(BASE_DIR / 'logs')
    
    TITULO_API: str = "Sistema RAG com Llama 3.2"
    VERSAO_API: str = "1.0.0"
    HOST_API: str = "0.0.0.0"
    PORTA_API: int = 8000


config = Config()

try:
  
    db_dir = os.path.dirname(config.CAMINHO_BANCO_SQL)
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)
        print(f" Diretório criado: {db_dir}")

    os.makedirs(config.CAMINHO_BANCO_VETORIAL, exist_ok=True)
    print(f" Diretório criado: {config.CAMINHO_BANCO_VETORIAL}")
  
    os.makedirs(config.CAMINHO_LOGS, exist_ok=True)
    print(f" Diretório criado: {config.CAMINHO_LOGS}")
    
except Exception as e:
    print(f"Erro ao criar diretórios: {e}")
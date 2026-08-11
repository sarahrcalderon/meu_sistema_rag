from typing import Optional
from ..core.processador import ProcessadorRAG, processador
from ..services.ollama_service import ollama_service
from ..utils.logger import logger

def get_processador() -> ProcessadorRAG:
    """
    Injeta o processador RAG
    
    Retorna:
    - Instância do ProcessadorRAG
    """
    return processador

def get_ollama_service():
    """
    Injeta o serviço Ollama
    
    Retorna:
    - Instância do OllamaService
    """
    return ollama_service

def get_logger():
    """
    Injeta o logger
    
    Retorna:
    - Instância do logger
    """
    return logger
"""
Modelos de dados (Pydantic) para validação da API
"""

from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class PerguntaRequest(BaseModel):
    """Modelo para requisição de pergunta"""
    pergunta: str
    quantidade_resultados: Optional[int] = 5
    
    class Config:
        json_schema_extra = {
            "example": {
                "pergunta": "Qual o total de vendas?",
                "quantidade_resultados": 5
            }
        }

class RespostaResponse(BaseModel):
    """Modelo para resposta da API"""
    pergunta: str
    resposta: str
    fontes: Optional[List[str]] = []
    timestamp: str
    chunks_utilizados: int = 0
    
    class Config:
        json_schema_extra = {
            "example": {
                "pergunta": "Qual o total de vendas?",
                "resposta": "O total de vendas foi R$ 50.000",
                "fontes": ["Documento 1", "Documento 2"],
                "timestamp": "2024-01-01T10:00:00",
                "chunks_utilizados": 3
            }
        }

class UploadResponse(BaseModel):
    """Modelo para resposta de upload"""
    mensagem: str
    id_documento: int
    total_chunks: int
    nome_arquivo: str

class DocumentoResponse(BaseModel):
    """Modelo para listar documentos"""
    id: int
    nome: str
    data_upload: str
    total_paginas: int
    quantidade_chunks: int

class StatusResponse(BaseModel):
    """Modelo para status do sistema"""
    status: str
    total_chunks: int
    ollama_rodando: bool
    modelo: str
    timestamp: str

class ErroResponse(BaseModel):
    """Modelo para erros"""
    erro: str
    detalhe: Optional[str] = None
    timestamp: str
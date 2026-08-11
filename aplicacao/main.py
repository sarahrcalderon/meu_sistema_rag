"""
Arquivo principal de configuração da aplicação FastAPI
Aqui importamos as rotas e configuramos a aplicação
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import os
from datetime import datetime
from dotenv import load_dotenv


load_dotenv()

from .api.routes import router

app = FastAPI(
    title="Sistema RAG com TinyLlama - Chat com Documentos",
    description="""
    API para conversar com seus documentos usando TinyLlama (local e grátis)
    
    ## Funcionalidades:
    -  Upload de documentos (PDF, TXT, CSV)
    -  Busca semântica com ChromaDB
    -  Chat com TinyLlama (local)
    -  Métricas e status do sistema
    
    ## Tecnologias:
    - FastAPI + Uvicorn
    - ChromaDB (Banco Vetorial)
    - SQLite
    - Ollama + TinyLlama
    - Sentence-Transformers
    """,
    version="1.0.0",
    contact={
        "name": "Seu Nome",
        "email": "seu@email.com",
    },
    license_info={
        "name": "MIT",
    }
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, coloque o domínio específico
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(router)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    """Trata erros de validação"""
    return JSONResponse(
        status_code=422,
        content={
            "erro": "Erro de validação",
            "detalhes": exc.errors(),
            "timestamp": datetime.now().isoformat()
        }
    )

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Trata erros globais"""
    return JSONResponse(
        status_code=500,
        content={
            "erro": "Erro interno do servidor",
            "detalhe": str(exc),
            "timestamp": datetime.now().isoformat()
        }
    )

@app.on_event("startup")
async def startup_event():
    """Executa quando a API inicia"""
    print("=" * 50)
    print(" Iniciando Sistema RAG com TinyLlama")
    print("=" * 50)
    print(f" Banco SQL: {os.getenv('CAMINHO_BANCO_SQL', 'sqlite:///dados/meu_banco.db')}")
    print(f" Banco Vetorial: {os.getenv('CAMINHO_BANCO_VETORIAL', './dados/chroma_db')}")
    print(f" Modelo: {os.getenv('MODELO_OLLAMA', 'tinyllama')}")
    print("=" * 50)
    print(" API disponível em: http://localhost:8000")
    print(" Documentação: http://localhost:8000/docs")
    print("=" * 50)

@app.on_event("shutdown")
async def shutdown_event():
    """Executa quando a API para"""
    print(" Encerrando Sistema RAG com TinyLlama...")
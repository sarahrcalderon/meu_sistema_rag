from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from fastapi.responses import JSONResponse
import os
import shutil
from datetime import datetime
from typing import List


from .models import (
    PerguntaRequest,
    RespostaResponse,
    UploadResponse,
    DocumentoResponse,
    StatusResponse
)


from .dependencies import get_processador, get_ollama_service, get_logger

from ..core.banco_dados import (
    salvar_no_sql,
    listar_documentos_sql,
    Documento,
    SessaoLocal,
    contar_chunks,
    limpar_banco_vetorial
)
from ..core.config import config


router = APIRouter()


@router.get("/", tags=["Status"])
async def raiz():
    """Endpoint inicial"""
    return {
        "mensagem": f" {config.TITULO_API}",
        "status": "online",
        "versao": config.VERSAO_API,
        "documentacao": "/docs",
        "total_chunks": contar_chunks()
    }

@router.get("/status", response_model=StatusResponse, tags=["Status"])
async def status_sistema(
    processador = Depends(get_processador)
):
    """Status completo do sistema"""
    status = processador.verificar_sistema()
    return StatusResponse(
        status="online",
        total_chunks=status.get("chunks", 0),
        ollama_rodando=status.get("ollama_rodando", False),
        modelo=status.get("modelo", "tinyllama"),
        timestamp=datetime.now().isoformat()
    )

@router.get("/health", tags=["Status"])
async def health_check():
    """Health check para orquestradores"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@router.post("/upload", response_model=UploadResponse, tags=["Documentos"])
async def fazer_upload(
    arquivo: UploadFile = File(...),
    processador = Depends(get_processador),
    logger = Depends(get_logger)
):
    """Upload de documentos (PDF, TXT, CSV)"""
    
    logger.info(f"Upload solicitado: {arquivo.filename}")
    
    extensao = os.path.splitext(arquivo.filename)[1].lower()
    if extensao not in ['.pdf', '.txt', '.csv']:
        raise HTTPException(400, f"Arquivo não suportado. Use: PDF, TXT, CSV")
    
    os.makedirs("dados/documentos", exist_ok=True)
    caminho = f"dados/documentos/{datetime.now().strftime('%Y%m%d_%H%M%S')}_{arquivo.filename}"
    
    try:
        with open(caminho, "wb") as buffer:
            shutil.copyfileobj(arquivo.file, buffer)
        
        # Extrai texto
        texto, paginas = await _extrair_texto(caminho, extensao)
        
        if not texto.strip():
            raise HTTPException(400, "Não foi possível extrair texto")
        
        # Processa documento
        resultado = processador.processar_documento(texto, arquivo.filename)
        
        if "erro" in resultado:
            raise HTTPException(400, resultado["erro"])
        
        # Salva metadados
        id_doc = salvar_no_sql(
            nome_arquivo=arquivo.filename,
            total_paginas=paginas,
            resumo=texto[:500],
            quantidade_chunks=resultado["total_chunks"]
        )
        
        logger.info(f"Documento processado: ID={id_doc}, Chunks={resultado['total_chunks']}")
        
        return UploadResponse(
            mensagem=f" Documento '{arquivo.filename}' processado!",
            id_documento=id_doc,
            total_chunks=resultado["total_chunks"],
            nome_arquivo=arquivo.filename
        )
        
    except HTTPException:
        raise
    except Exception as erro:
        logger.error(f"Erro no upload: {erro}")
        raise HTTPException(500, str(erro))
    finally:
        if os.path.exists(caminho):
            os.remove(caminho)

async def _extrair_texto(caminho: str, extensao: str) -> tuple:
    """Extrai texto de diferentes tipos de arquivo"""
    texto = ""
    paginas = 1
    
    if extensao == '.pdf':
        from pypdf import PdfReader
        leitor = PdfReader(caminho)
        paginas = len(leitor.pages)
        for pagina in leitor.pages:
            try:
                texto += pagina.extract_text() + "\n"
            except:
                pass
    else:
        try:
            with open(caminho, 'r', encoding='utf-8') as f:
                texto = f.read()
        except UnicodeDecodeError:
            with open(caminho, 'r', encoding='latin-1') as f:
                texto = f.read()
    
    return texto, paginas

@router.get("/documentos", response_model=List[DocumentoResponse], tags=["Documentos"])
async def listar_documentos():
    """Lista todos os documentos"""
    try:
        docs = listar_documentos_sql()
        return [
            DocumentoResponse(
                id=d.id,
                nome=d.nome,
                data_upload=d.data_upload.isoformat(),
                total_paginas=d.total_paginas,
                quantidade_chunks=d.quantidade_chunks
            )
            for d in docs
        ]
    except Exception as erro:
        raise HTTPException(500, str(erro))


@router.post("/perguntar", response_model=RespostaResponse, tags=["Perguntas"])
async def fazer_pergunta(
    requisicao: PerguntaRequest,
    processador = Depends(get_processador),
    logger = Depends(get_logger)
):
    """Faz uma pergunta sobre os documentos"""
    
    logger.info(f"Pergunta: {requisicao.pergunta[:50]}...")
    
    try:
        resultado = processador.responder_pergunta(
            requisicao.pergunta,
            requisicao.quantidade_resultados
        )
        
        logger.info(f"Resposta gerada com {resultado['chunks_utilizados']} chunks")
        
        return RespostaResponse(
            pergunta=resultado["pergunta"],
            resposta=resultado["resposta"],
            fontes=resultado.get("fontes", []),
            timestamp=datetime.now().isoformat(),
            chunks_utilizados=resultado.get("chunks_utilizados", 0)
        )
        
    except Exception as erro:
        logger.error(f"Erro na pergunta: {erro}")
        raise HTTPException(500, str(erro))


@router.delete("/limpar", tags=["Manutenção"])
async def limpar_dados(logger = Depends(get_logger)):
    """Limpa todos os dados"""
    try:
        limpar_banco_vetorial()
        
        sessao = SessaoLocal()
        try:
            sessao.query(Documento).delete()
            sessao.commit()
            logger.info("Dados limpos com sucesso")
            return {"mensagem": " Todos os dados foram limpos!"}
        except Exception as erro:
            sessao.rollback()
            raise
        finally:
            sessao.close()
            
    except Exception as erro:
        logger.error(f"Erro ao limpar dados: {erro}")
        raise HTTPException(500, str(erro))

@router.get("/testar-ollama", tags=["Manutenção"])
async def testar_ollama(
    ollama = Depends(get_ollama_service)
):
    """Testa a conexão com o Ollama"""
    from ..core.prompts import testar_tinyllama
    
    if ollama.verificar_servidor():
        resposta = testar_tinyllama()
        return {
            "status": "sucesso",
            "mensagem": "TinyLlama está funcionando!",
            "resposta_teste": resposta
        }
    else:
        return {
            "status": "erro",
            "mensagem": "Ollama/TinyLlama não está rodando",
            "dica": "Inicie com: ollama serve"
        }
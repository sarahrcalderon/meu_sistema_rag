from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import chromadb
from chromadb.config import Settings
import os
from datetime import datetime
from urllib.parse import urlparse
from dotenv import load_dotenv
from pathlib import Path


load_dotenv()

from .config import config

Base = declarative_base()

caminho_sql = config.CAMINHO_BANCO_SQL

def _configurar_sqlite(caminho: str) -> tuple[str, dict]:
    """Normaliza caminhos SQLite locais e ignora URIs em memória."""
    if caminho.startswith("sqlite:///"):
        parsed = urlparse(caminho)
        if parsed.path in ("/:memory:", ":memory:"):
            return caminho, {"check_same_thread": False}

        caminho_arquivo = parsed.path.lstrip("/")
        if caminho_arquivo and not os.path.isabs(caminho_arquivo):
            caminho_arquivo = os.path.abspath(caminho_arquivo)
        if caminho_arquivo:
            diretorio = os.path.dirname(caminho_arquivo)
            if diretorio:
                os.makedirs(diretorio, exist_ok=True)
            return f"sqlite:///{caminho_arquivo.replace('\\', '/')}" , {"check_same_thread": False}

    if not os.path.isabs(caminho):
        caminho = os.path.abspath(caminho)

    diretorio = os.path.dirname(caminho)
    if diretorio:
        os.makedirs(diretorio, exist_ok=True)

    if os.name == 'nt':
        caminho = caminho.replace('\\', '/')

    return f"sqlite:///{caminho}", {"check_same_thread": False}


url_sql, sqlite_connect_args = _configurar_sqlite(caminho_sql)

print(f" Banco SQL: {url_sql}")

# Cria o engine
engine = create_engine(
    url_sql,
    connect_args=sqlite_connect_args if 'sqlite' in url_sql else {}
)
SessaoLocal = sessionmaker(bind=engine)

class Documento(Base):
    """Tabela que guarda informações dos documentos"""
    __tablename__ = 'documentos'
    
    id = Column(Integer, primary_key=True)
    nome = Column(String(200))
    data_upload = Column(DateTime, default=datetime.now)
    total_paginas = Column(Integer)
    resumo = Column(Text)
    quantidade_chunks = Column(Integer)

# Cria as tabelas
try:
    Base.metadata.create_all(engine)
    print(" Tabelas SQL criadas com sucesso!")
except Exception as e:
    print(f" Erro ao criar tabelas SQL: {e}")


caminho_vetorial = config.CAMINHO_BANCO_VETORIAL

if caminho_vetorial:
    os.makedirs(caminho_vetorial, exist_ok=True)

try:
    cliente_chroma = chromadb.PersistentClient(
        path=caminho_vetorial,
        settings=Settings(anonymized_telemetry=False)
    )
    print(f" Banco vetorial configurado em: {caminho_vetorial}")
except Exception as e:
    print(f" Erro ao configurar banco vetorial: {e}")
    # Cria um cliente com fallback
    cliente_chroma = chromadb.PersistentClient(
        path="./dados/chroma_db",
        settings=Settings(anonymized_telemetry=False)
    )


try:
    colecao = cliente_chroma.get_or_create_collection(
        name="documentos_rag",
        metadata={"hnsw:space": "cosine"}
    )
    print(" Coleção ChromaDB criada/recuperada com sucesso!")
except Exception as e:
    print(f" Erro ao criar coleção: {e}")
    # Tenta criar com outro nome
    colecao = cliente_chroma.get_or_create_collection(
        name="documentos_rag_v2",
        metadata={"hnsw:space": "cosine"}
    )



def salvar_no_sql(nome_arquivo, total_paginas, resumo, quantidade_chunks):
    """Salva os metadados do documento no banco SQL"""
    sessao = SessaoLocal()
    try:
        documento = Documento(
            nome=nome_arquivo,
            total_paginas=total_paginas,
            resumo=resumo[:500] if resumo else "",
            quantidade_chunks=quantidade_chunks
        )
        sessao.add(documento)
        sessao.commit()
        return documento.id
    except Exception as erro:
        sessao.rollback()
        raise erro
    finally:
        sessao.close()

def listar_documentos_sql():
    """Retorna a lista de todos os documentos salvos"""
    sessao = SessaoLocal()
    try:
        documentos = sessao.query(Documento).all()
        return documentos
    finally:
        sessao.close()

def buscar_documento_por_id(id_documento):
    """Busca um documento específico pelo ID"""
    sessao = SessaoLocal()
    try:
        documento = sessao.query(Documento).filter(Documento.id == id_documento).first()
        return documento
    finally:
        sessao.close()


def salvar_no_vetorial(chunks, embeddings, metadados):
    """Salva os pedaços de texto e seus vetores no ChromaDB"""
    if not chunks:
        return 0
    
    try:
  
        ids = [f"pedaco_{datetime.now().timestamp()}_{i}" for i in range(len(chunks))]
   
        colecao.add(
            documents=chunks,
            embeddings=embeddings,
            metadatas=metadados,
            ids=ids
        )
        return len(ids)
    except Exception as e:
        print(f" Erro ao salvar no vetorial: {e}")
        return 0

def buscar_no_vetorial(embedding_pergunta, quantidade=5):
    """Busca os pedaços de texto mais relevantes para a pergunta"""
    try:
        resultados = colecao.query(
            query_embeddings=[embedding_pergunta],
            n_results=quantidade
        )
        
        if resultados and resultados['documents']:
            return resultados['documents'][0]
        return []
    except Exception as e:
        print(f" Erro ao buscar no vetorial: {e}")
        return []

def buscar_com_metadados(embedding_pergunta, quantidade=5):
    """Busca os pedaços de texto com seus metadados"""
    try:
        resultados = colecao.query(
            query_embeddings=[embedding_pergunta],
            n_results=quantidade
        )
        return resultados
    except Exception:
        return {"documents": [], "metadatas": [], "distances": []}

def limpar_banco_vetorial():
    """Remove todos os dados do banco vetorial"""
    try:
        cliente_chroma.delete_collection("documentos_rag")

        global colecao
        colecao = cliente_chroma.get_or_create_collection(
            name="documentos_rag",
            metadata={"hnsw:space": "cosine"}
        )
        return "Banco vetorial limpo com sucesso!"
    except Exception as erro:
        return f"Erro ao limpar: {erro}"

def contar_chunks():
    """Retorna o número total de chunks no banco vetorial"""
    try:
        return colecao.count()
    except Exception:
        return 0
# aplicacao/core/banco_dados.py
"""
Módulo responsável por gerenciar:
1. Banco de dados SQL (metadados dos documentos)
2. Banco vetorial ChromaDB (busca semântica)
"""

from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import chromadb
from chromadb.config import Settings
import os
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path

# Carrega as configurações
load_dotenv()

# Tenta importar a configuração
try:
    from .config import config
except ImportError:
    # Fallback: usa valores padrão
    from dataclasses import dataclass
    @dataclass
    class Config:
        CAMINHO_BANCO_SQL = os.getenv('CAMINHO_BANCO_SQL', '.database/bancosistemarag.db')
        CAMINHO_BANCO_VETORIAL = os.getenv('CAMINHO_BANCO_VETORIAL', '.database/chroma_db')
    config = Config()

# ==========================================
# 1. CONFIGURAÇÃO DO BANCO SQL
# ==========================================

Base = declarative_base()

# CORRIGIDO: Usa o caminho correto
caminho_sql = config.CAMINHO_BANCO_SQL

# Converte para caminho absoluto se for relativo
if not os.path.isabs(caminho_sql):
    caminho_sql = os.path.abspath(caminho_sql)

# Garante que o diretório existe
sql_dir = os.path.dirname(caminho_sql)
if sql_dir:
    os.makedirs(sql_dir, exist_ok=True)

# Cria a URL do SQLite corretamente para Windows
if os.name == 'nt':  # Windows
    caminho_sql = caminho_sql.replace('\\', '/')
    if not caminho_sql.startswith('sqlite:///'):
        url_sql = f"sqlite:///{caminho_sql}"
    else:
        url_sql = caminho_sql
else:  # Linux/Mac
    if not caminho_sql.startswith('sqlite:///'):
        url_sql = f"sqlite:///{caminho_sql}"
    else:
        url_sql = caminho_sql

print(f"📁 Banco SQL: {url_sql}")

# Cria o engine
engine = create_engine(
    url_sql,
    connect_args={"check_same_thread": False} if 'sqlite' in url_sql else {}
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
    print("✅ Tabelas SQL criadas com sucesso!")
except Exception as e:
    print(f"⚠️ Erro ao criar tabelas SQL: {e}")

# ==========================================
# 2. CONFIGURAÇÃO DO BANCO VETORIAL
# ==========================================

caminho_vetorial = config.CAMINHO_BANCO_VETORIAL

# Garante que o diretório existe
os.makedirs(caminho_vetorial, exist_ok=True)

# Variáveis globais para o ChromaDB
cliente_chroma = None
colecao = None

try:
    cliente_chroma = chromadb.PersistentClient(
        path=caminho_vetorial,
        settings=Settings(anonymized_telemetry=False)
    )
    print(f"✅ Banco vetorial configurado em: {caminho_vetorial}")
except Exception as e:
    print(f"⚠️ Erro ao configurar banco vetorial: {e}")
    # Cria um cliente com fallback
    os.makedirs(".database/chroma_db", exist_ok=True)
    try:
        cliente_chroma = chromadb.PersistentClient(
            path=".database/chroma_db",
            settings=Settings(anonymized_telemetry=False)
        )
        print("✅ Banco vetorial fallback configurado!")
    except Exception as e2:
        print(f"❌ Erro ao configurar banco vetorial fallback: {e2}")
        cliente_chroma = None

# Cria ou recupera a coleção
if cliente_chroma is not None:
    try:
        colecao = cliente_chroma.get_or_create_collection(
            name="documentos_rag",
            metadata={"hnsw:space": "cosine"}
        )
        print("✅ Coleção ChromaDB criada/recuperada com sucesso!")
    except Exception as e:
        print(f"⚠️ Erro ao criar coleção: {e}")
        # Tenta criar com outro nome
        try:
            colecao = cliente_chroma.get_or_create_collection(
                name="documentos_rag_v2",
                metadata={"hnsw:space": "cosine"}
            )
            print("✅ Coleção alternativa criada!")
        except Exception as e2:
            print(f"❌ Não foi possível criar a coleção ChromaDB: {e2}")
            colecao = None
else:
    colecao = None

# ==========================================
# 3. FUNÇÕES PARA SALVAR NO SQL
# ==========================================

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

# ==========================================
# 4. FUNÇÕES PARA SALVAR NO BANCO VETORIAL
# ==========================================

def salvar_no_vetorial(chunks, embeddings, metadados):
    """Salva os pedaços de texto e seus vetores no ChromaDB"""
    global colecao
    
    if not chunks:
        return 0
    
    if colecao is None:
        print("⚠️ Coleção ChromaDB não disponível")
        return 0
    
    try:
        # Gera IDs únicos
        ids = [f"pedaco_{datetime.now().timestamp()}_{i}" for i in range(len(chunks))]
        
        # Adiciona à coleção
        colecao.add(
            documents=chunks,
            embeddings=embeddings,
            metadatas=metadados,
            ids=ids
        )
        return len(ids)
    except Exception as e:
        print(f"⚠️ Erro ao salvar no vetorial: {e}")
        return 0

def buscar_no_vetorial(embedding_pergunta, quantidade=5):
    """Busca os pedaços de texto mais relevantes para a pergunta"""
    global colecao
    
    if colecao is None:
        return []
    
    try:
        resultados = colecao.query(
            query_embeddings=[embedding_pergunta],
            n_results=quantidade
        )
        
        if resultados and resultados['documents']:
            return resultados['documents'][0]
        return []
    except Exception as e:
        print(f"⚠️ Erro ao buscar no vetorial: {e}")
        return []

def buscar_com_metadados(embedding_pergunta, quantidade=5):
    """Busca os pedaços de texto com seus metadados"""
    global colecao
    
    if colecao is None:
        return {"documents": [], "metadatas": [], "distances": []}
    
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
    global colecao, cliente_chroma
    
    if colecao is None or cliente_chroma is None:
        return "Banco vetorial não disponível"
    
    try:
        cliente_chroma.delete_collection("documentos_rag")
        # Recria a coleção vazia
        colecao = cliente_chroma.get_or_create_collection(
            name="documentos_rag",
            metadata={"hnsw:space": "cosine"}
        )
        return "Banco vetorial limpo com sucesso!"
    except Exception as erro:
        return f"Erro ao limpar: {erro}"

def contar_chunks():
    """Retorna o número total de chunks no banco vetorial"""
    global colecao
    
    if colecao is None:
        return 0
    try:
        return colecao.count()
    except Exception:
        return 0
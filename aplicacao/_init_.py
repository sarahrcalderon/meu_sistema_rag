# aplicacao/__init__.py
"""
Pacote principal da aplicação RAG com TinyLlama
"""

from .principal import app
from .banco_dados import (
    salvar_no_sql,
    buscar_no_vetorial,
    listar_documentos_sql,
    Documento,
    SessaoLocal,
    contar_chunks
)
from .embeddings import (
    gerar_embedding,
    gerar_embeddings_lote,
    testar_embedding
)
from .prompts import (
    processar_pergunta,
    testar_tinyllama,
    verificar_ollama,
    chamar_tinyllama
)

__version__ = "1.0.0"
__all__ = [
    'app',
    'salvar_no_sql',
    'buscar_no_vetorial',
    'listar_documentos_sql',
    'Documento',
    'SessaoLocal',
    'contar_chunks',
    'gerar_embedding',
    'gerar_embeddings_lote',
    'testar_embedding',
    'processar_pergunta',
    'testar_tinyllama',
    'verificar_ollama',
    'chamar_tinyllama'
]

print(f"🦙 Sistema RAG com TinyLlama v{__version__} carregado!")
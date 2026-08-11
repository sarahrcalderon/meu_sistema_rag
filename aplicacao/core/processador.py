"""
Orquestrador do pipeline RAG
Coordena as operações de embedding, busca e geração
"""

from typing import List, Dict, Any
from ..core.config import config
from ..core.embeddings import gerar_embedding, gerar_embeddings_lote
from ..core.banco_dados import buscar_no_vetorial, salvar_no_vetorial
from ..core.prompts import processar_pergunta
from ..services.ollama_service import ollama_service
from ..utils.logger import log_info, log_erro, log_debug

class ProcessadorRAG:
    """
    Orquestrador do pipeline RAG (Retrieval-Augmented Generation)
    """
    
    def __init__(self):
        self.tamanho_chunk = config.TAMANHO_CHUNK
        self.top_k = config.TOP_K_PADRAO
        self.max_chunks = config.MAX_CHUNKS_CONTEXTO
        
    def processar_documento(self, texto: str, nome_arquivo: str) -> Dict[str, Any]:
        """
        Processa um documento: divide em chunks, gera embeddings e salva
        
        Parâmetros:
        - texto: Texto completo do documento
        - nome_arquivo: Nome do arquivo
        
        Retorna:
        - Dicionário com resultados do processamento
        """
        log_info(f"Processando documento: {nome_arquivo}")
        
        chunks = self._dividir_chunks(texto)
        
        if not chunks:
            log_erro(f"Documento vazio: {nome_arquivo}")
            return {"erro": "Documento vazio", "chunks": []}
        
        log_debug(f"Documento dividido em {len(chunks)} chunks")
        
        embeddings = gerar_embeddings_lote(chunks)
        
        metadados = [
            {
                "arquivo": nome_arquivo,
                "indice_chunk": i,
                "total_chunks": len(chunks),
                "tamanho": len(chunk)
            }
            for i, chunk in enumerate(chunks)
        ]
        
        total = salvar_no_vetorial(chunks, embeddings, metadados)
        
        log_info(f"Documento processado: {total} chunks salvos")
        
        return {
            "chunks": chunks,
            "embeddings": embeddings,
            "total_chunks": total,
            "metadados": metadados
        }
    
    def responder_pergunta(self, pergunta: str, top_k: int = None) -> Dict[str, Any]:
        """
        Processa uma pergunta e gera uma resposta
        
        Parâmetros:
        - pergunta: Pergunta do usuário
        - top_k: Número de chunks a buscar
        
        Retorna:
        - Dicionário com resposta e metadados
        """
        log_info(f"Processando pergunta: {pergunta[:50]}...")
        
        embedding = gerar_embedding(pergunta)
        
        k = top_k or self.top_k
        chunks = buscar_no_vetorial(embedding, k)
        
        if not chunks:
            log_info("Nenhum chunk encontrado para a pergunta")
            return {
                "pergunta": pergunta,
                "resposta": " Nenhum documento relevante encontrado.",
                "chunks_utilizados": 0,
                "fontes": []
            }
        
        log_debug(f"Encontrados {len(chunks)} chunks relevantes")
        
        contexto = "\n\n".join(chunks[:self.max_chunks])
        
        resposta = processar_pergunta(pergunta, contexto)
        
        return {
            "pergunta": pergunta,
            "resposta": resposta,
            "chunks_utilizados": len(chunks),
            "fontes": [f"Chunk {i+1}" for i in range(len(chunks))]
        }
    
    def _dividir_chunks(self, texto: str) -> List[str]:
        """
        Divide o texto em chunks
        
        Parâmetros:
        - texto: Texto a ser dividido
        
        Retorna:
        - Lista de chunks
        """
        if not texto or not texto.strip():
            return []
        
        chunks = []

        paragrafos = texto.split('\n\n')
        
        for paragrafo in paragrafos:
            paragrafo = paragrafo.strip()
            if not paragrafo:
                continue
                
            if len(paragrafo) <= self.tamanho_chunk:
                chunks.append(paragrafo)
            else:
                for i in range(0, len(paragrafo), self.tamanho_chunk):
                    chunk = paragrafo[i:i+self.tamanho_chunk]
                    if chunk.strip():
                        chunks.append(chunk.strip())
        
        return chunks
    
    def verificar_sistema(self) -> Dict[str, Any]:
        """Verifica o status do sistema"""
        return {
            "ollama_rodando": ollama_service.verificar_servidor(),
            "modelo": config.MODELO_OLLAMA,
            "chunks": self._contar_chunks_total(),
            "config": {
                "tamanho_chunk": self.tamanho_chunk,
                "top_k": self.top_k,
                "max_chunks": self.max_chunks
            }
        }
    
    def _contar_chunks_total(self) -> int:
        """Conta o total de chunks no banco vetorial"""
        try:
            from ..core.banco_dados import contar_chunks
            return contar_chunks()
        except:
            return 0

processador = ProcessadorRAG()
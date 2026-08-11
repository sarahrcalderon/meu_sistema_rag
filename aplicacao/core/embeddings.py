from sentence_transformers import SentenceTransformer
import os
import numpy as np
from dotenv import load_dotenv

load_dotenv()

MODELO_EMBEDDING = 'all-MiniLM-L6-v2'

print(" Carregando modelo de embedding...")
try:
    modelo_local = SentenceTransformer(MODELO_EMBEDDING)
    dimensao = modelo_local.get_sentence_embedding_dimension()
    print(f" Modelo '{MODELO_EMBEDDING}' carregado!")
    print(f"   Dimensão do vetor: {dimensao}")
except Exception as erro:
    print(f" Erro ao carregar modelo: {erro}")
    print("   Tentando modelo alternativo...")
    modelo_local = SentenceTransformer('paraphrase-MiniLM-L3-v2')
    print(" Modelo alternativo carregado!")


def gerar_embedding(texto):
    """
    Gera o vetor (embedding) de UM texto
    
    Parâmetros:
    - texto: String com o texto a ser convertido
    
    Retorna:
    - Lista de números (vetor) representando o texto
    """
    if not texto or texto.strip() == "":
        return [0.0] * modelo_local.get_sentence_embedding_dimension()
    
    try:
        vetor = modelo_local.encode(texto, convert_to_numpy=True)
        return vetor.tolist()
    except Exception as erro:
        print(f"Erro ao gerar embedding: {erro}")
        return [0.0] * modelo_local.get_sentence_embedding_dimension()

def gerar_embeddings_lote(textos):
    """
    Gera vetores para VÁRIOS textos de uma vez (mais rápido)
    
    Parâmetros:
    - textos: Lista de strings
    
    Retorna:
    - Lista de vetores (cada um é uma lista de números)
    """
    if not textos:
        return []

    textos_validos = [t for t in textos if t and t.strip()]
    
    if not textos_validos:
        return []
    
    try:
        vetores = modelo_local.encode(textos_validos, convert_to_numpy=True)
        return [v.tolist() for v in vetores]
    except Exception as erro:
        print(f"Erro ao gerar embeddings em lote: {erro}")

        return [gerar_embedding(t) for t in textos_validos]

def gerar_embedding_com_modelo(texto, nome_modelo=None):
    """
    Versão flexível que permite escolher outro modelo
    
    Parâmetros:
    - texto: Texto a converter
    - nome_modelo: Nome de outro modelo (opcional)
    """
    modelo_usar = nome_modelo or MODELO_EMBEDDING
    try:
        from sentence_transformers import SentenceTransformer
        modelo = SentenceTransformer(modelo_usar)
        vetor = modelo.encode(texto, convert_to_numpy=True)
        return vetor.tolist()
    except Exception as erro:
        print(f"Erro: {erro}")
        return gerar_embedding(texto)

def similaridade_cosseno(vetor1, vetor2):
    """Calcula a similaridade entre dois vetores"""
    import numpy as np
    v1 = np.array(vetor1)
    v2 = np.array(vetor2)
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

def testar_embedding():
    """Função para verificar se o embedding está funcionando"""
    texto_teste = "Este é um teste do sistema de embeddings com TinyLlama."
    vetor = gerar_embedding(texto_teste)
    print(f" Embedding gerado com sucesso!")
    print(f"   Tamanho do vetor: {len(vetor)}")
    print(f"   Primeiros 5 valores: {vetor[:5]}")
    return vetor

if __name__ == "__main__":
    testar_embedding()
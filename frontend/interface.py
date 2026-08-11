# frontend/interface.py
"""
Interface gráfica para o sistema RAG com TinyLlama
Permite fazer upload de documentos e conversar com eles
"""

import streamlit as st
import requests
import json
import os
from datetime import datetime

# ==========================================
# 1. CONFIGURAÇÃO DA PÁGINA
# ==========================================

st.set_page_config(
    page_title="Chat com Documentos - TinyLlama",
    page_icon="🦙",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# 2. ESTILO PERSONALIZADO
# ==========================================

st.markdown("""
<style>
    .titulo-principal {
        color: #FF6B35;
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
    }
    .subtitulo {
        color: #666;
        font-size: 1.1rem;
        text-align: center;
        margin-bottom: 2rem;
    }
    .badge-gratis {
        background-color: #34A853;
        color: white;
        padding: 0.2rem 0.8rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: bold;
    }
    .badge-local {
        background-color: #FF6B35;
        color: white;
        padding: 0.2rem 0.8rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: bold;
    }
    .resposta-destaque {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #FF6B35;
    }
    .card-info {
        background-color: #e8f5e9;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    .card-erro {
        background-color: #ffebee;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 5px solid #f44336;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. TÍTULO
# ==========================================

st.markdown('<p class="titulo-principal">🦙 Chat com Documentos - TinyLlama</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitulo">Faça perguntas sobre seus PDFs, CSVs e TXTs usando <span class="badge-gratis">GRÁTIS</span> <span class="badge-local">LOCAL</span> com TinyLlama</p>', unsafe_allow_html=True)

# ==========================================
# 4. BARRA LATERAL
# ==========================================

with st.sidebar:
    st.header("📤 Enviar Documento")
    st.caption("Suporta: PDF, TXT, CSV")
    
    # Upload
    arquivo = st.file_uploader(
        "Escolha um arquivo",
        type=['pdf', 'txt', 'csv'],
        help="Selecione um documento para fazer upload"
    )
    
    if arquivo and st.button("📥 Processar Documento", use_container_width=True):
        with st.spinner("⏳ Processando documento..."):
            try:
                files = {"arquivo": (arquivo.name, arquivo, arquivo.type)}
                response = requests.post(
                    "http://localhost:8000/upload",
                    files=files,
                    timeout=60
                )
                
                if response.status_code == 200:
                    dados = response.json()
                    st.success(f"✅ {dados['mensagem']}")
                    st.info(f"📊 {dados['total_chunks']} pedaços criados")
                    st.balloons()
                else:
                    st.error(f"❌ Erro: {response.text}")
                    
            except requests.exceptions.ConnectionError:
                st.error("❌ Não foi possível conectar à API. Verifique se ela está rodando em http://localhost:8000")
            except requests.exceptions.Timeout:
                st.error("⏰ Tempo limite excedido. O documento pode ser muito grande.")
            except Exception as e:
                st.error(f"❌ Erro: {str(e)}")
    
    st.divider()
    
    # ==========================================
    # 5. LISTA DE DOCUMENTOS
    # ==========================================
    
    st.header("📄 Documentos Carregados")
    
    if st.button("🔄 Atualizar Lista", use_container_width=True):
        try:
            response = requests.get("http://localhost:8000/documentos", timeout=10)
            
            if response.status_code == 200:
                docs = response.json()
                if docs:
                    for doc in docs:
                        with st.container():
                            st.write(f"📎 **{doc['nome']}**")
                            st.caption(f"Páginas: {doc['total_paginas']} | Chunks: {doc['quantidade_chunks']}")
                            st.caption(f"📅 {doc['data_upload'][:10]}")
                            st.divider()
                else:
                    st.info("📭 Nenhum documento carregado ainda")
            else:
                st.error("❌ Erro ao buscar documentos")
                
        except requests.exceptions.ConnectionError:
            st.error("❌ API não está rodando")
        except Exception as e:
            st.error(f"❌ Erro: {str(e)}")
    
    st.divider()
    
    # ==========================================
    # 6. STATUS DO SISTEMA
    # ==========================================
    
    st.header("🔮 Status do Sistema")
    
    try:
        # Testa a API
        response = requests.get("http://localhost:8000/status", timeout=5)
        
        if response.status_code == 200:
            status = response.json()
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Status", "🟢 Online" if status['status'] == 'online' else "🔴 Offline")
                st.metric("Chunks", status.get('total_chunks', 0))
            with col2:
                st.metric("Modelo", "TinyLlama")
                st.metric("Ollama", "🟢 Rodando" if status.get('ollama_rodando') else "🔴 Parado")
                
            # Verifica se o Ollama está configurado
            if not status.get('ollama_rodando'):
                st.warning("⚠️ Ollama não está rodando. Inicie com: ollama serve")
        else:
            st.error("❌ Erro ao obter status da API")
            
    except requests.exceptions.ConnectionError:
        st.error("❌ API não está rodando. Execute:")
        st.code("uvicorn aplicacao.principal:app --reload", language="bash")
    except Exception as e:
        st.error(f"❌ Erro: {str(e)}")
    
    st.divider()
    
    # ==========================================
    # 7. LIMPAR DADOS
    # ==========================================
    
    if st.button("🗑️ Limpar Todos os Dados", use_container_width=True):
        try:
            response = requests.delete("http://localhost:8000/limpar", timeout=10)
            if response.status_code == 200:
                st.success("✅ Todos os dados foram limpos!")
                st.rerun()
            else:
                st.error("❌ Erro ao limpar dados")
        except:
            st.error("❌ Erro ao conectar à API")

# ==========================================
# 8. ÁREA PRINCIPAL - CHAT
# ==========================================

st.header("💬 Chat com seus Documentos")

# Inicializa o histórico de mensagens
if "mensagens" not in st.session_state:
    st.session_state.mensagens = [
        {
            "role": "assistant", 
            "content": "🦙 Olá! Envie um documento (PDF, TXT ou CSV) e depois faça perguntas sobre ele. Estou usando o TinyLlama rodando localmente no seu computador!"
        }
    ]

# ==========================================
# 9. EXIBIR HISTÓRICO DE MENSAGENS
# ==========================================

for mensagem in st.session_state.mensagens:
    with st.chat_message(mensagem["role"]):
        st.markdown(mensagem["content"])
        
        # Se tiver fontes, exibe
        if "fontes" in mensagem and mensagem["fontes"]:
            with st.expander("📚 Fontes utilizadas"):
                for i, fonte in enumerate(mensagem["fontes"], 1):
                    st.write(f"{i}. {fonte}")

# ==========================================
# 10. INPUT DO USUÁRIO
# ==========================================

if pergunta := st.chat_input("Digite sua pergunta sobre os documentos..."):
    
    # Adiciona a pergunta ao histórico
    st.session_state.mensagens.append({"role": "user", "content": pergunta})
    
    # Exibe a pergunta
    with st.chat_message("user"):
        st.markdown(pergunta)
    
    # ==========================================
    # 11. PROCESSAR PERGUNTA
    # ==========================================
    
    with st.chat_message("assistant"):
        with st.spinner("🦙 Pensando com TinyLlama..."):
            try:
                # Envia para a API
                response = requests.post(
                    "http://localhost:8000/perguntar",
                    json={"pergunta": pergunta, "quantidade_resultados": 5},
                    timeout=120  # 2 minutos para o TinyLlama pensar
                )
                
                if response.status_code == 200:
                    dados = response.json()
                    
                    # Exibe a resposta
                    st.markdown(dados["resposta"])
                    
                    # Exibe fontes se tiver
                    if dados.get("fontes"):
                        with st.expander(f"📚 Fontes utilizadas ({len(dados['fontes'])} documentos)"):
                            for i, fonte in enumerate(dados["fontes"], 1):
                                st.write(f"{i}. {fonte}")
                    
                    # Salva no histórico
                    st.session_state.mensagens.append({
                        "role": "assistant",
                        "content": dados["resposta"],
                        "fontes": dados.get("fontes", [])
                    })
                    
                elif response.status_code == 422:
                    st.error("❌ Erro de validação. Verifique sua pergunta.")
                else:
                    st.error(f"❌ Erro na API: {response.text}")
                    
            except requests.exceptions.ConnectionError:
                st.error("❌ Não foi possível conectar à API. Verifique se está rodando.")
                st.code("uvicorn aplicacao.principal:app --reload", language="bash")
                
            except requests.exceptions.Timeout:
                st.error("⏰ O TinyLlama demorou muito para responder. Tente uma pergunta mais simples.")
                
            except Exception as e:
                st.error(f"❌ Erro inesperado: {str(e)}")


st.divider()
st.caption("🦙 Sistema RAG com TinyLlama - Processamento local e gratuito | Desenvolvido para estágio em IA/DS")
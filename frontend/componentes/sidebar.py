import streamlit as st
import requests

def render_sidebar():
    """Renderiza a barra lateral completa"""
    
    with st.sidebar:
        st.header(" Enviar Documento")
        st.caption("Suporta: PDF, TXT, CSV")
        
        # Upload
        arquivo = st.file_uploader(
            "Escolha um arquivo",
            type=['pdf', 'txt', 'csv']
        )
        
        if arquivo and st.button(" Processar", use_container_width=True):
            _processar_upload(arquivo)
        
        st.divider()
        
        st.header(" Documentos")
        if st.button(" Atualizar", use_container_width=True):
            _listar_documentos()
        
        st.divider()
  
        st.header(" Status")
        _mostrar_status()
        
        st.divider()

        if st.button(" Limpar Dados", use_container_width=True):
            _limpar_dados()

def _processar_upload(arquivo):
    """Processa o upload do documento"""
    with st.spinner(" Processando..."):
        try:
            files = {"arquivo": (arquivo.name, arquivo, arquivo.type)}
            response = requests.post(
                "http://localhost:8000/upload",
                files=files,
                timeout=60
            )
            
            if response.status_code == 200:
                dados = response.json()
                st.success(f" {dados['mensagem']}")
                st.info(f" {dados['total_chunks']} chunks criados")
                st.balloons()
            else:
                st.error(f" Erro: {response.text}")
                
        except requests.exceptions.ConnectionError:
            st.error(" API não está rodando")
        except Exception as e:
            st.error(f" Erro: {str(e)}")

def _listar_documentos():
    """Lista os documentos carregados"""
    try:
        response = requests.get("http://localhost:8000/documentos", timeout=10)
        if response.status_code == 200:
            docs = response.json()
            if docs:
                for doc in docs:
                    with st.container():
                        st.write(f"📎 **{doc['nome']}**")
                        st.caption(f"Páginas: {doc['total_paginas']} | Chunks: {doc['quantidade_chunks']}")
                        st.divider()
            else:
                st.info(" Nenhum documento")
        else:
            st.error(" Erro ao buscar")
    except:
        st.error(" API não está rodando")

def _mostrar_status():
    """Mostra o status do sistema"""
    try:
        response = requests.get("http://localhost:8000/status", timeout=5)
        if response.status_code == 200:
            status = response.json()
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Status", " Online" if status['status'] == 'online' else " Offline")
                st.metric("Chunks", status.get('total_chunks', 0))
            with col2:
                st.metric("Modelo", "TinyLlama")
                st.metric("Ollama", " Rodando" if status.get('ollama_rodando') else " Parado")
                
            if not status.get('ollama_rodando'):
                st.warning(" Ollama parado. Execute: ollama serve")
    except:
        st.error(" API não está rodando")
        st.code("uvicorn aplicacao.main:app --reload")

def _limpar_dados():
    """Limpa todos os dados"""
    try:
        response = requests.delete("http://localhost:8000/limpar", timeout=10)
        if response.status_code == 200:
            st.success(" Dados limpos!")
            st.rerun()
        else:
            st.error(" Erro ao limpar")
    except:
        st.error(" Erro ao conectar")
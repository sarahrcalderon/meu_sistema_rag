"""
Interface gráfica para o sistema RAG com TinyLlama
"""

import streamlit as st
from componentes.sidebar import render_sidebar
from componentes.chat import render_chat


st.set_page_config(
    page_title="Chat com Documentos - TinyLlama",
    page_icon="🦙",
    layout="wide",
    initial_sidebar_state="expanded"
)


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
</style>
""", unsafe_allow_html=True)


st.markdown('<p class="titulo-principal">🦙 Chat com Documentos - TinyLlama</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitulo">Faça perguntas sobre seus PDFs, CSVs e TXTs usando <span class="badge-gratis">GRÁTIS</span> <span class="badge-local">LOCAL</span> com TinyLlama</p>', unsafe_allow_html=True)


render_sidebar()
render_chat()
#  Sistema RAG com TinyLlama

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.0-green.svg)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.29.0-red.svg)](https://streamlit.io/)
[![Ollama](https://img.shields.io/badge/Ollama-TinyLlama-orange.svg)](https://ollama.ai/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](http://makeapullrequest.com)

##  Sobre o Projeto

Sistema de Chat com Documentos usando **RAG (Retrieval-Augmented Generation)** com **TinyLlama** rodando localmente através do **Ollama**. Este projeto foi desenvolvido como portfólio para estágio em Inteligência Artificial e Ciência de Dados.

###  Objetivos do Projeto

- ✅ Demonstrar conhecimentos em **Python para IA e Ciência de Dados**
- ✅ Implementar **RAG** com banco de dados **vetorial** e **SQL**
- ✅ Integrar com **APIs** usando **FastAPI**
- ✅ Utilizar **IA Generativa** com **Prompt Engineering** (Chain-of-Thought e Few-Shot)
- ✅ Criar uma interface amigável com **Streamlit**
- ✅ Manter tudo **100% gratuito e local**

###  Requisitos Atendidos

| Requisito | Tecnologia Utilizada |
|-----------|---------------------|
| **SQL** | SQLite + SQLAlchemy |
| **Banco Vetorial** | ChromaDB |
| **Integração via API** | FastAPI + Uvicorn |
| **Framework** | Streamlit, FastAPI |
| **Python IA** | Sentence-Transformers, PyTorch |
| **IA Generativa** | TinyLlama (Ollama) |
| **Prompt Engineering** | Chain-of-Thought + Few-Shot |

---

##  Funcionalidades

-  **Upload de Documentos**: Suporte a PDF, TXT e CSV
- **Busca Semântica**: ChromaDB para encontrar informações relevantes
-  **Chat Inteligente**: TinyLlama para responder perguntas
-  **Prompt Engineering Avançado**: 
  - Chain-of-Thought (raciocínio passo a passo)
  - Few-Shot (exemplos antes da resposta)
-  **Interface Amigável**: Streamlit para fácil interação
-  **Métricas**: Status do sistema, quantidade de documentos
-  **100% Local e Gratuito**: Sem dependência de APIs pagas

---

##  Tecnologias Utilizadas

### Backend
- **FastAPI** - Framework para API
- **Uvicorn** - Servidor ASGI
- **SQLAlchemy** - ORM para SQL
- **SQLite** - Banco de dados relacional
- **ChromaDB** - Banco de dados vetorial
- **Sentence-Transformers** - Embeddings locais

### IA e Processamento
- **Ollama** - Servidor de modelos LLM
- **TinyLlama** - Modelo de linguagem (1.1B parâmetros)
- **PyTorch** - Framework de deep learning

### Frontend
- **Streamlit** - Interface web interativa
- **Requests** - Comunicação com API

---



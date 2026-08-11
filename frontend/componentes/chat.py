import streamlit as st
import requests

def render_chat():
    """Renderiza a área de chat"""
    
    st.header("Chat com seus Documentos")
    

    if "mensagens" not in st.session_state:
        st.session_state.mensagens = [
            {
                "role": "assistant",
                "content": " Olá! Envie um documento e faça perguntas sobre ele. Uso o TinyLlama rodando localmente!"
            }
        ]
    
    # Exibe histórico
    for mensagem in st.session_state.mensagens:
        with st.chat_message(mensagem["role"]):
            st.markdown(mensagem["content"])
            if "fontes" in mensagem and mensagem["fontes"]:
                with st.expander(" Fontes"):
                    for i, fonte in enumerate(mensagem["fontes"], 1):
                        st.write(f"{i}. {fonte}")

    if pergunta := st.chat_input("Digite sua pergunta..."):
        _processar_pergunta(pergunta)

def _processar_pergunta(pergunta):
    """Processa uma pergunta do usuário"""
    
    # Adiciona ao histórico
    st.session_state.mensagens.append({"role": "user", "content": pergunta})
    
    with st.chat_message("user"):
        st.markdown(pergunta)
    
    with st.chat_message("assistant"):
        with st.spinner(" Pensando com TinyLlama..."):
            try:
                response = requests.post(
                    "http://localhost:8000/perguntar",
                    json={"pergunta": pergunta, "quantidade_resultados": 5},
                    timeout=120
                )
                
                if response.status_code == 200:
                    dados = response.json()
                    st.markdown(dados["resposta"])
                    
                    if dados.get("fontes"):
                        with st.expander(f" Fontes ({len(dados['fontes'])})"):
                            for i, fonte in enumerate(dados["fontes"], 1):
                                st.write(f"{i}. {fonte}")
                    
                    st.session_state.mensagens.append({
                        "role": "assistant",
                        "content": dados["resposta"],
                        "fontes": dados.get("fontes", [])
                    })
                else:
                    st.error(f" Erro: {response.text}")
                    
            except requests.exceptions.ConnectionError:
                st.error(" API não está rodando")
                st.code("uvicorn aplicacao.main:app --reload")
            except requests.exceptions.Timeout:
                st.error(" TinyLlama demorou muito. Tente uma pergunta mais simples.")
            except Exception as e:
                st.error(f" Erro: {str(e)}")
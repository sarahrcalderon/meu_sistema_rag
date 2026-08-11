"""
Serviço para comunicação com o Ollama
"""

import requests
import json
from typing import Optional, Dict, Any
from ..core.config import config
from ..utils.logger import log_info, log_erro, log_debug

class OllamaService:
    """
    Cliente para interagir com a API do Ollama
    """
    
    def __init__(self):
        self.url = config.OLLAMA_URL
        self.modelo = config.MODELO_OLLAMA
        self.timeout = config.TIMEOUT
        
    def verificar_servidor(self) -> bool:
        """
        Verifica se o Ollama está rodando
        
        Retorna:
        - True se estiver rodando, False caso contrário
        """
        try:
            resposta = requests.get(
                f"{self.url}/api/tags",
                timeout=5
            )
            
            if resposta.status_code == 200:
                dados = resposta.json()
                modelos = [m['name'] for m in dados.get('models', [])]
                
                # Verifica se o modelo está disponível
                if self.modelo in modelos or any(self.modelo in m for m in modelos):
                    log_info(f"✅ Ollama rodando com modelo '{self.modelo}'")
                    return True
                else:
                    log_warning(f"Modelo '{self.modelo}' não encontrado")
                    log_info(f"Modelos disponíveis: {modelos}")
                    return False
                    
            return False
            
        except requests.exceptions.ConnectionError:
            log_erro(" Ollama não está rodando!")
            return False
        except Exception as erro:
            log_erro(f"Erro ao verificar Ollama", erro)
            return False
    
    def gerar_resposta(self, prompt: str) -> str:
        """
        Gera uma resposta usando o Ollama
        
        Parâmetros:
        - prompt: Texto com a pergunta
        
        Retorna:
        - Resposta gerada
        """
        if not self.verificar_servidor():
            return self._mensagem_erro_servidor()
        
        try:
            payload = {
                "model": self.modelo,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": config.TEMPERATURA,
                    "top_p": 0.9,
                    "top_k": 40,
                    "num_predict": config.MAX_TOKENS,
                    "stop": ["\n\n\n"]
                }
            }
            
            log_debug(f"Enviando prompt para Ollama: {prompt[:100]}...")
            
            resposta = requests.post(
                f"{self.url}/api/generate",
                json=payload,
                timeout=self.timeout
            )
            
            if resposta.status_code == 200:
                dados = resposta.json()
                texto = dados.get('response', '').strip()
                
                if not texto:
                    return "Não foi possível gerar uma resposta. Tente reformular sua pergunta."
                
                log_debug(f"Resposta recebida: {texto[:100]}...")
                return texto
            else:
                log_erro(f"Erro no Ollama: {resposta.status_code}")
                return f"Erro no Ollama: {resposta.status_code}"
                
        except requests.exceptions.Timeout:
            log_erro("Timeout ao chamar Ollama")
            return " O TinyLlama demorou muito para responder. Tente uma pergunta mais simples."
        except Exception as erro:
            log_erro("Erro ao chamar Ollama", erro)
            return f" Erro ao gerar resposta: {str(erro)}"
    
    def listar_modelos(self) -> list:
        """Lista os modelos disponíveis no Ollama"""
        try:
            resposta = requests.get(f"{self.url}/api/tags", timeout=5)
            if resposta.status_code == 200:
                dados = resposta.json()
                return [m['name'] for m in dados.get('models', [])]
            return []
        except:
            return []
    
    def _mensagem_erro_servidor(self) -> str:
        """Mensagem de erro quando o Ollama não está rodando"""
        return """
         Ollama/TinyLlama não está disponível!
        
        Para resolver:
        1. Inicie o Ollama: `ollama serve`
        2. Baixe o TinyLlama: `ollama pull tinyllama`
        3. Verifique: `ollama list`
        """

ollama_service = OllamaService()
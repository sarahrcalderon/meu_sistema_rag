import requests
from ..core.config import config

class OllamaService:
    """
    Cliente para interagir com a API do Ollama
    """
    
    def __init__(self):
        self.url = config.OLLAMA_URL
        self.modelo = config.MODELO_OLLAMA 
        self.timeout = 120
        
    def verificar_servidor(self) -> bool:
        """Verifica se o Ollama está rodando"""
        try:
            resposta = requests.get(f"{self.url}/api/tags", timeout=5)
            
            if resposta.status_code == 200:
                dados = resposta.json()
                modelos = [m['name'] for m in dados.get('models', [])]
                
                if self.modelo in modelos or any(self.modelo in m for m in modelos):
                    print(f" Ollama rodando com modelo '{self.modelo}'")
                    return True
                else:
                    print(f" Modelo '{self.modelo}' não encontrado")
                    print(f"   Modelos disponíveis: {modelos}")
                    return False
            return False
        except:
            return False
    
    def gerar_resposta(self, prompt: str) -> str:
        """Gera uma resposta usando o Llama 3.2"""
        if not self.verificar_servidor():
            return " Ollama/Llama 3.2 não está disponível!"
        
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
                }
            }
            
            resposta = requests.post(
                f"{self.url}/api/generate",
                json=payload,
                timeout=self.timeout
            )
            
            if resposta.status_code == 200:
                dados = resposta.json()
                texto = dados.get('response', '').strip()
                return texto if texto else "Não foi possível gerar uma resposta."
            else:
                return f"Erro no Ollama: {resposta.status_code}"
                
        except Exception as erro:
            return f" Erro: {str(erro)}"
    
    def listar_modelos(self) -> list:
        """Lista os modelos disponíveis"""
        try:
            resposta = requests.get(f"{self.url}/api/tags", timeout=5)
            if resposta.status_code == 200:
                dados = resposta.json()
                return [m['name'] for m in dados.get('models', [])]
            return []
        except:
            return []

ollama_service = OllamaService()
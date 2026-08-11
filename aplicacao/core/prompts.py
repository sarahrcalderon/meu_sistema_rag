import requests
import os
from dotenv import load_dotenv

load_dotenv()

URL_OLLAMA = os.getenv('OLLAMA_URL', 'http://localhost:11434')
MODELO = os.getenv('MODELO_OLLAMA', 'llama3.2') 
TEMPERATURA = float(os.getenv('TEMPERATURA', 0.3))
MAX_TOKENS = int(os.getenv('MAX_TOKENS', 1000))

print(f"🦙 Usando modelo: {MODELO}")

def verificar_ollama():
    """
    Verifica se o Ollama está rodando e se o modelo está disponível
    """
    try:
        resposta = requests.get(f"{URL_OLLAMA}/api/tags", timeout=3)
        
        if resposta.status_code == 200:
            dados = resposta.json()
            modelos = [m['name'] for m in dados.get('models', [])]
            
            if MODELO in modelos or any(MODELO in m for m in modelos):
                print(f" Ollama rodando com modelo '{MODELO}'")
                return True
            else:
                print(f" Modelo '{MODELO}' não encontrado.")
                print(f"   Modelos disponíveis: {modelos}")
                print(f"   Baixe com: ollama pull {MODELO}")
                return False
        else:
            print(f"Erro ao conectar com Ollama: {resposta.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("Ollama não está rodando!")
        print("   Inicie com: ollama serve")
        return False
    except Exception as erro:
        print(f"Erro: {erro}")
        return False

def chamar_llama(prompt):
    """
    Chama o Llama 3.2 via Ollama
    """
    if not verificar_ollama():
        return """
         Ollama/Llama 3.2 não está disponível!
        
        Para resolver:
        1. Inicie o Ollama: ollama serve
        2. Baixe o Llama 3.2: ollama pull llama3.2
        3. Verifique: ollama list
        """
    
    try:
        payload = {
            "model": MODELO,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": TEMPERATURA,
                "top_p": 0.9,
                "top_k": 40,
                "num_predict": MAX_TOKENS,
            }
        }
        
        resposta = requests.post(
            f"{URL_OLLAMA}/api/generate",
            json=payload,
            timeout=120
        )
        
        if resposta.status_code == 200:
            dados = resposta.json()
            resposta_texto = dados.get('response', '').strip()
            
            if not resposta_texto:
                return "Não foi possível gerar uma resposta. Tente reformular sua pergunta."
            
            return resposta_texto
        else:
            return f"Erro no Ollama: {resposta.status_code}"
            
    except requests.exceptions.Timeout:
        return " O Llama 3.2 demorou muito para responder."
    except Exception as erro:
        return f" Erro ao chamar Llama 3.2: {str(erro)}"

def montar_prompt(pergunta, contexto):
    """
    Monta o prompt para o Llama 3.2
    """
    prompt = f"""<|start_header_id|>system<|end_header_id|>
Você é um assistente especialista em análise de documentos. 
Responda APENAS com base no contexto fornecido.
Seja objetivo e direto. Responda em português do Brasil.

<|eot_id|>
<|start_header_id|>user<|end_header_id|>
CONTEXTO:
{contexto}

PERGUNTA: {pergunta}

INSTRUÇÕES:
1. Se a informação não estiver no contexto, diga "Não encontrei essa informação no documento."
2. Seja objetivo e direto.
3. Responda em português do Brasil.

EXEMPLO:
Contexto: "Vendas: R$100 em janeiro, R$150 em fevereiro"
Pergunta: "Qual o valor total?"
Resposta: "O valor total é R$250"

AGORA RESPONDA A PERGUNTA:

<|eot_id|>
<|start_header_id|>assistant<|end_header_id|>
"""
    
    return prompt

def processar_pergunta(pergunta, contexto):
    """
    Processa uma pergunta usando Llama 3.2
    """
    print(f" Processando pergunta com {MODELO}...")
    print(f" Contexto: {len(contexto)} caracteres")
    
    prompt = montar_prompt(pergunta, contexto)
    resposta = chamar_llama(prompt)

    resposta = resposta.replace('<|start_header_id|>', '')
    resposta = resposta.replace('<|end_header_id|>', '')
    resposta = resposta.replace('<|eot_id|>', '')
    resposta = resposta.replace('assistant', '')
    resposta = resposta.strip()
    
    return resposta if resposta else "Não foi possível gerar uma resposta."

def testar_llama():
    """Testa se o Llama 3.2 está funcionando"""
    print("Testando Llama 3.2...")
    
    prompt = "<|start_header_id|>user<|end_header_id|>Diga 'OK'<|eot_id|><|start_header_id|>assistant<|end_header_id|>"
    resposta = chamar_llama(prompt)
    
    print(f"Resposta: {resposta}")
    
    if "OK" in resposta.upper() or "funcionando" in resposta.lower():
        print("Llama 3.2 está funcionando!")
        return True
    else:
        print("Llama 3.2 respondeu, mas não como esperado.")
        return False

if __name__ == "__main__":
    testar_llama()
# test_definitivo.py
"""
Teste completo do sistema
"""

import requests
import json

BASE_URL = "http://localhost:8000"

print("=" * 70)
print(" TESTE COMPLETO DO SISTEMA RAG")
print("=" * 70)

print("\n1️ LIMPANDO DADOS...")
try:
    response = requests.delete(f"{BASE_URL}/limpar")
    print(f" Dados limpos: {response.json()['mensagem']}")
except:
    print(" Não foi possível limpar dados")

# 2. Verificar status
print("\n2️ VERIFICANDO STATUS...")
response = requests.get(f"{BASE_URL}/status")
status = response.json()
print(f" Status: {status['status']}")
print(f"   Modelo: {status['modelo']}")
print(f"   Ollama: {' Rodando' if status['ollama_rodando'] else '❌ Parado'}")

# 3. Criar arquivo de teste
print("\n3️ CRIANDO ARQUIVO DE TESTE...")
conteudo = """Relatório de Vendas - Janeiro 2024

Produtos vendidos:
- Mouse: 150 unidades
- Teclado: 100 unidades
- Monitor: 50 unidades

Total de vendas: R$ 25.000,00
Produto mais vendido: Mouse

Faturamento por categoria:
- Periféricos: R$ 15.000,00
- Monitores: R$ 10.000,00
"""

with open("teste_final.txt", "w", encoding="utf-8") as f:
    f.write(conteudo)
print(" Arquivo criado: teste_final.txt")

# 4. Fazer upload
print("\n4️ FAZENDO UPLOAD...")
with open("teste_final.txt", "rb") as f:
    files = {"arquivo": ("teste_final.txt", f, "text/plain")}
    response = requests.post(f"{BASE_URL}/upload", files=files)
    
if response.status_code == 200:
    dados = response.json()
    print(f" {dados['mensagem']}")
    print(f"   ID: {dados['id_documento']}")
    print(f"   Chunks: {dados['total_chunks']}")
else:
    print(f" Erro: {response.text}")
    exit()

# 5. Fazer perguntas
print("\n5️ FAZENDO PERGUNTAS...")
print("-" * 50)

perguntas = [
    "Qual foi o total de vendas?",
    "Qual produto foi mais vendido?",
    "Quantos mouses foram vendidos?",
    "Qual foi o faturamento de periféricos?"
]

for pergunta in perguntas:
    print(f"\n PERGUNTA: {pergunta}")
    print("-" * 40)
    
    response = requests.post(
        f"{BASE_URL}/perguntar",
        json={"pergunta": pergunta, "quantidade_resultados": 3}
    )
    
    if response.status_code == 200:
        dados = response.json()
        print(f" RESPOSTA: {dados['resposta']}")
        print(f" Chunks utilizados: {dados['chunks_utilizados']}")
    else:
        print(f" Erro: {response.text}")

print("\n" + "=" * 70)
print(" TESTE CONCLUÍDO!")
print("=" * 70)
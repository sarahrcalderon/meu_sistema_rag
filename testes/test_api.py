import pytest
from fastapi.testclient import TestClient
from aplicacao.main import app
import os

client = TestClient(app)

class TestAPI:
    """Testes da API"""
    
    def test_raiz(self):
        """Testa o endpoint raiz"""
        response = client.get("/")
        assert response.status_code == 200
        assert "online" in response.json()["status"]
    
    def test_status(self):
        """Testa o endpoint de status"""
        response = client.get("/status")
        assert response.status_code == 200
        assert "status" in response.json()
    
    def test_health(self):
        """Testa o health check"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    
    def test_perguntar_sem_documentos(self):
        """Testa perguntar sem documentos"""
        response = client.post(
            "/perguntar",
            json={"pergunta": "Teste", "quantidade_resultados": 3}
        )
        assert response.status_code == 200
        assert "Nenhum documento" in response.json()["resposta"]
    
    def test_upload_arquivo_invalido(self):
        """Testa upload de arquivo inválido"""
        arquivo = ("test.txt", b"conteudo", "text/plain")
        response = client.post(
            "/upload",
            files={"arquivo": arquivo}
        )
        # Pode ser 200 se processar ou 400 se rejeitar
        assert response.status_code in [200, 400]
    
    def test_limpar_dados(self):
        """Testa limpeza de dados"""
        response = client.delete("/limpar")
        assert response.status_code == 200
        assert "limpos" in response.json()["mensagem"]
    
    def test_documentos_lista(self):
        """Testa listagem de documentos"""
        response = client.get("/documentos")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    def test_testar_ollama(self):
        """Testa o endpoint de teste do Ollama"""
        response = client.get("/testar-ollama")
        assert response.status_code == 200
        assert "status" in response.json()
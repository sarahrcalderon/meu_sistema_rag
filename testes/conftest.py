import pytest
import os
import sys
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

@pytest.fixture
def ambiente_teste():
    """Configura ambiente para testes"""
    os.environ["CAMINHO_BANCO_SQL"] = "sqlite:///:memory:"
    os.environ["CAMINHO_BANCO_VETORIAL"] = "./testes/data/chroma_db"
    
    yield

    import shutil
    if os.path.exists("./testes/data"):
        shutil.rmtree("./testes/data")
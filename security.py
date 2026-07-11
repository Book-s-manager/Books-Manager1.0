import hashlib   # funções hash criptográficas (embutido no Python)
import os        # acesso a variáveis de ambiente (embutido no Python)
from dotenv import load_dotenv  # lê o arquivo .env e carrega no os.environ
from fastapi import Header, HTTPException

load_dotenv()  # carrega as variáveis do .env para o processo Python

# Lê o hash da API Key do ambiente — None se a variável não existir
_API_KEY_HASH = os.getenv("API_KEY_HASH")


def verificar_api_key(x_api_key: str = Header(...)):
    """Dependência FastAPI: verifica se o header X-API-Key é válido.

    Header(...) torna o campo obrigatório — FastAPI retorna 422 se ausente.
    Se a chave não bater com o hash armazenado, retornamos 401 Unauthorized.
    """
    if _API_KEY_HASH is None:
        # Servidor mal configurado — avisa o desenvolvedor, não o cliente
        raise HTTPException(status_code=500,
                            detail="API_KEY_HASH não configurada no servidor")

    # Hasheia a chave recebida e compara com o hash armazenado
    hash_recebido = hashlib.sha256(x_api_key.encode()).hexdigest()

    if hash_recebido != _API_KEY_HASH:
        raise HTTPException(status_code=401,
                            detail="API Key inválida")
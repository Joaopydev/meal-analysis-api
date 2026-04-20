import os
from datetime import datetime, timedelta, timezone

import jwt
from dotenv import load_dotenv

load_dotenv()

def load_pem_key(key_env_var: str) -> bytes:
    """
    Carrega a chave PEM de uma variável de ambiente e a formata
    corretamente para PyJWT, garantindo que seja um objeto bytes.
    """
    key_str = os.getenv(key_env_var)
    if not key_str:
        raise ValueError(f"Environment variable {key_env_var} not found.")
    
    # Esta linha é crucial para restaurar as quebras de linha em chaves PEM
    key_str = key_str.strip().replace('\\n', '\n').replace('"', '')
    
    return key_str.encode('utf-8')

def signin_access_token(user_id: str):
    now = datetime.now(timezone.utc)
    payload = {
        "user_id": str(user_id),
        "iss": os.getenv("ISSUER"),
        "iat": int(now.timestamp()),
        "exp": now + timedelta(days=3)
    }
    
    private_key = load_pem_key("SECRET_JWT_PRIVATE_KEY")

    access_token = jwt.encode(
        payload=payload,
        key=private_key,
        algorithm="RS256",
    )
    return access_token


def validate_access_token(token_jwt: str):
    try:
        public_key = load_pem_key("SECRET_JWT_PUBLIC_KEY")
        payload_data = jwt.decode(
            jwt=token_jwt,
            key=public_key,
            algorithms="RS256",
            issuer=os.getenv("ISSUER")
        )
        return payload_data.get("user_id")
    except:
        return None
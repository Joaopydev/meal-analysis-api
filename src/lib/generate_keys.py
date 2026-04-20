from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend


# --- 1. Geração das Chaves RSA (Privada e Pública) ---

def generate_rsa_key_pair():
    """Gera um par de chaves RSA (2048 bits) para RS256."""
    # Geração da chave privada
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )

    # Serialização da chave privada (formato PEM)
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )

    # Serialização da chave pública (formato PEM)
    public_key = private_key.public_key()
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    return private_pem.decode('utf-8'), public_pem.decode('utf-8')

private, public = generate_rsa_key_pair()
print(private)
print("/n")
print("/n")
print("/n")
print("/n")
print(public)
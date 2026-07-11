import secrets, hashlib

chave  = secrets.token_hex(32)         # chave que o cliente vai usar
hashed = hashlib.sha256(chave.encode()).hexdigest()  # hash que o servidor guarda

print("Chave (guarde você):", chave)
print("Hash  (vai no .env):", hashed)
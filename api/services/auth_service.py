from db import db
from passlib.hash import bcrypt

# Buscar usuario por email en la tabla 'usuario'
async def get_user_by_email(email: str):
    await db.connect()
    user = await db.usuario.find_unique(where={"email": email})
    await db.disconnect()
    return user

# Verificar password hash bcrypt
def verify_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.verify(plain, hashed)
    except Exception:
        return False

# Crear hash (por si luego hacemos registro)
def hash_password(plain: str) -> str:
    return bcrypt.hash(plain)

import os
import subprocess
from prisma import Prisma

# 🚀 Verificar que el cliente Prisma existe; si no, generarlo automáticamente
try:
    client_dir = os.path.join(os.getcwd(), ".prisma")
    if not os.path.exists(client_dir):
        print("⚙️ Prisma client not found. Generating...")
        subprocess.run(
            ["python", "-m", "prisma", "generate"],
            check=True,
        )
        print("✅ Prisma client generated successfully.")
except Exception as e:
    print("❌ Failed to generate Prisma client:", e)

# Inicializar cliente
db = Prisma()

async def connect_db():
    if not db.is_connected():
        await db.connect()

async def disconnect_db():
    if db.is_connected():
        await db.disconnect()

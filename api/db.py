import os
import subprocess
from prisma import Prisma


# 🚀 Verificar que el cliente Prisma existe; si no, generarlo automáticamente
try:
    client_dir = os.path.join(os.getcwd(), ".prisma")
    if not os.path.exists(client_dir):
        print("⚙️ Prisma client not found. Generating...")
        # Intentar con prisma CLI directamente
        try:
            result = subprocess.run(
                ["prisma", "generate"],
                cwd=os.path.join(os.getcwd(), "prisma"),
                check=True,
                capture_output=True,
                text=True
            )
            print("✅ Prisma client generated successfully.")
        except (subprocess.CalledProcessError, FileNotFoundError):
            # Si falla, intentar con python -m prisma
            try:
                import sys
                result = subprocess.run(
                    [sys.executable, "-m", "prisma", "generate"],
                    cwd=os.path.join(os.getcwd(), "prisma"),
                    check=True,
                    capture_output=True,
                    text=True
                )
                print("✅ Prisma client generated successfully.")
            except Exception as e2:
                print(f"⚠️ Warning: Could not auto-generate Prisma client: {e2}")
                print("💡 Please run manually: cd prisma && prisma generate")
except Exception as e:
    print(f"⚠️ Warning: Prisma client check failed: {e}")
    print("💡 If you see Prisma errors, run: cd prisma && prisma generate")

# Inicializar cliente
db = Prisma()

async def connect_db():
    if not db.is_connected():
        await db.connect()

async def disconnect_db():
    if db.is_connected():
        await db.disconnect()

# 🛠️ Scripts - Granja del Cerdo API

Esta carpeta contiene scripts utilitarios para desarrollo, testing y mantenimiento del proyecto.

## 📁 Estructura

```
scripts/
├── README.md          # Este archivo
└── temp/              # Scripts temporales (ignorados por Git)
```

---

## 📋 Carpetas

### `temp/`
**Scripts temporales y de prueba**

Esta carpeta está configurada en `.gitignore` para no subir scripts temporales al repositorio.

**Uso recomendado**:
- Scripts de debugging puntual
- Análisis de datos específicos
- Pruebas rápidas
- Experimentos temporales

**Ejemplos de scripts temporales**:
```python
# temp/analizar_lote_especifico.py
# temp/test_feature_extraction.py
# temp/debug_prediccion.py
# temp/verificar_costos.py
```

**⚠️ Importante**: Los archivos en `temp/` NO se subirán a Git automáticamente.

---

## 🔧 Scripts Permanentes (Futuros)

Cuando crees scripts que sean útiles de forma permanente, colócalos directamente en la carpeta `scripts/` (no en `temp/`).

**Ejemplos de scripts permanentes**:
- Scripts de migración de datos
- Herramientas de mantenimiento
- Scripts de backup
- Utilidades de desarrollo

---

## 📝 Convenciones

### Nombres de Archivos
- Usar snake_case: `mi_script_util.py`
- Nombres descriptivos: `poblar_datos_prueba.py`
- Prefijos según propósito:
  - `test_*.py` - Scripts de testing
  - `debug_*.py` - Scripts de debugging
  - `migrate_*.py` - Scripts de migración
  - `backup_*.py` - Scripts de backup

### Estructura de Script
```python
#!/usr/bin/env python3
"""
Descripción breve del script.

Uso:
    python script_name.py [argumentos]

Ejemplo:
    python poblar_datos.py --cantidad 100
"""

import sys
from pathlib import Path

# Agregar api al path si es necesario
api_dir = Path(__file__).parent.parent / "api"
sys.path.insert(0, str(api_dir))

def main():
    """Función principal del script."""
    pass

if __name__ == "__main__":
    main()
```

---

## 🚀 Ejemplos de Uso

### Script Temporal de Debugging
```bash
# Crear script temporal
cd scripts/temp
notepad debug_lote.py

# Ejecutar
python debug_lote.py
```

### Script Permanente de Utilidad
```bash
# Crear script permanente
cd scripts
notepad backup_database.py

# Ejecutar
python backup_database.py
```

---

## ⚙️ Configuración

### Variables de Entorno
Los scripts deben cargar variables de entorno desde el `.env` en la raíz:

```python
from pathlib import Path
from dotenv import load_dotenv

# Cargar .env desde raíz del proyecto
root_dir = Path(__file__).parent.parent
env_path = root_dir / ".env"
load_dotenv(env_path)
```

### Conexión a Base de Datos
```python
import sys
from pathlib import Path

# Agregar api al path
api_dir = Path(__file__).parent.parent / "api"
sys.path.insert(0, str(api_dir))

from db import db
import asyncio

async def mi_script():
    await db.connect()
    try:
        # Tu código aquí
        pass
    finally:
        await db.disconnect()

if __name__ == "__main__":
    asyncio.run(mi_script())
```

---

## 📚 Scripts Útiles Sugeridos

### 1. Backup de Base de Datos
```python
# scripts/backup_database.py
# Crear backup de la base de datos PostgreSQL
```

### 2. Verificar Integridad de Datos
```python
# scripts/verificar_datos.py
# Verificar que todos los lotes tengan costos y producción
```

### 3. Generar Reporte
```python
# scripts/generar_reporte.py
# Generar reporte mensual de lotes y ganancias
```

### 4. Limpiar Datos Antiguos
```python
# scripts/limpiar_datos_antiguos.py
# Eliminar lotes y costos de más de X meses
```

---

## 🔒 Seguridad

### Scripts Temporales
- ✅ Nunca incluir credenciales hardcodeadas
- ✅ Usar variables de entorno
- ✅ No subir a Git (ya configurado en `.gitignore`)

### Scripts Permanentes
- ✅ Documentar bien el propósito
- ✅ Incluir manejo de errores
- ✅ Validar inputs del usuario
- ✅ Hacer commit al repositorio

---

## 📞 Ayuda

Si tienes dudas sobre cómo crear o usar scripts:
1. Revisa los ejemplos en esta documentación
2. Consulta scripts existentes como referencia
3. Contacta al equipo de desarrollo

---

**Última actualización**: Enero 2026

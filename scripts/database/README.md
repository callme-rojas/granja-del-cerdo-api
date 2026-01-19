# Scripts de Base de Datos

Este directorio contiene scripts para poblar y gestionar la base de datos.

## 📋 Scripts Disponibles

### `poblar_feriados.py`
Pobla la tabla `Feriado` con los feriados de Bolivia 2026.

**Uso**:
```bash
# Desde la raíz del proyecto
python scripts/database/poblar_feriados.py
```

**Resultado**: 13 feriados creados en la BD

---

### `poblar_gastos_mensuales.py`
Pobla la tabla `GastoMensual` con gastos mensuales de ejemplo y crea tipos de costo si no existen.

**Uso**:
```bash
# Desde la raíz del proyecto
python scripts/database/poblar_gastos_mensuales.py

# Calcular prorrateo para un lote específico
python scripts/database/poblar_gastos_mensuales.py calcular <id_lote>
```

**Resultado**: 3 tipos de costo + 6 gastos mensuales creados

---

### `init_database.py`
Script de inicialización de base de datos (legacy).

---

### `init_database.sql`
Script SQL de inicialización (legacy).

---

## ⚠️ Importante

Todos los scripts deben ejecutarse desde la **raíz del proyecto** para que los imports funcionen correctamente.

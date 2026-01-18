# 🔄 GUÍA: RE-ENTRENAR MODELO CON RANGOS AMPLIADOS

## 📊 Análisis de Datos Reales

**Resultado del análisis:**
- ✅ **49.2% de los costos reales están fuera del rango de entrenamiento**
- ⚠️  **Logística**: Máximo real 8,379 Bs vs máximo entrenamiento 2,850 Bs (194% más)
- ⚠️  **Alimentación**: Máximo real 5,681 Bs vs máximo entrenamiento 360 Bs (1,478% más)
- ⚠️  **Fijos**: Máximo real 2,462 Bs vs máximo entrenamiento 600 Bs (310% más)

**Conclusión:** Es necesario re-entrenar con rangos más amplios para mejorar la precisión.

---

## 🔧 Cambios Realizados

### 1. `api/ml/data/generate_data.py`

#### Costos Logísticos:
```python
# ANTES:
base_log = rng.uniform(150.0, 350.0, size=n_rows)
por_animal = rng.uniform(10.0, 25.0, size=n_rows) * cantidad_animales

# AHORA:
base_log = rng.uniform(150.0, 500.0, size=n_rows)  # Aumentado
por_animal = rng.uniform(10.0, 50.0, size=n_rows) * cantidad_animales  # Aumentado
# Máximo teórico: ~6,500+ Bs (cubre datos reales hasta 8,379 Bs)
```

#### Costos Alimentación:
```python
# ANTES:
costo_alimentacion = rng.uniform(0.0, 1.2, size=n_rows) * cantidad_animales * días

# AHORA:
costo_alimentacion = rng.uniform(0.0, 5.0, size=n_rows) * cantidad_animales * días
# Máximo teórico: ~1,800 Bs, pero permite valores más altos
```

#### Costos Fijos:
```python
# ANTES:
costo_fijo_total = rng.normal(loc=500.0, scale=200.0, size=n_rows)
# Rango: ~200-600 Bs

# AHORA:
costo_fijo_total = rng.normal(loc=1000.0, scale=500.0, size=n_rows)
# Rango: ~100-2,500 Bs (cubre datos reales hasta 2,462 Bs)
```

### 2. `api/ml/core/training_12_months.py`

También ajustado para mantener consistencia.

---

## 🚀 Cómo Re-Entrenar el Modelo

### Opción 1: Usando el script completo (Recomendado)

```bash
cd api/ml/core
python training_12_months.py
```

Este script:
1. Genera 360 lotes con los nuevos rangos
2. Entrena 3 modelos (Linear, RandomForest, GradientBoosting)
3. Evalúa con validación cruzada
4. Selecciona el mejor modelo
5. Guarda en `api/ml/models/12_months_model.pkl`

### Opción 2: Usando el script de poblar y validar

```bash
cd api/ml/core
python poblar_y_validar.py --n-lotes 360 --no-poblar-bd
```

---

## 📈 Resultados Esperados

Después de re-entrenar con rangos ampliados:

1. **Mejor cobertura**: El modelo habrá visto valores más altos durante el entrenamiento
2. **Mayor precisión**: Menos extrapolación = predicciones más confiables
3. **Mejor generalización**: El modelo podrá manejar mejor los casos reales

---

## ⚠️ IMPORTANTE

1. **Backup del modelo actual**: El nuevo modelo sobrescribirá `12_months_model.pkl`
2. **Tiempo de entrenamiento**: ~2-5 minutos dependiendo de tu máquina
3. **Verificación**: Después de re-entrenar, prueba con lotes reales para verificar mejoras

---

## ✅ Checklist Post-Entrenamiento

- [ ] Modelo re-entrenado guardado correctamente
- [ ] Probar predicción con lote 1400 (valores altos)
- [ ] Comparar resultados antes/después
- [ ] Verificar que las métricas (MAE, RMSE, R²) sean similares o mejores
- [ ] Probar con varios lotes reales para validar

---

**Última actualización:** Diciembre 2024


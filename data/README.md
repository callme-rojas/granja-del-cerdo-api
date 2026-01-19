# Datos Generados

Este directorio contiene datasets y archivos de datos generados por el sistema.

## 📁 Archivos

### `dataset_xgboost_24_features.csv`
Dataset sintético con 2000 muestras y 24 features para entrenar el modelo XGBoost.

**Generado por**: `api/ml/data/generate_data.py`

---

### `analisis_documento.json`
Análisis estructurado del documento del proyecto de grado.

**Generado por**: `scripts/analysis/analizar_documento.py`

---

## 🔄 Regenerar Datos

Para regenerar el dataset:
```bash
cd api
python ml/data/generate_data.py --n 2000
```

El archivo se guardará automáticamente en `data/dataset_xgboost_24_features.csv`

# Modulo de Machine Learning - Sistema de Prediccion de Precios

## Estructura del Modulo

```
ml/
├── core/                    # Funcionalidades principales
│   ├── training_12_months.py    # Entrenamiento profesional
│   ├── compare_models.py        # Comparacion de algoritmos
│   └── evaluate_model.py        # Evaluacion de modelos
├── data/                    # Datasets y generacion
│   ├── generate_data.py         # Generacion de datos sinteticos
│   ├── synthetic_lotes.csv      # Dataset de lotes
│   └── synthetic_features.csv   # Dataset de features
├── models/                  # Modelos entrenados
│   ├── best_model.pkl           # Mejor modelo (3 algoritmos)
│   └── 12_months_model.pkl      # Mejor modelo (12 meses)
├── utils/                   # Utilidades
│   ├── train_model.py           # Entrenamiento basico
│   └── run_pipeline.py          # Pipeline completo
├── tests/                   # Pruebas
│   └── test_integration.py      # Pruebas de integracion
├── docs/                    # Documentacion
│   ├── README.md                # Documentacion tecnica
│   ├── RESUMEN_EJECUTIVO.md    # Resumen para defensa
│   └── dataset_12_meses.csv     # Dataset principal
└── README.md                # Este archivo
```

## Uso Rapido

### 1. Entrenar Modelo de 12 Meses
```bash
python core/training_12_months.py
```

### 2. Comparar 3 Algoritmos
```bash
python core/compare_models.py
```

### 3. Evaluar Modelo
```bash
python core/evaluate_model.py
```

### 4. Probar Integracion
```bash
python tests/test_integration.py
```

## Resultados Principales

- **Mejor Modelo**: LinearRegression (Según diseño académico)
- **MAE**: 0.461 Bs/kg
- **R² Score**: 0.931
- **Dataset**: 360 lotes (12 meses)
- **Algoritmos**: Solo los 3 del diseño académico

## Proximos Pasos

1. Integracion con backend
2. Pruebas con lotes reales
3. Validacion en produccion

## Soporte

Para preguntas tecnicas, revisar `docs/RESUMEN_EJECUTIVO.md`

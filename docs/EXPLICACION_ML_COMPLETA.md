# 🤖 EXPLICACIÓN COMPLETA DEL SISTEMA DE MACHINE LEARNING

## 📋 ÍNDICE
1. [Visión General del Flujo](#1-visión-general-del-flujo)
2. [Generación de Datos de Entrenamiento](#2-generación-de-datos-de-entrenamiento)
3. [Preparación de Features](#3-preparación-de-features)
4. [Entrenamiento del Modelo](#4-entrenamiento-del-modelo)
5. [Predicción en Tiempo Real](#5-predicción-en-tiempo-real)
6. [Componentes Técnicos](#6-componentes-técnicos)

---

## 1. VISIÓN GENERAL DEL FLUJO

```
┌─────────────────────────────────────────────────────────────┐
│                    FLUJO COMPLETO DEL ML                    │
└─────────────────────────────────────────────────────────────┘

FASE 1: ENTRENAMIENTO (Una vez, offline)
├── Generar 360 lotes sintéticos (12 meses)
├── Extraer 10 features de cada lote
├── Calcular precio_venta_final_kg (target)
├── Normalizar features con StandardScaler
├── Entrenar 3 modelos (Linear, RandomForest, GradientBoosting)
├── Evaluar con validación cruzada (K-Fold)
├── Seleccionar mejor modelo (menor MAE)
└── Guardar modelo + scaler en .pkl

FASE 2: PREDICCIÓN (Cada vez que se solicita)
├── Obtener datos del lote desde BD
├── Construir 10 features del lote
├── Normalizar features con el scaler guardado
├── Predecir precio con el modelo entrenado
└── Aplicar margen adicional si se solicita
```

---

## 2. GENERACIÓN DE DATOS DE ENTRENAMIENTO

**Archivo:** `api/ml/data/generate_data.py` → `generar_lote()`

### ¿Qué hace?
Genera 360 lotes sintéticos que simulan 12 meses de operación real.

### Proceso paso a paso:

#### 2.1. Generar características básicas
```python
cantidad_animales = 15-100 animales (aleatorio)
peso_promedio_entrada = 80-115 kg (distribución normal)
precio_compra_kg = 18-25 Bs/kg (uniforme)
duracion_estadia_dias = 1-3 días (discreta)
mes_adquisicion = 1-12 (estacionalidad)
```

#### 2.2. Calcular pesos y costos
```python
kilos_entrada = cantidad_animales × peso_promedio_entrada

# NUEVO: Ganancia de peso realista
ganancia_por_dia = 0.8-1.5 kg/cerdo/día (aleatorio)
ganancia_total = ganancia_por_dia × cantidad × días
kilos_salida = kilos_entrada + ganancia_total

# Costos logísticos (RANGOS AMPLIADOS)
costo_logistica = base (150-500 Bs) + por_animal (10-50 Bs/animal) + ruido
# Rango total: ~310 Bs (lote pequeño) hasta ~6,500 Bs (lote grande de 100 animales)

# Costos alimentación (solo si estadía > 1 día) - RANGOS AMPLIADOS
costo_alimentacion = cantidad × días × 0-5.0 Bs/día (60% probabilidad)
# Rango: 0 Bs hasta ~1,800 Bs (100 animales × 3 días × 5.0 Bs)

# Costos fijos - RANGOS AMPLIADOS
costo_fijo_total = 100-2,500 Bs (distribución normal, media=1000, desv=700)
```

**⚠️ IMPORTANTE: RANGOS DE ENTRENAMIENTO vs VALORES REALES**

Los rangos mostrados son los usados para **generar datos sintéticos** durante el entrenamiento. Sin embargo:

1. **El modelo puede manejar valores fuera del rango:**
   - La normalización (StandardScaler) transforma todos los valores a la misma escala
   - La regresión lineal puede **extrapolar** (predecir fuera del rango visto)
   - Pero la precisión puede disminuir cuanto más lejos esté del rango de entrenamiento

2. **Ejemplo práctico:**
   - Rango entrenamiento (nuevo): logística 150-6,500 Bs
   - Valor real: 864 Bs (dentro del rango) ✅
   - Valor real: 5,000 Bs (dentro del nuevo rango) ✅
   - Valor real: 8,000 Bs (fuera del rango) ⚠️ Funciona, pero menos preciso

3. **Recomendaciones:**
   - ✅ Valores dentro del rango: Máxima precisión
   - ⚠️ Valores ligeramente fuera: Funciona bien
   - ❌ Valores muy fuera: Considerar re-entrenar el modelo con datos más amplios

#### 2.3. Calcular precio de venta (TARGET)
```python
# 1. Costos adicionales por kg
costo_adicional_por_kg = (logística + alimentación) / kilos_salida

# 2. Costos fijos por kg
costo_fijo_por_kg = costo_fijo_total / kilos_salida

# 3. Margen según estacionalidad
if mes in [12, 1]:  # Alta demanda
    margen = 10-20%
elif mes in [5, 6]:  # Baja demanda
    margen = 3-10%
else:
    margen = 5-15%

# 4. Precio final
precio_base = precio_compra + costos_adicionales + costos_fijos
precio_venta_final_kg = precio_base × (1 + margen) + ruido_market
```

**Resultado:** DataFrame con 360 filas, cada una con:
- 10 features (inputs)
- 1 target: `precio_venta_final_kg` (output a predecir)

---

## 3. PREPARACIÓN DE FEATURES

**Archivo:** `api/ml/data/generate_data.py` → `construir_features()`

### Las 10 Features del Modelo:

```python
features = {
    1. "cantidad_animales": int,              # Nivel I
    2. "peso_promedio_entrada": float,        # Nivel I
    3. "precio_compra_kg": float,              # Nivel I
    4. "costo_logistica_total": float,         # Nivel II
    5. "costo_alimentacion_estadia": float,   # Nivel II
    6. "duracion_estadia_dias": int,          # Nivel II
    7. "mes_adquisicion": int,                # Nivel II
    8. "costo_total_lote": float,             # Feature Engineering (CTL)
    9. "peso_salida": float,                  # Feature adicional
    10. "costo_fijo_por_kg": float,           # Nivel III
}

# Feature Engineering: CTL (Costo Total por Lote)
costo_total_lote = compra_total + logística + alimentación
```

### ¿Por qué estas features?
- **Nivel I**: Características básicas del lote
- **Nivel II**: Costos operativos y contexto temporal
- **Nivel III**: Costos fijos distribuidos
- **CTL**: Feature engineering que concentra el 99.6% de la varianza económica

---

## 4. ENTRENAMIENTO DEL MODELO

**Archivo:** `api/ml/core/training_12_months.py`

### 4.1. División de Datos
```python
X = features (360 × 10)  # Matriz de features
y = target (360 × 1)      # Vector de precios

# División 80/20
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
# Resultado: 288 lotes para entrenar, 72 para probar
```

### 4.2. Normalización (StandardScaler)
```python
scaler = StandardScaler()
scaler.fit(X_train)  # Aprende media y desviación estándar

X_train_scaled = scaler.transform(X_train)  # Normaliza
X_test_scaled = scaler.transform(X_test)

# ¿Por qué normalizar?
# - Diferentes escalas: cantidad_animales (15-100) vs costo_total_lote (30,000+)
# - El modelo necesita valores en la misma escala
# - Fórmula: (valor - media) / desviación_estándar
```

### 4.3. Comparación de Modelos

Se entrenan 3 algoritmos diferentes:

#### A) Linear Regression
```python
model = LinearRegression()
model.fit(X_train_scaled, y_train)
# Fórmula aprendida: y = w₀ + w₁×x₁ + w₂×x₂ + ... + w₁₀×x₁₀
# Ventaja: Simple, rápido, interpretable
```

#### B) Random Forest Regressor
```python
model = RandomForestRegressor(n_estimators=100, max_depth=10)
model.fit(X_train_scaled, y_train)
# Ventaja: Captura relaciones no lineales, robusto
```

#### C) Gradient Boosting Regressor
```python
model = GradientBoostingRegressor(n_estimators=100, learning_rate=0.1)
model.fit(X_train_scaled, y_train)
# Ventaja: Secuencial, mejora iterativamente
```

### 4.4. Validación Cruzada (K-Fold)

**Archivo:** `api/ml/core/cross_validation.py`

```python
# Divide datos en 5 folds (subconjuntos)
Fold 1: Entrenar en [2,3,4,5], Probar en [1]
Fold 2: Entrenar en [1,3,4,5], Probar en [2]
Fold 3: Entrenar en [1,2,4,5], Probar en [3]
Fold 4: Entrenar en [1,2,3,5], Probar en [4]
Fold 5: Entrenar en [1,2,3,4], Probar en [5]

# Calcula MAE y RMSE en cada fold
# Promedia los resultados → métrica más confiable
```

**Ventajas:**
- Usa todos los datos para entrenar y probar
- Reduce riesgo de sobreajuste
- Métricas más confiables

### 4.5. Selección del Mejor Modelo - EXPLICACIÓN DETALLADA

```python
# Compara métricas de los 3 modelos
mejor_modelo = min(modelos, key=lambda m: m['mae'])

# Criterios:
# 1. Menor MAE (Mean Absolute Error)
# 2. Menor RMSE (Root Mean Squared Error)
# 3. Mayor R² (coeficiente de determinación)
# 4. Validación cruzada estable
```

#### ¿Qué significan estos criterios?

##### 1. MAE (Mean Absolute Error) - Error Absoluto Medio

**¿Qué es?**
El promedio de cuánto se equivoca el modelo en sus predicciones.

**Fórmula:**
```
MAE = (1/n) × Σ|precio_real - precio_predicho|
```

**Ejemplo práctico:**
Si predices 3 lotes:
- Lote 1: Real = 25.00, Predicho = 24.50 → Error = 0.50
- Lote 2: Real = 23.00, Predicho = 23.80 → Error = 0.80
- Lote 3: Real = 26.00, Predicho = 25.30 → Error = 0.70
- **MAE = (0.50 + 0.80 + 0.70) / 3 = 0.67 Bs/kg**

**Interpretación:**
- MAE = 0.467 Bs/kg significa que, en promedio, el modelo se equivoca por 0.47 Bs/kg
- **Menor es mejor**: Un MAE de 0.3 es mejor que uno de 0.5

**¿Por qué es importante?**
- Te dice directamente cuánto error puedes esperar
- Fácil de interpretar: "El modelo se equivoca en promedio por X Bs/kg"

##### 2. RMSE (Root Mean Squared Error) - Raíz del Error Cuadrático Medio

**¿Qué es?**
Similar al MAE, pero penaliza más los errores grandes.

**Fórmula:**
```
RMSE = √[(1/n) × Σ(precio_real - precio_predicho)²]
```

**Ejemplo práctico:**
Mismos 3 lotes:
- Lote 1: Error = 0.50 → Error² = 0.25
- Lote 2: Error = 0.80 → Error² = 0.64
- Lote 3: Error = 0.70 → Error² = 0.49
- **RMSE = √[(0.25 + 0.64 + 0.49) / 3] = √0.46 = 0.68 Bs/kg**

**Diferencia con MAE:**
- Si un error es muy grande (ej: 2.0 Bs/kg), el MAE lo cuenta como 2.0
- El RMSE lo cuenta como 2.0² = 4.0, penalizándolo más
- **RMSE siempre será ≥ MAE**

**Interpretación:**
- RMSE = 0.589 Bs/kg significa que los errores grandes son penalizados
- **Menor es mejor**: Un RMSE bajo indica predicciones consistentes

**¿Cuándo usar cada uno?**
- **MAE**: Si todos los errores son igualmente importantes
- **RMSE**: Si quieres evitar errores muy grandes (más conservador)

##### 3. R² (Coeficiente de Determinación) - R-Squared

**¿Qué es?**
Mide qué porcentaje de la variación en los precios es explicado por el modelo.

**Fórmula:**
```
R² = 1 - (SS_res / SS_tot)

Donde:
- SS_res = Suma de errores al cuadrado (residuales)
- SS_tot = Suma de diferencias al cuadrado (total)
```

**Interpretación:**
- **R² = 0.929** significa que el modelo explica el **92.9%** de la variación en precios
- Solo el 7.1% de la variación no es explicada por el modelo
- **Mayor es mejor**: R² = 1.0 sería perfecto (100% explicado)

**Escala de R²:**
- **R² = 1.0**: Modelo perfecto (imposible en la realidad)
- **R² = 0.9-1.0**: Excelente (90-100% explicado) ✅ Tu modelo está aquí
- **R² = 0.7-0.9**: Bueno (70-90% explicado)
- **R² = 0.5-0.7**: Aceptable (50-70% explicado)
- **R² < 0.5**: Malo (menos del 50% explicado)

**Ejemplo visual:**
```
Si los precios reales varían entre 20-30 Bs/kg:
- R² = 0.929 → El modelo explica el 92.9% de esa variación
- El 7.1% restante es "ruido" o factores no capturados
```

##### 4. Validación Cruzada Estable

**¿Qué significa "estable"?**
Que las métricas no varían mucho entre diferentes folds.

**Ejemplo:**
```
Modelo A (estable):
  Fold 1: MAE = 0.55
  Fold 2: MAE = 0.52
  Fold 3: MAE = 0.54
  Fold 4: MAE = 0.53
  Fold 5: MAE = 0.56
  Promedio: 0.54 ± 0.015 (poca variación) ✅

Modelo B (inestable):
  Fold 1: MAE = 0.45
  Fold 2: MAE = 0.65
  Fold 3: MAE = 0.40
  Fold 4: MAE = 0.70
  Fold 5: MAE = 0.50
  Promedio: 0.54 ± 0.12 (mucha variación) ⚠️
```

**¿Por qué es importante?**
- Un modelo estable es más confiable
- Si varía mucho entre folds, puede que no generalice bien
- Tu modelo tiene CV MAE = 0.550 ± 0.022 → **Muy estable** ✅

#### Criterio de Selección Final:

El sistema selecciona el modelo con **menor MAE** porque:
1. Es la métrica más fácil de interpretar
2. Es la que mejor refleja el error promedio esperado
3. Si hay empate, se considera RMSE y R²

**En tu caso:**
- Linear Regression: MAE = 0.467 Bs/kg ✅ **Ganador**
- Random Forest: MAE = 0.532 Bs/kg
- Gradient Boosting: MAE = 0.545 Bs/kg

**Resultado actual (modelo re-entrenado con rangos ampliados):** Linear Regression gana por:
- MAE: 0.467 Bs/kg (mejorado)
- R²: 0.929 (explica 92.9% de la varianza - excelente)
- CV MAE: 0.550 ± 0.022 Bs/kg (validación cruzada)
- Rápido, simple e interpretable

### 4.6. Guardado del Modelo

```python
model_data = {
    'model': mejor_modelo_entrenado,
    'scaler': scaler_fitted,
    'feature_names': ['cantidad_animales', ...],
    'metrics': {...},
    ...
}

joblib.dump(model_data, 'ml/models/12_months_model.pkl')
```

---

## 5. PREDICCIÓN EN TIEMPO REAL

**Archivo:** `api/routes/v1/prediccion.py` → `predict_lote()`

### 5.1. Obtener Datos del Lote
```python
# Desde la base de datos
lote = db.lote.find_unique(id_lote=1400)
costos = db.costo.find_many(id_lote=1400)
produccion = db.produccion.find_unique(id_lote=1400)
```

### 5.2. Construir Features

**Archivo:** `api/services/features_service.py` → `build_features_para_modelo()`

```python
# Calcula las 10 features del lote real (ejemplo: lote 1400)
features = {
    "cantidad_animales": 16,
    "peso_promedio_entrada": 98.91,
    "precio_compra_kg": 20.68,
    "costo_logistica_total": 864.00,
    "costo_alimentacion_estadia": 339.75,
    "duracion_estadia_dias": 1,
    "mes_adquisicion": 12,
    "costo_total_lote": 33,936.83,
    "peso_salida": 1,601.01,  # Con ganancia de peso (1.15 kg/día/cerdo)
    "costo_fijo_por_kg": 0.37,
}
```

### 5.3. Normalizar Features
```python
# Cargar modelo y scaler guardados
model_data = joblib.load('ml/models/12_months_model.pkl')
model = model_data['model']
scaler = model_data['scaler']

# Construir vector de entrada (ejemplo: lote 1400)
X = [[16, 98.91, 20.68, 864, 339.75, 1, 12, 33936.83, 1601.01, 0.37]]

# Normalizar con el mismo scaler usado en entrenamiento
X_scaled = scaler.transform(X)
# Resultado: valores normalizados en la misma escala que el entrenamiento
# Ejemplo: [16, 98.91, ...] → [-0.98, 1.2, ...] (valores normalizados)
```

### 5.4. Hacer Predicción
```python
# El modelo predice directamente el precio
precio_ml_base = model.predict(X_scaled)[0]
# Resultado: 24.79 Bs/kg (ejemplo con lote 1400, modelo re-entrenado)
```

### 5.5. Aplicar Margen Adicional
```python
# Si el usuario selecciona un margen (ej: 10%)
margen_rate = 0.10

# Aplicar margen sobre el precio base
precio_final = precio_ml_base * (1 + margen_rate)
# Resultado: 24.79 × 1.10 = 27.27 Bs/kg (ejemplo con lote 1400)
```

### 5.6. Calcular Métricas Financieras
```python
ingreso_total = precio_final × kilos_salida
costo_total = compra + costos_variables + costos_fijos
ganancia_neta = ingreso_total - costo_total
roi = (ganancia_neta / costo_total) × 100
```

---

## 6. COMPONENTES TÉCNICOS

### 6.1. StandardScaler (Normalización) - EXPLICACIÓN DETALLADA

#### ¿Qué es StandardScaler?

**StandardScaler** es una técnica de preprocesamiento que transforma todas las features (variables de entrada) para que tengan la misma escala estadística.

#### ¿Por qué es necesario?

**Problema sin normalización:**
Imagina que tienes estas features:
- `cantidad_animales`: valores entre 15-100
- `costo_total_lote`: valores entre 20,000-50,000 Bs

Si no normalizas:
- El modelo verá que `costo_total_lote` tiene valores mucho más grandes
- Pensará que es más importante (aunque no necesariamente lo sea)
- `cantidad_animales` será ignorada porque sus valores son pequeños

**Solución con StandardScaler:**
- Transforma ambas features a la misma escala
- Ambas tienen igual "peso" en el modelo
- El modelo puede aprender correctamente la importancia real de cada feature

#### ¿Qué hace exactamente?

**Transformación Z-score (estandarización):**

```
valor_normalizado = (valor - media) / desviación_estándar
```

**Resultado:**
- **Media = 0**: Los valores se centran en cero
- **Desviación estándar = 1**: Todos tienen la misma "dispersión"

#### Ejemplo Práctico:

**Feature: cantidad_animales**
```
Valores originales: [15, 20, 25, 30, 50, 80, 100]
Media: 45.7
Desviación estándar: 30.2

Valor a normalizar: 16
Normalizado: (16 - 45.7) / 30.2 = -0.98
```

**Feature: costo_total_lote**
```
Valores originales: [20,000, 25,000, 30,000, 35,000, 40,000, 45,000, 50,000]
Media: 35,000
Desviación estándar: 10,801

Valor a normalizar: 33,937
Normalizado: (33,937 - 35,000) / 10,801 = -0.10
```

**Resultado:**
- Ambos valores están ahora en la misma escala (-0.98 y -0.10)
- El modelo puede compararlos directamente
- Ninguna feature domina sobre la otra

#### Proceso en tu Sistema:

**1. Durante el Entrenamiento:**
```python
scaler = StandardScaler()
scaler.fit(X_train)  # Aprende media y desv. estándar de cada feature

# Guarda:
# - Media de cada feature
# - Desviación estándar de cada feature
```

**2. Durante la Predicción:**
```python
# Carga el scaler guardado
scaler = model_data['scaler']

# Normaliza las features del lote nuevo
X_scaled = scaler.transform(X_nuevo)

# Usa las mismas medias y desviaciones del entrenamiento
```

**⚠️ IMPORTANTE:**
- Debes usar el **mismo scaler** del entrenamiento
- No puedes crear un scaler nuevo para cada predicción
- Si cambias el scaler, las predicciones serán incorrectas

#### Ventajas de StandardScaler:

✅ **Igual peso**: Todas las features tienen la misma importancia inicial
✅ **Convergencia rápida**: Los algoritmos de ML convergen más rápido
✅ **Mejor precisión**: El modelo puede aprender mejor las relaciones
✅ **Estable**: Funciona bien con la mayoría de algoritmos

#### Alternativas (no usadas en tu sistema):

- **MinMaxScaler**: Escala entre 0 y 1 (no usado aquí)
- **RobustScaler**: Usa mediana en lugar de media (más robusto a outliers)
- **Sin normalización**: Solo funciona si todas las features ya están en la misma escala

#### Ejemplo Visual:

```
ANTES (sin normalizar):
cantidad_animales:    [15, 20, 25, 30, 50, 80, 100]
costo_total_lote:    [20,000, 25,000, 30,000, 35,000, 40,000, 45,000, 50,000]
                      ↑
                      costo_total_lote domina porque es mucho más grande

DESPUÉS (normalizado):
cantidad_animales:    [-1.0, -0.8, -0.7, -0.5, 0.1, 1.1, 1.8]
costo_total_lote:    [-1.4, -0.9, -0.5, 0.0, 0.5, 0.9, 1.4]
                      ↑
                      Ambas en la misma escala, igual peso
```

### 6.2. Linear Regression (Modelo Final) - EXPLICACIÓN DETALLADA

#### ¿Qué es la Regresión Lineal?

La **Regresión Lineal** es un algoritmo de Machine Learning que encuentra la mejor línea recta (o plano en múltiples dimensiones) que relaciona las características de entrada (features) con el valor a predecir (target).

**Analogía simple:**
Imagina que tienes un gráfico con puntos dispersos. La regresión lineal dibuja la línea recta que mejor se ajusta a esos puntos, minimizando la distancia entre la línea y todos los puntos.

#### Fórmula Matemática:

```
y = w₀ + w₁×x₁ + w₂×x₂ + w₃×x₃ + ... + w₁₀×x₁₀

Donde:
- y = precio_venta_final_kg (lo que queremos predecir)
- w₀ = intercepto (término constante, el "punto de partida")
- w₁, w₂, ..., w₁₀ = coeficientes (pesos aprendidos)
- x₁, x₂, ..., x₁₀ = features normalizadas (entradas)
```

#### Ejemplo Práctico con tu Modelo:

Para el lote 1400, el modelo aprendió algo como:
```
precio = 15.2 + (0.8 × cantidad_animales) + (0.05 × peso_entrada) 
        + (0.9 × precio_compra) + (0.001 × logística) + ...
```

**Interpretación:**
- Si `precio_compra` aumenta 1 Bs/kg → el precio predicho aumenta ~0.9 Bs/kg
- Si `cantidad_animales` aumenta 10 → el precio predicho aumenta ~8 Bs/kg
- El intercepto (15.2) es el precio base cuando todas las features son 0

#### Proceso de Aprendizaje (Entrenamiento):

1. **Inicialización**: El modelo empieza con pesos aleatorios (w₀, w₁, ..., w₁₀)
2. **Predicción**: Calcula `y_pred = w₀ + w₁×x₁ + ... + w₁₀×x₁₀` para cada lote
3. **Error**: Compara predicción vs valor real: `error = y_real - y_pred`
4. **Ajuste**: Modifica los pesos para reducir el error
5. **Repetición**: Repite pasos 2-4 miles de veces hasta minimizar el error

**Método usado:** Mínimos Cuadrados (Ordinary Least Squares - OLS)
- Encuentra los pesos que minimizan la suma de errores al cuadrado
- Matemáticamente garantiza la mejor solución posible

#### Ventajas de Regresión Lineal:

✅ **Simple y rápida**: Fácil de entender e implementar
✅ **Interpretable**: Puedes ver exactamente cómo cada feature afecta el precio
✅ **Eficiente**: Entrena y predice muy rápido
✅ **Estable**: No tiene hiperparámetros complejos que ajustar
✅ **Funciona bien**: En muchos casos es tan buena como modelos más complejos

#### Desventajas:

⚠️ **Asume relación lineal**: Si la relación real es muy compleja/no-lineal, puede no capturarla bien
⚠️ **Sensible a outliers**: Valores extremos pueden afectar mucho el modelo

#### ¿Por qué funciona bien en tu caso?

En tu negocio de reventa de cerdos:
- Las relaciones son principalmente lineales (más costos → más precio)
- El precio depende de sumas y proporciones (costos + margen)
- No hay relaciones muy complejas o no-lineales
- Por eso Linear Regression es perfecto para este problema

### 6.3. Validación Cruzada (K-Fold)

**Proceso:**
```
Datos: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

Fold 1: Entrenar [2-10], Probar [1] → MAE₁
Fold 2: Entrenar [1,3-10], Probar [2] → MAE₂
...
Fold 5: Entrenar [1-4,6-10], Probar [5] → MAE₅

MAE final = (MAE₁ + MAE₂ + ... + MAE₅) / 5
```

**Ventajas:**
- Usa todos los datos
- Reduce riesgo de sobreajuste
- Métricas más confiables

### 6.4. Métricas de Evaluación

**MAE (Mean Absolute Error):**
```
MAE = (1/n) × Σ|y_real - y_pred|
```
- Error promedio en Bs/kg
- Ejemplo: MAE = 0.498 → error promedio de 0.50 Bs/kg

**RMSE (Root Mean Squared Error):**
```
RMSE = √[(1/n) × Σ(y_real - y_pred)²]
```
- Penaliza errores grandes más que MAE
- Ejemplo: RMSE = 0.65 Bs/kg

**R² (Coeficiente de Determinación):**
```
R² = 1 - (SS_res / SS_tot)
```
- Proporción de varianza explicada
- R² = 0.752 → el modelo explica 75.2% de la variación en precios

---

## 🎯 RESUMEN EJECUTIVO

### Flujo Completo:

1. **ENTRENAMIENTO (Offline, una vez)**
   - Genera 360 lotes sintéticos
   - Entrena 3 modelos con validación cruzada
   - Selecciona mejor modelo (Linear Regression)
   - Guarda modelo + scaler

2. **PREDICCIÓN (Online, cada solicitud)**
   - Obtiene datos del lote desde BD
   - Construye 10 features
   - Normaliza con scaler guardado
   - Predice precio con modelo entrenado
   - Aplica margen adicional si se solicita

### Características Clave:

- ✅ **10 Features**: Capturan toda la información relevante
- ✅ **Normalización**: StandardScaler asegura igual peso
- ✅ **Validación Cruzada**: Métricas confiables
- ✅ **Modelo Simple**: Linear Regression (rápido, interpretable)
- ✅ **Precisión**: MAE = 0.467 Bs/kg, R² = 0.929 (modelo re-entrenado con rangos ampliados)

---

## 📚 REFERENCIAS TÉCNICAS

- **Scikit-learn**: Biblioteca de ML en Python
- **Linear Regression**: Algoritmo de regresión lineal múltiple
- **StandardScaler**: Normalización Z-score
- **K-Fold Cross-Validation**: Validación cruzada con K=5
- **Joblib**: Serialización de modelos Python

---

---

## 📖 GLOSARIO Y CONCEPTOS CLAVE

### Regresión Lineal - Explicación Simple

**¿Qué es?**
La regresión lineal es como encontrar la mejor línea recta que pasa por un conjunto de puntos. En tu caso, esos "puntos" son los lotes de cerdos con sus características y precios reales.

**Analogía del mundo real:**
Imagina que tienes un gráfico donde:
- Eje X: cantidad de animales
- Eje Y: precio de venta

La regresión lineal dibuja la línea que mejor se ajusta a todos tus datos históricos. Luego, cuando tienes un nuevo lote, puedes usar esa línea para predecir su precio.

**En tu sistema:**
- No es solo una línea (2D), sino un "plano" en 10 dimensiones (una por cada feature)
- El modelo aprende cómo cada característica (cantidad, peso, costos, etc.) afecta el precio final
- La fórmula aprendida es: `precio = constante + (peso₁ × feature₁) + (peso₂ × feature₂) + ...`

**¿Por qué funciona bien?**
En tu negocio, el precio depende principalmente de sumas y proporciones:
- Precio = Compra + Costos + Margen
- Esta es una relación principalmente lineal, perfecta para regresión lineal

---

### Criterios de Selección del Modelo - Guía Completa

Cuando entrenas varios modelos (Linear, Random Forest, Gradient Boosting), necesitas decidir cuál es el mejor. Aquí están los criterios:

#### 1. MAE (Error Absoluto Medio) - El Criterio Principal

**Pregunta que responde:** "¿Cuánto se equivoca el modelo en promedio?"

**Ejemplo concreto:**
```
Predicciones del modelo para 5 lotes:
Lote 1: Predijo 24.50, Real fue 25.00 → Error: 0.50 Bs/kg
Lote 2: Predijo 23.80, Real fue 23.00 → Error: 0.80 Bs/kg
Lote 3: Predijo 25.30, Real fue 26.00 → Error: 0.70 Bs/kg
Lote 4: Predijo 22.90, Real fue 22.50 → Error: 0.40 Bs/kg
Lote 5: Predijo 24.20, Real fue 24.00 → Error: 0.20 Bs/kg

MAE = (0.50 + 0.80 + 0.70 + 0.40 + 0.20) / 5 = 0.52 Bs/kg
```

**Interpretación:**
- "El modelo se equivoca en promedio por 0.52 Bs/kg"
- Si vendes 1,000 kg, el error promedio sería de 520 Bs
- **Menor MAE = Mejor modelo**

**Tu modelo actual:** MAE = 0.467 Bs/kg
- Esto significa que, en promedio, el precio predicho está a 0.47 Bs/kg del precio real
- Es un error muy bajo (menos del 2% del precio típico de ~25 Bs/kg)

#### 2. RMSE (Raíz del Error Cuadrático Medio) - Penaliza Errores Grandes

**Pregunta que responde:** "¿Qué tan grandes son los peores errores?"

**Mismo ejemplo:**
```
Mismos 5 lotes:
MAE = 0.52 Bs/kg (promedio simple)
RMSE = √[(0.50² + 0.80² + 0.70² + 0.40² + 0.20²) / 5]
     = √[(0.25 + 0.64 + 0.49 + 0.16 + 0.04) / 5]
     = √[0.316] = 0.56 Bs/kg
```

**Diferencia clave:**
- Si un error es muy grande (ej: 2.0 Bs/kg), el MAE lo cuenta como 2.0
- El RMSE lo cuenta como 2.0² = 4.0, penalizándolo más
- **RMSE siempre será ≥ MAE**

**Cuándo importa:**
- Si quieres evitar errores muy grandes (más conservador)
- Si un error grande es mucho peor que varios errores pequeños

**Tu modelo actual:** RMSE = 0.589 Bs/kg
- Indica que los errores grandes son controlados
- La diferencia con MAE (0.467) es pequeña, lo que significa que no hay errores extremos

#### 3. R² (Coeficiente de Determinación) - Qué Tan Bien Explica

**Pregunta que responde:** "¿Qué porcentaje de la variación en precios explica el modelo?"

**Ejemplo visual:**
```
Imagina que los precios reales varían así:
Lote 1: 20.00 Bs/kg
Lote 2: 22.50 Bs/kg
Lote 3: 25.00 Bs/kg
Lote 4: 27.50 Bs/kg
Lote 5: 30.00 Bs/kg

Variación total: 10.00 Bs/kg (de 20 a 30)

Si R² = 0.929:
- El modelo explica el 92.9% de esa variación
- Solo el 7.1% es "ruido" o factores no capturados
```

**Escala de interpretación:**
- **R² = 1.0**: Perfecto (100% explicado) - Imposible en la realidad
- **R² = 0.9-1.0**: Excelente (90-100%) ✅ **Tu modelo está aquí**
- **R² = 0.7-0.9**: Bueno (70-90%)
- **R² = 0.5-0.7**: Aceptable (50-70%)
- **R² < 0.5**: Malo (menos del 50%)

**Tu modelo actual:** R² = 0.929
- Explica el 92.9% de la variación en precios
- Solo el 7.1% no es explicado (factores externos, ruido, etc.)
- **Excelente resultado**

#### 4. Validación Cruzada Estable - Confiabilidad

**Pregunta que responde:** "¿El modelo es consistente o varía mucho?"

**Ejemplo de modelo estable:**
```
Validación cruzada (5 folds):
Fold 1: MAE = 0.55 Bs/kg
Fold 2: MAE = 0.52 Bs/kg
Fold 3: MAE = 0.54 Bs/kg
Fold 4: MAE = 0.53 Bs/kg
Fold 5: MAE = 0.56 Bs/kg

Promedio: 0.54 Bs/kg
Desviación estándar: ±0.015 Bs/kg (muy pequeña) ✅ ESTABLE
```

**Ejemplo de modelo inestable:**
```
Validación cruzada (5 folds):
Fold 1: MAE = 0.45 Bs/kg
Fold 2: MAE = 0.65 Bs/kg
Fold 3: MAE = 0.40 Bs/kg
Fold 4: MAE = 0.70 Bs/kg
Fold 5: MAE = 0.50 Bs/kg

Promedio: 0.54 Bs/kg
Desviación estándar: ±0.12 Bs/kg (muy grande) ⚠️ INESTABLE
```

**¿Por qué importa?**
- Un modelo estable es más confiable
- Si varía mucho, puede que no generalice bien a nuevos datos
- Prefieres un modelo que siempre funciona "bien" a uno que a veces funciona "muy bien" y a veces "muy mal"

**Tu modelo actual:** CV MAE = 0.550 ± 0.022 Bs/kg
- Desviación estándar de solo 0.022 → **Muy estable** ✅
- El modelo es consistente en diferentes subconjuntos de datos

---

### StandardScaler - Normalización Explicada

#### ¿Por qué necesitas normalizar?

**Problema real:**
Tus features tienen escalas muy diferentes:
- `cantidad_animales`: 15-100 (números pequeños)
- `costo_total_lote`: 20,000-50,000 (números muy grandes)

Sin normalizar, el modelo pensaría:
- "costo_total_lote es más importante porque sus números son más grandes"
- Esto es incorrecto: ambas features pueden ser igualmente importantes

**Solución: StandardScaler**
Transforma todas las features a la misma escala, dándoles igual "peso" inicial.

#### ¿Cómo funciona?

**Fórmula:**
```
valor_normalizado = (valor - media) / desviación_estándar
```

**Ejemplo paso a paso:**

**Feature: cantidad_animales**
```
Valores originales: [15, 20, 25, 30, 50, 80, 100]
Media: 45.7
Desviación estándar: 30.2

Para normalizar el valor 16:
Normalizado = (16 - 45.7) / 30.2 = -0.98
```

**Feature: costo_total_lote**
```
Valores originales: [20,000, 25,000, 30,000, 35,000, 40,000, 45,000, 50,000]
Media: 35,000
Desviación estándar: 10,801

Para normalizar el valor 33,937:
Normalizado = (33,937 - 35,000) / 10,801 = -0.10
```

**Resultado:**
- Ambos valores están ahora en la misma escala (-0.98 y -0.10)
- El modelo puede compararlos directamente
- Ninguna feature domina sobre la otra

#### Proceso en tu Sistema:

**1. Durante el Entrenamiento:**
```python
# El scaler "aprende" las características de los datos
scaler = StandardScaler()
scaler.fit(X_train)

# Guarda internamente:
# - Media de cada feature: [45.7, 35,000, ...]
# - Desviación estándar de cada feature: [30.2, 10,801, ...]
```

**2. Durante la Predicción:**
```python
# Carga el scaler guardado (con las medias y desviaciones aprendidas)
scaler = model_data['scaler']

# Normaliza las features del lote nuevo usando las mismas estadísticas
X_scaled = scaler.transform(X_nuevo)

# Usa las mismas medias y desviaciones del entrenamiento
# Esto es CRÍTICO: debe usar los mismos parámetros
```

**⚠️ IMPORTANTE:**
- Debes usar el **mismo scaler** del entrenamiento
- No puedes crear un scaler nuevo para cada predicción
- Si cambias el scaler, las predicciones serán incorrectas
- Es como usar una regla diferente para medir: los resultados no serían comparables

#### Ventajas:

✅ **Igual peso**: Todas las features tienen la misma importancia inicial
✅ **Convergencia rápida**: Los algoritmos de ML convergen más rápido
✅ **Mejor precisión**: El modelo puede aprender mejor las relaciones
✅ **Estable**: Funciona bien con la mayoría de algoritmos

#### Ejemplo Visual:

```
ANTES (sin normalizar):
┌─────────────────────────────────────┐
│ cantidad_animales:    [15, 20, 25]  │ ← Números pequeños
│ costo_total_lote:     [20k, 25k, 30k] │ ← Números muy grandes
│                                      │
│ El modelo piensa:                    │
│ "costo_total_lote es más importante" │ ❌ Incorrecto
└─────────────────────────────────────┘

DESPUÉS (normalizado):
┌─────────────────────────────────────┐
│ cantidad_animales:    [-1.0, -0.8, -0.7] │ ← Misma escala
│ costo_total_lote:     [-1.4, -0.9, -0.5] │ ← Misma escala
│                                      │
│ El modelo piensa:                    │
│ "Ambas tienen igual peso inicial"    │ ✅ Correcto
└─────────────────────────────────────┘
```

---

**Última actualización:** Diciembre 2024 (Modelo re-entrenado con rangos ampliados)


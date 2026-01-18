# 🐷 Guía Completa de Funcionalidades - Sistema de Gestión de Granja del Cerdo

## 📋 Tabla de Contenidos

1. [Instalación y Configuración del Proyecto](#instalación-y-configuración-del-proyecto)
2. [Credenciales de Acceso](#credenciales-de-acceso)
3. [Funcionalidades del Sistema](#funcionalidades-del-sistema)
   - [Dashboard Analítico](#1-dashboard-analítico)
   - [Gestión de Lotes](#2-gestión-de-lotes)
   - [Control de Costos](#3-control-de-costos)
   - [Predicciones con Machine Learning](#4-predicciones-con-machine-learning)
   - [Catálogo de Tipos de Costo](#5-catálogo-de-tipos-de-costo)

---

## 🚀 Instalación y Configuración del Proyecto

### Requisitos Previos

- **Python 3.9 o superior**
- **PostgreSQL** (base de datos)
- **Git** (para clonar el repositorio)
- **Navegador web moderno** (Chrome, Firefox, Edge, etc.)

### Paso 1: Clonar el Repositorio

```bash
git clone <url-del-repositorio>
cd monorepo
```

### Paso 2: Configurar el Backend (API)

1. **Navegar al directorio de la API:**
   ```bash
   cd api
   ```

2. **Crear entorno virtual (recomendado):**
   ```bash
   python -m venv venv
   ```
   
   **Activar el entorno virtual:**
   - **Windows:**
     ```bash
     venv\Scripts\activate
     ```
   - **Linux/Mac:**
     ```bash
     source venv/bin/activate
     ```

3. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar variables de entorno:**
   
   Crea un archivo `.env` en el directorio `api/` con el siguiente contenido:
   ```env
   DATABASE_URL=postgresql://granjadelcerdo_pdb_user:Kuef1xTZUY9SxoggqmFxPDXo2LLkteWF@dpg-d3pa6q1r0fns73afp7h0-a.oregon-postgres.render.com/granjadelcerdo_pdb
   JWT_SECRET=mysecret123
   ```

5. **Configurar Prisma (generar cliente):**
   ```bash
   python -m prisma generate
   ```

6. **Ejecutar la API:**
   ```bash
   python app.py
   ```
   
   La API estará disponible en: **http://127.0.0.1:8000**

### Paso 3: Configurar el Frontend (UI)

1. **Abrir una nueva terminal** y navegar al directorio de la UI:
   ```bash
   cd ui
   ```

2. **Crear entorno virtual (opcional, pero recomendado):**
   ```bash
   python -m venv venv
   ```
   
   **Activar el entorno virtual:**
   - **Windows:**
     ```bash
     venv\Scripts\activate
     ```
   - **Linux/Mac:**
     ```bash
     source venv/bin/activate
     ```

3. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Ejecutar la aplicación Streamlit:**
   ```bash
   streamlit run Inicio.py
   ```
   
   La interfaz estará disponible en: **http://localhost:8501**

### Paso 4: Verificar que Todo Funciona

1. **Verificar el Backend:**
   - Abre tu navegador y visita: `http://127.0.0.1:8000`
   - Deberías ver un mensaje JSON con información de la API

2. **Verificar el Frontend:**
   - Abre tu navegador y visita: `http://localhost:8501`
   - Deberías ver la página de login

---

## 🔐 Credenciales de Acceso

Para iniciar sesión en el sistema, utiliza las siguientes credenciales:

```
Email: dayanadelgadillo@granja.com
Contraseña: granjacerdo
```

### Pasos para Iniciar Sesión:

1. Abre la aplicación en tu navegador: `http://localhost:8501`
2. Verás la página de login con un fondo oscuro
3. Ingresa el email: `dayanadelgadillo@granja.com`
4. Ingresa la contraseña: `granjacerdo`
5. Haz clic en el botón **"Iniciar Sesión"**
6. Serás redirigido automáticamente al Dashboard

**⚠️ Nota Importante:** Al recargar la página del navegador, perderás la sesión y deberás iniciar sesión nuevamente. El sistema mostrará una advertencia nativa del navegador antes de recargar.

---

## 📱 Funcionalidades del Sistema

El sistema está organizado en 5 páginas principales accesibles desde el menú lateral:

### 1. Dashboard Analítico 📊

#### Descripción
Vista general del sistema con análisis estadísticos, gráficos interactivos y métricas clave de la granja.

#### Funcionalidades Disponibles:

**📈 Métricas Principales:**
- Total de lotes registrados
- Cantidad total de animales
- Costos totales (fijos y variables)
- Ingresos proyectados

**📊 Gráficos Interactivos:**
- Gráficos de líneas para tendencias temporales
- Gráficos de barras animados
- Gráficos de dona para distribución
- Gráficos de dispersión con regresión
- Comparaciones entre lotes

**🔍 Filtros de Análisis:**
- Filtrar por rango de fechas
- Filtrar por tipo de lote
- Ordenar resultados por diferentes criterios

**📋 Tabla de Resumen:**
- Vista tabular de los últimos 20 lotes
- Información detallada: Número del lote, fecha, cantidad de animales, peso promedio, precio/kg, duración

#### Cómo Probar el Dashboard:

1. **Acceder al Dashboard:**
   - Después de iniciar sesión, serás redirigido automáticamente
   - O selecciona "Dashboard" desde el menú lateral

2. **Explorar las Métricas:**
   - Observa las tarjetas de métricas en la parte superior
   - Cada tarjeta muestra un valor clave con icono y color distintivo

3. **Interactuar con los Gráficos:**
   - Pasa el cursor sobre los gráficos para ver valores detallados
   - Usa la herramienta de zoom si está disponible
   - Explora los diferentes tipos de visualizaciones

4. **Usar los Filtros:**
   - Ajusta el rango de fechas para analizar períodos específicos
   - Selecciona diferentes opciones de ordenamiento
   - Haz clic en "Actualizar" para aplicar los filtros

---

### 2. Gestión de Lotes 🐷

#### Descripción
Módulo completo para gestionar los lotes de cerdos: crear, listar, editar y eliminar lotes.

#### Funcionalidades Disponibles:

**📋 Tab 1: Listar Lotes**

- **Búsqueda por número de lote:**
  - Campo de búsqueda para encontrar lotes específicos
  - Ingresa el número del lote y presiona Enter

- **Ordenamiento:**
  - Por número (ascendente/descendente)
  - Por fecha (reciente/antigua)

- **Visualización:**
  - Tabla con información detallada de todos los lotes
  - Columnas: Número del Lote, Fecha Adquisición, Cantidad Animales, Peso Promedio, Precio, Duración

**➕ Tab 2: Crear Lote**

Permite crear un nuevo lote con la siguiente información:

- **Fecha de Adquisición** (requerido): Fecha en que se adquirió el lote
- **Cantidad de Animales** (requerido): Número de cerdos en el lote (debe ser mayor a 0)
- **Peso Promedio de Entrada** (requerido): Peso promedio por cerdo en kg (debe ser mayor a 0)
- **Duración de Estadía (días)** (opcional): Días que permanecerán los animales (0-7 días)
- **Precio de Compra por kg** (opcional): Precio pagado por kilogramo (debe ser mayor a 0)

**Pasos para Crear un Lote:**

1. Navega a la página "Lotes" desde el menú lateral
2. Selecciona la pestaña **"➕ Crear Lote"**
3. Completa el formulario:
   - Selecciona la fecha de adquisición usando el selector de fecha
   - Ingresa la cantidad de animales (ej: 60)
   - Ingresa el peso promedio de entrada en kg (ej: 105.0)
   - Opcionalmente, ingresa la duración de estadía en días (0-7)
   - Opcionalmente, ingresa el precio de compra por kg
4. Haz clic en el botón **"✅ Crear Lote"**
5. Verás una confirmación de éxito y los detalles del lote creado
6. Opcionalmente, puedes hacer clic en **"Crear Otro Lote"** para agregar más lotes

**✏️ Tab 3: Editar Lote**

Permite modificar o eliminar un lote existente:

**Pasos para Editar un Lote:**

1. Navega a la página "Lotes"
2. Selecciona la pestaña **"✏️ Editar Lote"**
3. **Selecciona un lote** del dropdown (muestra: Número | cantidad animales | fecha)
4. Se mostrarán las **métricas actuales** del lote seleccionado:
   - Número del Lote
   - Cantidad de Animales
   - Peso Promedio
   - Precio de Compra
5. **Modifica los campos** que deseas cambiar:
   - Fecha de Adquisición
   - Cantidad de Animales
   - Peso Promedio de Entrada
   - Duración de Estadía
   - Precio de Compra por kg
6. Haz clic en **"💾 Actualizar Lote"** para guardar los cambios
7. Verás una confirmación de éxito con el mensaje "Lote Número X actualizado correctamente"

**Pasos para Eliminar un Lote:**

1. En la pestaña "✏️ Editar Lote", selecciona el lote que deseas eliminar
2. Completa cualquier campo del formulario (si quieres hacer algún cambio antes de eliminar)
3. Haz clic en el botón **"🗑️ Eliminar"**
4. Aparecerá una advertencia: "⚠️ ¿Estás seguro de que deseas eliminar este lote? Esta acción no se puede deshacer."
5. Tienes dos opciones:
   - **"❌ Cancelar"**: Cancela la operación
   - **"✅ Confirmar Eliminación"**: Confirma y elimina el lote permanentemente
6. Verás una confirmación de éxito: "Lote Número X eliminado correctamente"

**⚠️ Importante:**
- La eliminación es **permanente** y no se puede deshacer
- Al eliminar un lote, también se eliminarán todos los costos asociados

---

### 3. Control de Costos 💰

#### Descripción
Gestión completa de costos asociados a cada lote: registrar, editar y eliminar gastos.

#### Funcionalidades Disponibles:

**📊 Tab 1: Análisis de Costos**

- **Visualización de costos por lote:**
  - Gráficos de distribución de costos
  - Resumen de costos fijos vs variables
  - Estadísticas financieras

**➕ Tab 2: Registrar Costo**

Permite registrar un nuevo costo para un lote específico:

**Campos del Formulario:**

- **Lote** (selección automática): El lote seleccionado en la parte superior de la página
- **Tipo de Costo** (requerido): Selecciona de la lista de tipos de costo disponibles
- **Monto (Bs.)** (requerido): Cantidad en bolivianos (debe ser mayor a 0)
- **Fecha del Gasto** (requerido): Fecha en que se realizó el gasto
- **Descripción** (opcional): Detalles adicionales sobre el gasto

**Pasos para Registrar un Costo:**

1. Navega a la página "Costos" desde el menú lateral
2. **Selecciona un lote** del dropdown en la parte superior
3. Selecciona la pestaña **"➕ Registrar Costo"**
4. Si no hay tipos de costo disponibles, verás una advertencia indicando que debes crear tipos primero
5. Completa el formulario:
   - Selecciona el **tipo de costo** (ej: "Alimentación (VARIABLE)")
   - Ingresa el **monto** en bolivianos (ej: 5000.00)
   - Selecciona la **fecha del gasto**
   - Opcionalmente, agrega una **descripción**
6. Haz clic en **"✅ Registrar Costo"**
7. Verás una confirmación de éxito con el monto registrado
8. El costo quedará asociado al lote seleccionado

**✏️ Tab 3: Editar Costo**

Permite modificar o eliminar un costo existente:

**Pasos para Editar un Costo:**

1. En la página "Costos", selecciona un lote
2. Selecciona la pestaña **"✏️ Editar Costo"**
3. **Selecciona un costo** del dropdown (muestra: Número | Tipo de Costo | Monto)
4. Se mostrará un formulario con la información actual del costo:
   - Fecha del Gasto
   - Monto
   - Descripción
5. **Modifica los campos** que deseas cambiar
6. Haz clic en **"💾 Actualizar"** para guardar los cambios
7. Verás una confirmación de éxito

**Pasos para Eliminar un Costo:**

1. En la pestaña "✏️ Editar Costo", selecciona el costo que deseas eliminar
2. Modifica cualquier campo si lo deseas
3. Haz clic en el botón **"🗑️ Eliminar"**
4. Aparecerá una confirmación de eliminación
5. El costo será eliminado permanentemente

---

### 4. Predicciones con Machine Learning 🔮

#### Descripción
Sistema avanzado de predicción de precios usando Machine Learning basado en las características de los lotes.

#### Funcionalidades Disponibles:

**📊 Información del Modelo ML:**

Al expandir el panel "ℹ️ Información del Modelo de Machine Learning", verás:
- **Especificaciones:** Algoritmo (LinearRegression), Precisión (MAE: 0.435 Bs/kg), R² Score (0.934), Features (9 variables)
- **Proceso de Predicción:** Pasos que sigue el modelo para generar predicciones

**🔍 Selección de Lote:**

1. Selecciona un lote del dropdown (muestra: Número | animales | Peso | fecha)
2. El sistema cargará automáticamente la información del lote seleccionado

**📈 Información del Lote:**

Se muestran las métricas clave del lote:
- Cantidad de Animales
- Peso Entrada (kg)
- Precio Compra (Bs/kg)
- Duración (días)

**💰 Análisis de Costos:**

Se muestran dos cards con:
- **Costos Variables:** Total y detalle por tipo
- **Costos Fijos:** Total y detalle por tipo

**⚙️ Configuración de Predicción:**

1. **Ajusta el Margen de Ganancia:**
   - Usa el slider para seleccionar un porcentaje entre 0% y 100%
   - Valor por defecto: 10%
   - Se muestra un gráfico gauge visual indicando el margen seleccionado

2. **Información del Margen:**
   - Recomendaciones según el margen:
     - **Bajo (0-10%):** Competitivo
     - **Medio (10-20%):** Equilibrado
     - **Alto (>20%):** Premium

**🔮 Generar Predicción:**

**Pasos para Generar una Predicción:**

1. Selecciona un lote que tenga información completa
2. Ajusta el margen de ganancia según tus preferencias
3. Haz clic en el botón **"🔮 Generar Predicción con ML"**
4. El sistema procesará la información y generará una predicción
5. Verás los resultados organizados en varias secciones:

**📊 Resultados Principales:**

Se muestran 4 métricas clave:
- **Precio Base ML:** Precio predicho por el modelo de ML (Bs/kg)
- **Fijo por kg:** Costos fijos distribuidos por kilogramo (Bs/kg)
- **Precio Sugerido:** Precio final recomendado incluyendo margen (Bs/kg)
- **Ganancia Neta:** Ganancia estimada total en bolivianos (Bs)

**📋 Desglose de Cálculo:**

Tabla detallada mostrando:
- Precio Base (ML)
- Costos Fijos por kg
- Subtotal
- Margen aplicado
- Precio Sugerido Final

**💡 Información Adicional:**

- **Datos de la Predicción:**
  - Número de Predicción
  - Número del Lote
  - Modelo utilizado
  - Precisión del modelo

- **Proyección Financiera:**
  - Peso Salida Total (kg)
  - Ingreso Total Estimado (Bs)
  - Costo Total (Bs)
  - ROI (Return on Investment) en porcentaje

**📈 Visualización Comparativa:**

Gráfico de barras mostrando la composición del precio sugerido:
- Precio Base
- Costos Fijos/kg
- Margen
- Precio Final

**🔬 Ver Datos Completos:**

Puedes expandir el panel "Ver Datos Completos de la Predicción (JSON)" para ver toda la información técnica de la predicción en formato JSON.

---

### 5. Catálogo de Tipos de Costo 📋

#### Descripción
Gestión del catálogo de tipos de costo que se pueden usar al registrar gastos.

#### Funcionalidades Disponibles:

**📊 Tab 1: Catálogo y Análisis**

- **Estadísticas:**
  - Total de tipos registrados
  - Cantidad de costos fijos
  - Cantidad de costos variables
  - Tipo más común

- **Filtros:**
  - Filtrar por categoría (Todas, FIJO, VARIABLE)
  - Buscar por nombre

- **Visualizaciones:**
  - Gráfico de dona mostrando distribución por categoría
  - Gráfico de barras con cantidad por categoría

- **Detalle del Catálogo:**
  - Lista visual de todos los tipos de costo
  - Cada tipo muestra:
    - Nombre del tipo
    - Número del tipo
    - Badge indicando la categoría (FIJO o VARIABLE)

- **Guía de Categorías:**
  - **Costos FIJOS:**
    - No varían con la cantidad
    - Ejemplos: Alquiler, servicios, mantenimiento
    - Se distribuyen entre todos los kg
  - **Costos VARIABLES:**
    - Varían con la cantidad
    - Ejemplos: Alimentación, transporte
    - Por animal o por kg

**➕ Tab 2: Crear Tipo de Costo**

**Pasos para Crear un Tipo de Costo:**

1. Navega a la página "Tipos de Costo" desde el menú lateral
2. Selecciona la pestaña **"➕ Crear Tipo de Costo"**
3. Completa el formulario:
   - **Nombre del Tipo** (requerido): Mínimo 3 caracteres
     - Ejemplos: "Alimentación", "Logística", "Mantenimiento", "Transporte"
   - **Categoría** (requerido): Selecciona entre:
     - **FIJO:** Para costos que no varían con la cantidad
     - **VARIABLE:** Para costos que varían con la cantidad
4. Revisa los ejemplos en el panel lateral para ayudarte a decidir la categoría
5. Haz clic en **"✅ Crear Tipo de Costo"**
6. Verás una confirmación de éxito: "Tipo de costo 'Nombre' creado exitosamente"
7. El nuevo tipo estará disponible inmediatamente para usar al registrar costos

**⚠️ Validaciones:**
- El nombre debe tener al menos 3 caracteres
- No se pueden crear tipos duplicados (si ya existe, verás un error)

**🤖 Sistema de Reconocimiento Automático:**

El sistema incluye un sistema inteligente que reconoce automáticamente ciertos nombres de tipos de costo para el modelo ML:

- **Adquisición:** adquisición, compra, precio_compra
- **Logística:** logística, transporte, flete, combustible
- **Alimentación:** alimentación, comida, pienso

Estos aliases ayudan al modelo ML a categorizar y procesar mejor los costos.

---

## 🔄 Flujo de Trabajo Recomendado

Para aprovechar al máximo el sistema, sigue este flujo de trabajo:

### 1. Configuración Inicial

1. **Crear Tipos de Costo** (Tipos de Costo → Crear Tipo):
   - Crea los tipos de costo que usarás frecuentemente
   - Ejemplos: "Alimentación" (VARIABLE), "Transporte" (VARIABLE), "Alquiler de Corral" (FIJO), "Mantenimiento" (FIJO)

### 2. Gestión Diaria

2. **Registrar Lotes** (Lotes → Crear Lote):
   - Crea un nuevo lote cuando adquieras animales
   - Completa toda la información disponible

3. **Registrar Costos** (Costos → Registrar Costo):
   - Para cada lote, registra los gastos asociados
   - Selecciona el tipo de costo apropiado
   - Agrega descripciones detalladas para mejor seguimiento

### 3. Análisis y Toma de Decisiones

4. **Analizar en el Dashboard** (Dashboard):
   - Revisa las métricas generales
   - Analiza tendencias con los gráficos
   - Identifica lotes o períodos que requieren atención

5. **Generar Predicciones** (Predicciones):
   - Selecciona un lote con información completa
   - Genera predicciones de precio para planificar ventas
   - Ajusta el margen según tus objetivos de negocio
   - Usa los resultados para tomar decisiones de precio

### 4. Mantenimiento

6. **Editar o Actualizar** (según sea necesario):
   - Edita lotes si hay cambios en la información
   - Actualiza costos si hay correcciones
   - Elimina registros obsoletos (con precaución)

---

## 💡 Consejos y Mejores Prácticas

### Para Registrar Lotes:

- ✅ Siempre completa la fecha de adquisición correctamente
- ✅ Registra el peso promedio de entrada con precisión (afecta las predicciones)
- ✅ Si conoces el precio de compra, ingrésalo para cálculos más precisos
- ✅ La duración de estadía ayuda a calcular costos de alimentación automáticamente

### Para Registrar Costos:

- ✅ Crea tipos de costo específicos y descriptivos
- ✅ Usa descripciones detalladas para mejor seguimiento
- ✅ Registra los costos lo más pronto posible después de incurrir en ellos
- ✅ Clasifica correctamente entre FIJO y VARIABLE

### Para Predicciones:

- ✅ Asegúrate de que el lote tenga todos los datos necesarios
- ✅ Registra todos los costos antes de generar predicciones
- ✅ Considera márgenes competitivos (10-15%) para mantener precios accesibles
- ✅ Compara múltiples predicciones ajustando el margen para encontrar el equilibrio ideal

### Para el Dashboard:

- ✅ Revisa el dashboard regularmente para identificar tendencias
- ✅ Usa los filtros para analizar períodos específicos
- ✅ Compara diferentes lotes para identificar mejores prácticas

---

## ⚠️ Advertencias Importantes

1. **Sesión:** 
   - Al recargar la página del navegador, perderás la sesión
   - El sistema mostrará una advertencia antes de recargar
   - Deberás iniciar sesión nuevamente después de recargar

2. **Eliminación de Datos:**
   - La eliminación de lotes y costos es **permanente**
   - No se puede deshacer después de confirmar
   - Ten cuidado al eliminar registros

3. **Dependencias:**
   - Para registrar costos, primero debes crear tipos de costo
   - Para generar predicciones, el lote debe tener información completa
   - Para analizar costos, necesitas tener costos registrados

4. **Backend:**
   - Asegúrate de que el backend esté ejecutándose antes de usar el frontend
   - Si ves errores de conexión, verifica que la API esté activa en el puerto 8000

---

## 🆘 Solución de Problemas

### Error: "No se puede conectar al backend"

**Solución:**
1. Verifica que el backend esté ejecutándose en `http://127.0.0.1:8000`
2. Abre una terminal y ejecuta: `cd api && python app.py`
3. Espera a ver el mensaje indicando que el servidor está corriendo
4. Recarga la página del frontend

### Error: "Error al cargar lotes/costos"

**Solución:**
1. Verifica tu conexión a internet (si la base de datos es remota)
2. Verifica que las credenciales de la base de datos sean correctas
3. Revisa los logs del backend para más detalles del error

### Error: "No hay tipos de costo disponibles"

**Solución:**
1. Ve a la página "Tipos de Costo"
2. Crea al menos un tipo de costo antes de registrar gastos

### Error al generar predicción

**Solución:**
1. Verifica que el lote tenga:
   - Cantidad de animales > 0
   - Peso promedio > 0
   - Al menos algunos costos registrados (recomendado)
2. Asegúrate de que el modelo ML esté disponible en el servidor
3. Verifica que el lote exista en la base de datos

---

## 📞 Información Técnica

### Puertos Utilizados:

- **Backend (API):** Puerto 8000
- **Frontend (Streamlit):** Puerto 8501

### URLs:

- **API Base:** `http://127.0.0.1:8000`
- **UI:** `http://localhost:8501`
- **API Health Check:** `http://127.0.0.1:8000/health`

### Tecnologías Utilizadas:

- **Frontend:** Streamlit 1.28+, Python 3.9+
- **Backend:** Flask 2.3+, Python 3.9+
- **Base de Datos:** PostgreSQL
- **ORM:** Prisma Python
- **Machine Learning:** Scikit-learn (LinearRegression)
- **Visualización:** Plotly, Matplotlib
- **Autenticación:** JWT (JSON Web Tokens)

---

## ✅ Checklist de Funcionalidades Probadas

Para asegurarte de que todo funciona correctamente, prueba esta secuencia:

- [ ] Iniciar sesión con las credenciales
- [ ] Visualizar el Dashboard y sus gráficos
- [ ] Crear un tipo de costo nuevo
- [ ] Crear un lote nuevo
- [ ] Registrar un costo para ese lote
- [ ] Editar el lote creado
- [ ] Editar el costo registrado
- [ ] Generar una predicción para el lote
- [ ] Verificar que la predicción muestra todos los detalles
- [ ] Eliminar un costo (opcional)
- [ ] Eliminar un lote (opcional)

---

¡Disfruta usando el Sistema de Gestión de Granja del Cerdo! 🐷✨


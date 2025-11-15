# 🐷 Granja del Cerdo - Sistema Completo

Sistema completo de gestión para granjas de cerdos que incluye API backend y interfaz de usuario frontend.

## 📁 Estructura del Proyecto

Este es un **monorepo** que contiene tanto el backend como el frontend:

```
granja-del-cerdo-api/
├── api/              # Backend API (Flask)
│   ├── app.py        # Aplicación principal Flask
│   ├── routes/       # Rutas de la API
│   ├── services/     # Lógica de negocio
│   ├── utils/        # Utilidades
│   ├── ml/           # Modelos de Machine Learning
│   ├── prisma/       # Schema de base de datos
│   ├── requirements.txt
│   └── ...
│
├── ui/               # Frontend (Streamlit)
│   ├── Inicio.py     # Página principal/login
│   ├── pages/        # Páginas de la aplicación
│   ├── utils/        # Utilidades del frontend
│   ├── requirements.txt
│   └── ...
│
└── shared/           # Código compartido (si aplica)
```

## 🚀 Instalación y Configuración

### Requisitos Previos

- Python 3.9 o superior
- PostgreSQL (para la base de datos)
- Git

### 1. Clonar el Repositorio

```bash
git clone https://github.com/callme-rojas/granja-del-cerdo-api.git
cd granja-del-cerdo-api
```

### 2. Configurar el Backend (API)

```bash
# Navegar al directorio de la API
cd api

# Crear entorno virtual (recomendado)
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env  # Si existe
# Editar .env con tus credenciales de base de datos

# Configurar Prisma (si usas Prisma)
prisma generate
prisma migrate dev

# Ejecutar la API
python app.py
# O si usas Flask directamente:
flask run --port 5000
```

La API estará disponible en: `http://localhost:5000`

### 3. Configurar el Frontend (UI)

```bash
# En una nueva terminal, navegar al directorio de la UI
cd ui

# Crear entorno virtual (recomendado)
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar la aplicación Streamlit
streamlit run Inicio.py
# O directamente:
streamlit run ui/Inicio.py
```

La UI estará disponible en: `http://localhost:8501`

## 📋 Funcionalidades

### API (Backend)
- ✅ Autenticación de usuarios
- ✅ Gestión de lotes
- ✅ Control de costos
- ✅ Predicciones ML
- ✅ Analytics y reportes
- ✅ Gestión de producción

### UI (Frontend)
- ✅ Dashboard interactivo
- ✅ Gestión de lotes
- ✅ Control de costos
- ✅ Predicciones ML visuales
- ✅ Tipos de costo
- ✅ Autenticación integrada

## 🔧 Configuración de Variables de Entorno

Crea un archivo `.env` en el directorio `api/` con las siguientes variables:

```env
DATABASE_URL=postgresql://usuario:contraseña@localhost:5432/granja_cerdo
JWT_SECRET_KEY=tu-clave-secreta-muy-segura
RATE_LIMIT=100 per minute
```

## 📝 Scripts Útiles

### Ejecutar ambos servicios (API + UI)

```bash
# Terminal 1 - API
cd api && python app.py

# Terminal 2 - UI
cd ui && streamlit run Inicio.py
```

### Ejecutar tests

```bash
# Tests de la API
cd api
pytest

# Tests de la UI (si existen)
cd ui
pytest
```

## 🗂️ Estructura de la API

- **`app.py`**: Configuración principal de Flask
- **`routes/`**: Endpoints de la API organizados por versión
- **`services/`**: Lógica de negocio
- **`utils/`**: Utilidades y helpers
- **`ml/`**: Modelos de Machine Learning y pipelines
- **`prisma/`**: Schema y migraciones de base de datos

## 🗂️ Estructura de la UI

- **`Inicio.py`**: Página de login e inicio
- **`pages/`**: Páginas de la aplicación (Dashboard, Lotes, Costos, etc.)
- **`utils/`**: Componentes reutilizables, estilos, autenticación
- **`config.py`**: Configuración de la aplicación

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto es privado y propiedad de [tu nombre/empresa].

## 👤 Autor

**callme-rojas**
- GitHub: [@callme-rojas](https://github.com/callme-rojas)

## 📞 Soporte

Para soporte, abre un issue en el repositorio de GitHub.

---

**Nota**: Asegúrate de configurar correctamente las variables de entorno y la conexión a la base de datos antes de ejecutar la aplicación.


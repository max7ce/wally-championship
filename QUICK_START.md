# 🏐 WALLY CHAMPIONSHIP - GUÍA DE INICIO RÁPIDO

## ⚡ Setup Express (5 minutos)

### 1️⃣ Configurar Backend

```bash
cd backend

# Instalar dependencias
pip install -r requirements.txt

# Crear archivo .env
cp .env.example .env

# Editar .env con tu DATABASE_URL de PostgreSQL
# Ejemplo: postgresql://user:pass@localhost:5432/wally_championship

# Ejecutar setup automático
python setup.py

# Iniciar servidor
uvicorn main:app --reload
```

Backend corriendo en: **http://localhost:8000**

### 2️⃣ Configurar Frontend

```bash
cd frontend

# Instalar dependencias
npm install

# Crear archivo .env
cp .env.example .env

# Editar .env (ya viene con localhost:8000 por defecto)

# Iniciar desarrollo
npm run dev
```

Frontend corriendo en: **http://localhost:5173**

---

## 🎮 Uso del Sistema

### PASO 1: Sorteo de Equipos (Admin)

1. Ir a **http://localhost:5173**
2. Login:
   - Usuario: `admin`
   - Contraseña: `admin123`
3. Presionar "🎲 Realizar Sorteo de Equipos"
4. Ingresar los 8 nombres de equipos
5. Presionar "REALIZAR SORTEO"
6. ✅ Sistema asigna aleatoriamente EQ1-EQ8

### PASO 2: Control de Cancha (Operador)

1. Login con:
   - `cancha1 / cancha1` → Cancha 1
   - `cancha2 / cancha2` → Cancha 2
   - `cancha3 / cancha3` → Cancha 3

2. **Durante el partido:**
   - 👆 Tocar IZQUIERDA → +1 punto LOCAL
   - 👆 Tocar DERECHA → +1 punto VISITANTE
   - ➖ Botón `-` → Corregir puntaje
   - ⏸️ PAUSE/CONTINUAR → Pausar/reanudar cronómetro
   - ✓ FINALIZAR → Guardar resultado y cargar siguiente

3. **Condiciones de victoria:**
   - Llegar a 25 puntos
   - Tener más puntos al terminar 14 minutos
   - Si empate → PUNTO DE ORO (próximo punto gana)

### PASO 3: Panel Público (Pantalla Grande)

1. Login:
   - Usuario: `publico`
   - Contraseña: `publico`

2. Ver:
   - **EN VIVO:** Partidos que se están jugando ahora
   - **TABLA:** Tabla de posiciones actualizada
   - **RESULTADOS:** Partidos finalizados

---

## 📊 Estructura del Proyecto

```
wally-championship/
├── backend/
│   ├── main.py              # FastAPI app principal
│   ├── database.py          # Conexión PostgreSQL
│   ├── fixture_generator.py # Algoritmo de fixture
│   ├── schema.sql           # Esquema de BD
│   ├── setup.py            # Script de inicialización
│   └── requirements.txt     # Dependencias Python
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Scoreboard.jsx      # Control de cancha ⭐
│   │   │   ├── Scoreboard.css
│   │   │   ├── PanelPublico.jsx    # Panel público
│   │   │   ├── PanelPublico.css
│   │   │   ├── Sorteo.jsx          # Sorteo equipos
│   │   │   ├── Sorteo.css
│   │   │   ├── Login.jsx
│   │   │   └── Login.css
│   │   ├── utils/
│   │   │   └── api.js              # Cliente API
│   │   ├── App.jsx                 # App principal
│   │   └── main.jsx                # Entry point
│   ├── package.json
│   └── vite.config.js
│
└── README.md
```

---

## 🚀 Deploy en Railway

### Backend

1. Crear proyecto en Railway
2. Agregar PostgreSQL
3. Conectar GitHub repo
4. Variables de entorno:
   ```
   DATABASE_URL=${DATABASE_URL}
   SECRET_KEY=cambiar_por_valor_aleatorio_seguro
   CORS_ORIGINS=https://tu-frontend.railway.app
   ```
5. Root Directory: `backend`
6. Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### Frontend

1. Nuevo servicio en Railway
2. Mismo repo GitHub
3. Variables de entorno:
   ```
   VITE_API_URL=https://tu-backend.railway.app
   ```
4. Root Directory: `frontend`
5. Build: `npm install && npm run build`
6. Start: `npx vite preview --host 0.0.0.0 --port $PORT`

---

## 🔧 Troubleshooting

### "ModuleNotFoundError: No module named 'psycopg2'"
```bash
pip install psycopg2-binary
```

### "Database connection failed"
- Verificar que PostgreSQL está corriendo
- Verificar DATABASE_URL en .env
- Probar conexión: `psql $DATABASE_URL`

### "CORS error" en frontend
- Verificar CORS_ORIGINS en backend .env
- Debe incluir: `http://localhost:5173`

### Cronómetro no inicia
- Verificar que el partido está en estado "en_juego"
- Revisar console del navegador (F12)

---

## 🎯 Datos de Prueba

**Usuarios:**
- admin / admin123
- cancha1 / cancha1
- cancha2 / cancha2
- cancha3 / cancha3
- publico / publico

**Equipos de ejemplo:**
1. Los Tigres
2. Águilas FC
3. Leones Dorados
4. Dragones Rojos
5. Halcones Azules
6. Panteras Negras
7. Lobos Grises
8. Cóndores Andinos

---

## 📞 Soporte

Si tienes problemas:
1. Revisar logs del backend: terminal donde corre uvicorn
2. Revisar console del navegador: F12 → Console
3. Verificar que BD está inicializada: `python setup.py`

¡Listo para arrancar! 🏐🔥

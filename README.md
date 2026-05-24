# 🏐 Wally Championship - Sistema de Gestión de Campeonato

Sistema completo para gestión de campeonato de Wally con 8 equipos, 3 canchas y 2 días de competencia.

## 🌟 Características

### ✅ Fixture Inteligente - FASE GRUPOS
- **Todos vs todos × 3 RONDAS** (84 sets totales)
  - 28 enfrentamientos únicos (todos contra todos)
  - Cada enfrentamiento se repite 3 veces
  - Rondas intercaladas en 2 días
- Distribución automática en 3 canchas paralelas
- **Restricciones garantizadas:**
  - Un equipo NO puede jugar en 2 canchas simultáneamente
  - Mínimo 1 slot de descanso entre partidos del mismo equipo

### 📊 Sistema de Puntos
- **+1 punto** por cada set ganado
- **0 puntos** por set perdido
- **-1 punto** por Walkover (no presentarse)
- Máximo teórico: 7 rivales × 3 sets = **21 puntos**

### 🏆 Fase Final
- **Clasifican:** Top 4 equipos con más puntos
- **Semifinales:** 
  - 1° vs 4° (Cancha 1, mejor de 3 sets)
  - 2° vs 3° (Cancha 2, mejor de 3 sets)
- **Final:** 
  - Ganador Semi1 vs Ganador Semi2 (Cancha 1, mejor de 3 sets)
- Sets de fase final se juegan **seguidos** (sin cambio de cancha)

### 🎲 Sorteo de Equipos
- Interfaz visual para ingresar 8 equipos
- Sorteo aleatorio con animación
- Asignación automática a posiciones EQ1-EQ8

### 📊 Scoreboard por Cancha
- **Botón INICIO:** Cronómetro se activa manualmente
- **Control táctil:** Tocar lado izquierdo/derecho para sumar puntos
- **Cronómetro:** Cuenta regresiva de 14:00 → 00:00
- **Punto de Oro:** Activación automática en caso de empate
- **WO (Walkover):** Botón para registrar ausencia (25-0 automático)
- **Auto-guardado:** Sincronización cada 3 segundos
- Nombres de equipos como sello de agua
- Números grandes y claros

### 📺 Panel Público
- Vista EN VIVO de partidos en juego
- Tabla de posiciones en tiempo real (sistema de puntos por sets)
- Resultados finalizados
- Vista de Fase Final (semifinales y final)
- Diseño responsive para pantalla gigante

## 🚀 Tecnologías

- **Backend:** FastAPI + PostgreSQL
- **Frontend:** React + Vite
- **Deploy:** Railway
- **Base de Datos:** PostgreSQL 15

## 📦 Instalación Local

### Backend

```bash
cd backend
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tu DATABASE_URL de PostgreSQL

# Inicializar base de datos
python -c "from database import init_db, create_default_users; init_db(); create_default_users()"

# Generar fixture
python -c "
from database import get_db
from fixture_generator import generate_fixture, validate_fixture
from database import execute_many

slots, partidos = generate_fixture()
validate_fixture(partidos)

# Insertar en BD (código en main.py /setup/generate-fixture)
"

# Ejecutar servidor
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd frontend
npm install

# Configurar variables de entorno
cp .env.example .env
# Editar .env con la URL de tu backend

# Ejecutar en desarrollo
npm run dev

# Build para producción
npm run build
```

## 🎮 Uso del Sistema

### 1. Setup Inicial (Admin)

1. **Inicializar BD:**
   ```
   POST /setup/init-db
   ```

2. **Generar Fixture:**
   ```
   POST /setup/generate-fixture
   ```

3. **Realizar Sorteo:**
   - Login como `admin / admin123`
   - Ingresar nombres de los 8 equipos
   - Presionar "REALIZAR SORTEO"

### 2. Control de Cancha

Login con:
- `cancha1 / cancha1` → Control Cancha 1
- `cancha2 / cancha2` → Control Cancha 2
- `cancha3 / cancha3` → Control Cancha 3

**Flujo durante partido:**
1. Se carga automáticamente el próximo partido pendiente
2. Tocar lado izquierdo → Suma punto LOCAL
3. Tocar lado derecho → Suma punto VISITANTE
4. Botón `-` → Corregir puntaje
5. Cronómetro se inicia automáticamente al primer punto
6. PAUSE/CONTINUAR → Pausar/reanudar tiempo
7. Al llegar a 25 puntos o terminar tiempo → Auto-finalizar
8. Si termina empatado → PUNTO DE ORO (próximo punto gana)
9. Presionar "FINALIZAR PARTIDO" → Guarda resultado y carga siguiente

### 3. Panel Público

Login con:
- `publico / publico`

Pestañas:
- **EN VIVO:** Partidos en juego ahora
- **TABLA:** Tabla de posiciones
- **RESULTADOS:** Partidos finalizados

## 📊 Base de Datos

### Tablas Principales

- `equipos` - 8 equipos del campeonato
- `slots_tiempo` - 84 slots (2 días × 14 slots × 3 canchas)
- `partidos` - 28 enfrentamientos asignados a slots
- `resultados` - Puntajes y estados de cada partido
- `usuarios` - Autenticación (cancha1, cancha2, cancha3, publico, admin)

### Vistas

- `v_fixture` - Fixture completo con nombres de equipos
- `v_standings` - Tabla de posiciones calculada

## 🌐 Deploy en Railway

### Backend

1. Crear nuevo proyecto en Railway
2. Agregar servicio PostgreSQL
3. Conectar repositorio GitHub
4. Configurar variables de entorno:
   ```
   DATABASE_URL=${DATABASE_URL}
   SECRET_KEY=tu_secret_key_generado
   CORS_ORIGINS=https://tu-frontend.railway.app
   ```
5. Root Directory: `backend`
6. Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### Frontend

1. Crear nuevo servicio en Railway
2. Conectar mismo repositorio
3. Configurar variables de entorno:
   ```
   VITE_API_URL=https://tu-backend.railway.app
   ```
4. Root Directory: `frontend`
5. Build Command: `npm install && npm run build`
6. Start Command: `npx vite preview --host 0.0.0.0 --port $PORT`

## 🎯 Endpoints API

### Setup
- `POST /setup/init-db` - Inicializar esquema
- `POST /setup/generate-fixture` - Generar fixture

### Equipos
- `GET /equipos` - Listar equipos
- `POST /equipos/sorteo` - Sortear equipos

### Fixture
- `GET /fixture` - Fixture completo
- `GET /fixture/cancha/{cancha}` - Fixture por cancha (auth)

### Partidos
- `GET /partidos/proximo/{cancha}` - Próximo partido (auth)
- `POST /partidos/estado` - Actualizar estado
- `POST /partidos/score` - Actualizar puntaje
- `POST /partidos/{partido_id}/finalizar` - Finalizar partido

### Público
- `GET /standings` - Tabla de posiciones
- `GET /partidos/en-vivo` - Partidos en juego
- `GET /partidos/resultados` - Resultados finalizados

## 🔐 Usuarios por Defecto

| Username | Password | Tipo | Acceso |
|----------|----------|------|--------|
| cancha1 | cancha1 | cancha1 | Scoreboard Cancha 1 |
| cancha2 | cancha2 | cancha2 | Scoreboard Cancha 2 |
| cancha3 | cancha3 | cancha3 | Scoreboard Cancha 3 |
| publico | publico | publico | Panel Público |
| admin | admin123 | admin | Panel Admin + Sorteo |

## 📱 Modo de Uso Móvil

- **Orientación:** Horizontal (landscape) obligatoria
- **Gestos:** Toques en pantalla completa
- **Auto-save:** Cada 3 segundos cuando está en juego
- **Offline:** No soportado (requiere conexión continua)

## 🎨 Diseño

- **Tema:** Dark mode deportivo
- **Colores principales:**
  - Verde neón (#00ff88) - Acentos
  - Fondo oscuro (#0a0a0a)
  - Rojo (#ff0000) - Alertas
  - Dorado (#ffd700) - Punto de Oro

## 🐛 Troubleshooting

### El fixture no se genera correctamente
- Verificar que hay suficientes slots disponibles (mínimo 84)
- Revisar logs del algoritmo de asignación
- Ejecutar `/setup/generate-fixture` de nuevo

### Cronómetro no inicia
- Verificar que el partido está en estado "en_juego"
- Verificar que `isPaused` está en `false`
- Revisar console del navegador

### Partidos no se guardan
- Verificar autenticación del usuario
- Verificar que `partido_id` es válido
- Revisar logs del backend

## 📄 Licencia

MIT - Creado para Campeonato Wally Championship 2025

## 👨‍💻 Autor

Sistema desarrollado con FastAPI + React + PostgreSQL
Optimizado para uso en dispositivos móviles (horizontal)

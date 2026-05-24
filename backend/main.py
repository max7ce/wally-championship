"""
Wally Championship API
FastAPI backend para gestión de campeonato de Wally
"""
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
from typing import List, Optional
import os
from passlib.context import CryptContext
import secrets

from database import get_db, execute_query, execute_many, init_db, create_default_users
from fixture_generator import generate_fixture, validate_fixture

# ============================================
# App Configuration
# ============================================
app = FastAPI(
    title="Wally Championship API",
    description="API para gestión de campeonato de Wally - 8 equipos, 3 canchas, 2 días",
    version="1.0.0"
)

# CORS
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBasic()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ============================================
# Pydantic Models
# ============================================
class Equipo(BaseModel):
    nombre: str

class EquipoResponse(BaseModel):
    id: int
    nombre: str
    posicion: Optional[int]

class SorteoRequest(BaseModel):
    equipos: List[str]  # Lista de 8 nombres

class PartidoResponse(BaseModel):
    partido_id: int
    dia: int
    numero_slot: int
    hora_inicio: str
    cancha: int
    equipo_local: str
    equipo_visitante: str
    ronda: Optional[int]
    estado: str
    puntos_local: Optional[int]
    puntos_visitante: Optional[int]
    punto_de_oro: Optional[bool]

class ScoreUpdate(BaseModel):
    partido_id: int
    puntos_local: int
    puntos_visitante: int
    punto_de_oro: bool = False
    terminado_por: Optional[str] = None  # 'puntos', 'tiempo', 'punto_oro'
    tiempo_jugado: Optional[int] = None  # segundos

class EstadoUpdate(BaseModel):
    partido_id: int
    estado: str  # 'pendiente', 'en_juego', 'finalizado'

class StandingsResponse(BaseModel):
    nombre: str
    puntos: int
    jugados: int
    ganados: int
    empatados: int
    perdidos: int
    puntos_favor: int
    puntos_contra: int
    diferencia: int


# ============================================
# Authentication
# ============================================
def verify_user(credentials: HTTPBasicCredentials = Depends(security)):
    """Verificar credenciales de usuario"""
    query = "SELECT * FROM usuarios WHERE username = %s"
    users = execute_query(query, (credentials.username,))
    
    if not users:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado",
            headers={"WWW-Authenticate": "Basic"},
        )
    
    user = users[0]
    
    if not pwd_context.verify(credentials.password, user['password_hash']):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Contraseña incorrecta",
            headers={"WWW-Authenticate": "Basic"},
        )
    
    return user


# ============================================
# Endpoints
# ============================================

@app.get("/")
def root():
    """Health check"""
    return {"status": "ok", "message": "Wally Championship API"}


@app.post("/setup/init-db")
def setup_database():
    """Inicializar base de datos (solo desarrollo)"""
    try:
        init_db()
        create_default_users()
        return {"status": "success", "message": "Database initialized"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/setup/generate-fixture")
def setup_generate_fixture():
    """Generar fixture completo del campeonato"""
    try:
        # Generar fixture
        slots, partidos = generate_fixture()
        
        # Validar fixture
        is_valid = validate_fixture(partidos)
        if not is_valid:
            raise HTTPException(
                status_code=500, 
                detail="El fixture generado no cumple las restricciones"
            )
        
        # Insertar slots en BD
        slot_query = """
            INSERT INTO slots_tiempo (id, dia, numero_slot, hora_inicio, cancha)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT DO NOTHING
        """
        slot_params = [
            (s['id'], s['dia'], s['numero_slot'], s['hora_inicio'], s['cancha'])
            for s in slots
        ]
        execute_many(slot_query, slot_params)
        
        # Insertar partidos (con equipos genéricos EQ1-EQ8)
        # Primero crear equipos genéricos si no existen
        for i in range(1, 9):
            execute_query(
                "INSERT INTO equipos (nombre, posicion) VALUES (%s, %s) ON CONFLICT DO NOTHING",
                (f"EQ{i}", i),
                fetch=False
            )
        
        # Insertar partidos
        partido_query = """
            INSERT INTO partidos (slot_id, equipo_local_id, equipo_visitante_id)
            VALUES (%s, %s, %s)
        """
        partido_params = [
            (p['slot_id'], p['equipo_local'], p['equipo_visitante'])
            for p in partidos
        ]
        execute_many(partido_query, partido_params)
        
        return {
            "status": "success",
            "slots_created": len(slots),
            "partidos_created": len(partidos),
            "message": "Fixture generado correctamente"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/equipos/sorteo")
def sortear_equipos(request: SorteoRequest):
    """
    Realizar sorteo de equipos y asignar a posiciones
    Reemplaza los equipos genéricos (EQ1-EQ8) con nombres reales
    """
    if len(request.equipos) != 8:
        raise HTTPException(status_code=400, detail="Se requieren exactamente 8 equipos")
    
    try:
        # Mezclar equipos aleatoriamente
        import random
        equipos_mezclados = request.equipos.copy()
        random.shuffle(equipos_mezclados)
        
        # Actualizar equipos en BD
        for posicion, nombre in enumerate(equipos_mezclados, 1):
            execute_query(
                """
                UPDATE equipos 
                SET nombre = %s 
                WHERE posicion = %s
                """,
                (nombre, posicion),
                fetch=False
            )
        
        # Obtener equipos actualizados
        equipos = execute_query("SELECT * FROM equipos ORDER BY posicion")
        
        return {
            "status": "success",
            "equipos": equipos,
            "message": "Sorteo realizado correctamente"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/equipos", response_model=List[EquipoResponse])
def listar_equipos():
    """Listar todos los equipos"""
    equipos = execute_query("SELECT * FROM equipos ORDER BY posicion")
    return equipos


@app.get("/fixture")
def obtener_fixture():
    """Obtener fixture completo"""
    fixture = execute_query("SELECT * FROM v_fixture ORDER BY dia, numero_slot, cancha")
    return fixture


@app.get("/fixture/cancha/{cancha}")
def obtener_fixture_cancha(cancha: int, user = Depends(verify_user)):
    """Obtener fixture de una cancha específica (requiere autenticación)"""
    if cancha not in [1, 2, 3]:
        raise HTTPException(status_code=400, detail="Cancha inválida (1-3)")
    
    # Verificar que el usuario tenga acceso a esta cancha
    if user['tipo'] not in ['admin', f'cancha{cancha}']:
        raise HTTPException(status_code=403, detail="No tienes acceso a esta cancha")
    
    fixture = execute_query(
        "SELECT * FROM v_fixture WHERE cancha = %s ORDER BY dia, numero_slot",
        (cancha,)
    )
    return fixture


@app.get("/partidos/proximo/{cancha}")
def obtener_proximo_partido(cancha: int, user = Depends(verify_user)):
    """Obtener el próximo partido pendiente o en juego de una cancha"""
    if cancha not in [1, 2, 3]:
        raise HTTPException(status_code=400, detail="Cancha inválida")
    
    # Verificar acceso
    if user['tipo'] not in ['admin', f'cancha{cancha}']:
        raise HTTPException(status_code=403, detail="No tienes acceso a esta cancha")
    
    # Buscar partido en juego
    partido_en_juego = execute_query(
        """
        SELECT * FROM v_fixture 
        WHERE cancha = %s AND estado = 'en_juego'
        LIMIT 1
        """,
        (cancha,)
    )
    
    if partido_en_juego:
        return partido_en_juego[0]
    
    # Si no hay en juego, buscar el siguiente pendiente
    proximo = execute_query(
        """
        SELECT * FROM v_fixture 
        WHERE cancha = %s AND estado = 'pendiente'
        ORDER BY dia, numero_slot
        LIMIT 1
        """,
        (cancha,)
    )
    
    if not proximo:
        return {"message": "No hay más partidos pendientes en esta cancha"}
    
    return proximo[0]


@app.post("/partidos/estado")
def actualizar_estado_partido(update: EstadoUpdate, user = Depends(verify_user)):
    """Actualizar estado de un partido (pendiente -> en_juego -> finalizado)"""
    # Verificar que el partido existe
    partido = execute_query(
        "SELECT * FROM partidos WHERE id = %s",
        (update.partido_id,)
    )
    
    if not partido:
        raise HTTPException(status_code=404, detail="Partido no encontrado")
    
    # Crear o actualizar resultado
    execute_query(
        """
        INSERT INTO resultados (partido_id, estado, updated_at)
        VALUES (%s, %s, NOW())
        ON CONFLICT (partido_id) 
        DO UPDATE SET estado = %s, updated_at = NOW()
        """,
        (update.partido_id, update.estado, update.estado),
        fetch=False
    )
    
    return {"status": "success", "partido_id": update.partido_id, "estado": update.estado}


@app.post("/partidos/score")
def actualizar_score(update: ScoreUpdate, user = Depends(verify_user)):
    """Actualizar score de un partido"""
    # Verificar que el partido existe
    partido = execute_query(
        "SELECT * FROM partidos WHERE id = %s",
        (update.partido_id,)
    )
    
    if not partido:
        raise HTTPException(status_code=404, detail="Partido no encontrado")
    
    # Actualizar score
    execute_query(
        """
        INSERT INTO resultados 
        (partido_id, puntos_local, puntos_visitante, punto_de_oro, terminado_por, tiempo_jugado, estado, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s, 'en_juego', NOW())
        ON CONFLICT (partido_id) 
        DO UPDATE SET 
            puntos_local = %s,
            puntos_visitante = %s,
            punto_de_oro = %s,
            terminado_por = %s,
            tiempo_jugado = %s,
            updated_at = NOW()
        """,
        (
            update.partido_id, update.puntos_local, update.puntos_visitante,
            update.punto_de_oro, update.terminado_por, update.tiempo_jugado,
            update.puntos_local, update.puntos_visitante,
            update.punto_de_oro, update.terminado_por, update.tiempo_jugado
        ),
        fetch=False
    )
    
    return {"status": "success", "partido_id": update.partido_id}


@app.post("/partidos/{partido_id}/finalizar")
def finalizar_partido(partido_id: int, user = Depends(verify_user)):
    """Marcar un partido como finalizado"""
    execute_query(
        """
        UPDATE resultados 
        SET estado = 'finalizado', updated_at = NOW()
        WHERE partido_id = %s
        """,
        (partido_id,),
        fetch=False
    )
    
    return {"status": "success", "partido_id": partido_id, "estado": "finalizado"}


@app.get("/standings")
def obtener_tabla_posiciones():
    """Obtener tabla de posiciones"""
    standings = execute_query("SELECT * FROM v_standings")
    return standings


@app.get("/partidos/en-vivo")
def obtener_partidos_en_vivo():
    """Obtener todos los partidos que están en juego ahora"""
    partidos = execute_query(
        """
        SELECT * FROM v_fixture 
        WHERE estado = 'en_juego'
        ORDER BY cancha
        """
    )
    return partidos


@app.get("/partidos/resultados")
def obtener_resultados():
    """Obtener todos los partidos finalizados"""
    resultados = execute_query(
        """
        SELECT * FROM v_fixture 
        WHERE estado = 'finalizado'
        ORDER BY dia, numero_slot, cancha
        """
    )
    return resultados


# ============================================
# Startup Event
# ============================================
@app.on_event("startup")
async def startup_event():
    """Ejecutar al iniciar la aplicación"""
    print("🏐 Wally Championship API iniciada")
    print(f"📍 CORS permitido desde: {CORS_ORIGINS}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

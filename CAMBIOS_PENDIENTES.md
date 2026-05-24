# 🔄 CAMBIOS PENDIENTES - Frontend (Scoreboard y PanelPublico)

## 📋 RESUMEN DE LO QUE SE MODIFICÓ

### Backend ✅ (COMPLETADO)
- schema.sql: Agregados campos `fase`, `serie_numero`, `es_walkover`, `equipo_ausente_id`
- fixture_generator.py: Genera 84 partidos (3 rondas de 28)
- fase_final.py: Nuevo módulo para semifinales y final
- main.py: Endpoints de fase final agregados
- v_standings: Sistema de puntos cambiado (1 pt por set ganado, -1 por WO)

---

## 🎯 CAMBIOS NECESARIOS EN SCOREBOARD.JSX

### 1. Agregar botón INICIO para cronómetro

```jsx
// En la sección del cronómetro, agregar:
{!cronoIniciado ? (
  <button 
    onClick={() => {
      setCronoIniciado(true);
      setIsPaused(false);
    }}
    className="btn-inicio"
  >
    ▶ INICIAR PARTIDO
  </button>
) : (
  <button 
    onClick={togglePausa}
    className={`btn-pause ${isPaused ? 'paused' : ''}`}
  >
    {isPaused ? '▶ CONTINUAR' : '⏸ PAUSE'}
  </button>
)}
```

### 2. Agregar botón WO (Walkover)

```jsx
// Agregar en el footer, antes del botón FINALIZAR:
<button 
  onClick={() => setMostrarModalWO(true)}
  className="btn-wo"
  disabled={partido.estado === 'finalizado'}
>
  🚫 WALKOVER (WO)
</button>
```

### 3. Agregar Modal de WO

```jsx
// Al final del componente, antes del closing div:
{mostrarModalWO && (
  <div className="modal-wo">
    <div className="modal-content">
      <h2>¿Qué equipo NO se presentó?</h2>
      <button 
        onClick={() => registrarWO(partido.equipo_local_id)}
        className="btn-wo-equipo"
      >
        {partido.equipo_local}
      </button>
      <button 
        onClick={() => registrarWO(partido.equipo_visitante_id)}
        className="btn-wo-equipo"
      >
        {partido.equipo_visitante}
      </button>
      <button 
        onClick={() => setMostrarModalWO(false)}
        className="btn-cancelar"
      >
        Cancelar
      </button>
    </div>
  </div>
)}
```

### 4. Función registrarWO

```jsx
const registrarWO = async (equipoAusenteId) => {
  try {
    // WO = 25-0 a favor del presente
    const esLocal = equipoAusenteId === partido.equipo_local_id;
    
    await api.post('/partidos/score', {
      partido_id: partido.partido_id,
      puntos_local: esLocal ? 0 : 25,
      puntos_visitante: esLocal ? 25 : 0,
      punto_de_oro: false,
      es_walkover: true,
      equipo_ausente_id: equipoAusenteId,
      terminado_por: 'walkover',
      tiempo_jugado: 0
    });
    
    await api.post(`/partidos/${partido.partido_id}/finalizar`);
    
    setMostrarModalWO(false);
    
    // Cargar siguiente partido
    setTimeout(() => {
      cargarProximoPartido();
      resetearEstado();
    }, 2000);
    
  } catch (error) {
    console.error('Error registrando WO:', error);
  }
};

const resetearEstado = () => {
  setPuntosLocal(0);
  setPuntosVisitante(0);
  setTiempo(14 * 60);
  setPuntoDeOro(false);
  setIsPaused(true);
  setCronoIniciado(false);
};
```

### 5. Mostrar información de fase/serie

```jsx
// En el header, agregar:
<div className="fase-info">
  {partido.fase === 'grupos' && (
    <span className="badge-fase">FASE GRUPOS - RONDA {partido.ronda}</span>
  )}
  {partido.fase === 'semifinal' && (
    <span className="badge-fase semifinal">
      SEMIFINAL - SET {partido.serie_numero}/3
    </span>
  )}
  {partido.fase === 'final' && (
    <span className="badge-fase final">
      🏆 FINAL - SET {partido.serie_numero}/3
    </span>
  )}
</div>
```

---

## 🎨 ESTILOS CSS PARA AGREGAR

```css
/* Botón Inicio */
.btn-inicio {
  padding: 1.5rem 3rem;
  font-size: 1.5rem;
  font-weight: bold;
  background: linear-gradient(135deg, #00ff88 0%, #00cc6a 100%);
  border: none;
  color: #000;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s;
  text-transform: uppercase;
  animation: pulse-inicio 1.5s infinite;
}

@keyframes pulse-inicio {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.05); }
}

/* Botón WO */
.btn-wo {
  padding: 1rem 2rem;
  font-size: 1.2rem;
  font-weight: bold;
  background: rgba(255, 165, 0, 0.2);
  border: 2px solid #ffa500;
  color: #ffa500;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s;
  text-transform: uppercase;
}

.btn-wo:hover:not(:disabled) {
  background: rgba(255, 165, 0, 0.4);
}

/* Modal WO */
.modal-wo {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: rgba(20, 20, 20, 0.95);
  border: 2px solid #ffa500;
  border-radius: 20px;
  padding: 3rem;
  display: flex;
  flex-direction: column;
  gap: 2rem;
  text-align: center;
}

.modal-content h2 {
  font-size: 2rem;
  color: #ffa500;
}

.btn-wo-equipo {
  padding: 1.5rem 3rem;
  font-size: 1.5rem;
  font-weight: bold;
  background: rgba(255, 0, 0, 0.2);
  border: 2px solid #ff0000;
  color: #ff0000;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-wo-equipo:hover {
  background: rgba(255, 0, 0, 0.4);
  transform: scale(1.05);
}

.btn-cancelar {
  padding: 1rem 2rem;
  background: rgba(255, 255, 255, 0.1);
  border: 2px solid rgba(255, 255, 255, 0.3);
  color: #fff;
  border-radius: 12px;
  cursor: pointer;
}

/* Badge Fase */
.fase-info {
  margin-top: 0.5rem;
}

.badge-fase {
  padding: 0.5rem 1.5rem;
  border-radius: 8px;
  font-weight: bold;
  font-size: 0.9rem;
  display: inline-block;
  background: rgba(0, 119, 255, 0.2);
  border: 2px solid #0077ff;
  color: #0077ff;
}

.badge-fase.semifinal {
  background: rgba(255, 170, 0, 0.2);
  border-color: #ffaa00;
  color: #ffaa00;
}

.badge-fase.final {
  background: rgba(255, 215, 0, 0.2);
  border-color: #ffd700;
  color: #ffd700;
}
```

---

## 📊 CAMBIOS EN PANELPUBLICO.JSX

### 1. Actualizar columnas de tabla

Cambiar:
```jsx
<th>PJ</th>
<th>G</th>
<th>E</th>
<th>P</th>
```

Por:
```jsx
<th>Sets J</th>
<th>Sets G</th>
<th>Sets P</th>
<th>WO</th>
```

### 2. Actualizar renderizado de datos

Cambiar:
```jsx
<td>{equipo.jugados}</td>
<td>{equipo.ganados}</td>
<td>{equipo.empatados}</td>
<td>{equipo.perdidos}</td>
```

Por:
```jsx
<td>{equipo.sets_jugados}</td>
<td>{equipo.sets_ganados}</td>
<td>{equipo.sets_perdidos}</td>
<td className={equipo.walkovers > 0 ? 'wo-warning' : ''}>{equipo.walkovers}</td>
```

### 3. Agregar pestaña FASE FINAL

```jsx
<button 
  className={vista === 'fase-final' ? 'active' : ''}
  onClick={() => setVista('fase-final')}
>
  🏆 FASE FINAL
</button>
```

### 4. Renderizar vista de Fase Final

```jsx
{vista === 'fase-final' && (
  <div className="fase-final-view">
    {/* Aquí renderizar clasificados, semifinales, final */}
    {/* Llamar a /fase-final/estado para obtener info */}
  </div>
)}
```

---

## ✅ CHECKLIST DE IMPLEMENTACIÓN

- [ ] Modificar Scoreboard.jsx con botón INICIO
- [ ] Agregar botón y modal WO
- [ ] Agregar función registrarWO
- [ ] Mostrar badges de fase/serie
- [ ] Actualizar Scoreboard.css con nuevos estilos
- [ ] Modificar PanelPublico.jsx con nuevas columnas
- [ ] Agregar vista Fase Final en PanelPublico
- [ ] Probar localmente con `python setup.py`
- [ ] Verificar que se generan 84 partidos (3 rondas)
- [ ] Probar WO y verificar -1 punto en tabla
- [ ] Probar generar semifinales cuando termine fase grupos
- [ ] Probar generar final cuando terminen semifinales

---

## 🚀 COMANDOS PARA PROBAR

```bash
# Backend
cd backend
python setup.py  # Esto generará las 3 rondas
uvicorn main:app --reload

# Frontend
cd frontend
npm run dev

# Verificar partidos generados
# Login como admin → Ver fixture
# Debe haber 84 partidos en fase grupos
```

---

¿Todo claro? Una vez que hagas estos cambios, el sistema estará 100% completo con:
- 3 rondas de todos vs todos (84 sets)
- Sistema de puntos correcto (1 pt por set, -1 por WO)
- Semifinales automáticas (1° vs 4°, 2° vs 3°)
- Final automática (mejor de 3)
- Cronómetro manual con botón INICIO
- Walkover funcional

🏐🔥

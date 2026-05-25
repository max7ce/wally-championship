import { useState, useEffect, useRef } from 'react';
import { api } from '../utils/api';
import './Scoreboard.css';

const Scoreboard = ({ cancha, onLogout }) => {
  const [partido, setPartido] = useState(null);
  const [puntosLocal, setPuntosLocal] = useState(0);
  const [puntosVisitante, setPuntosVisitante] = useState(0);
  const [tiempo, setTiempo] = useState(14 * 60); // 14 minutos en segundos
  const [isPaused, setIsPaused] = useState(true);
  const [puntoDeOro, setPuntoDeOro] = useState(false);
  const [loading, setLoading] = useState(true);
  const [mensaje, setMensaje] = useState('');
  const [mostrarModalWO, setMostrarModalWO] = useState(false);

  const audioRef = useRef(null);
  const timerRef = useRef(null);
  const autosaveRef = useRef(null);

  // Cargar próximo partido
  useEffect(() => {
    cargarProximoPartido();
  }, []);

  const cargarProximoPartido = async () => {
    try {
      setLoading(true);
      const data = await api.get(`/partidos/proximo/${cancha}`);

      if (data.message) {
        setMensaje(data.message);
        setPartido(null);
      } else {
        setPartido(data);
        setPuntosLocal(data.puntos_local || 0);
        setPuntosVisitante(data.puntos_visitante || 0);
        setPuntoDeOro(data.punto_de_oro || false);

        // Si el partido está en juego, reanudar cronómetro
        if (data.estado === 'en_juego') {
          setIsPaused(false);
        }
      }
    } catch (error) {
      console.error('Error cargando partido:', error);
      setMensaje('Error al cargar partido');
    } finally {
      setLoading(false);
    }
  };

  // Cronómetro
  useEffect(() => {
    if (!isPaused && tiempo > 0) {
      timerRef.current = setInterval(() => {
        setTiempo(prev => {
          if (prev <= 1) {
            emitirPitido();
            verificarEmpate(puntosLocal, puntosVisitante);
            return 0;
          }
          return prev - 1;
        });
      }, 1000);
    }

    return () => {
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
    };
  }, [isPaused, tiempo]);

  // Auto-guardar cada 3 segundos cuando está en juego
  useEffect(() => {
    if (!isPaused && partido) {
      autosaveRef.current = setInterval(() => {
        guardarScore(false); // false = no finalizar
      }, 3000);
    }

    return () => {
      if (autosaveRef.current) {
        clearInterval(autosaveRef.current);
      }
    };
  }, [isPaused, partido, puntosLocal, puntosVisitante]);

  const emitirPitido = () => {
    // Crear pitido con Web Audio API
    const audioContext = new (window.AudioContext || window.webkitAudioContext)();
    const oscillator = audioContext.createOscillator();
    const gainNode = audioContext.createGain();

    oscillator.connect(gainNode);
    gainNode.connect(audioContext.destination);

    oscillator.frequency.value = 800;
    oscillator.type = 'sine';

    gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
    gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.5);

    oscillator.start(audioContext.currentTime);
    oscillator.stop(audioContext.currentTime + 0.5);
  };

  const verificarEmpate = (local, visitante) => {
    if (local === visitante) {
      setPuntoDeOro(true);
      emitirPitido();
      setTimeout(() => emitirPitido(), 300);
    }
  };

  const verificarGanador = (local, visitante) => {
    // Ganar por puntos (25)
    if (local >= 25 || visitante >= 25) {
      return true;
    }

    // Punto de oro
    if (puntoDeOro && local !== visitante) {
      return true;
    }

    return false;
  };

  const sumarPuntoLocal = async () => {
    if (!partido || partido.estado === 'finalizado') return;

    const nuevoPuntaje = puntosLocal + 1;
    setPuntosLocal(nuevoPuntaje);

    // Iniciar partido si está pendiente
    if (partido.estado === 'pendiente') {
      await api.post('/partidos/estado', {
        partido_id: partido.partido_id,
        estado: 'en_juego'
      });
      setPartido({ ...partido, estado: 'en_juego' });
      setIsPaused(false);
    }

    if (verificarGanador(nuevoPuntaje, puntosVisitante)) {
      finalizarPartido();
    }
  };

  const sumarPuntoVisitante = async () => {
    if (!partido || partido.estado === 'finalizado') return;

    const nuevoPuntaje = puntosVisitante + 1;
    setPuntosVisitante(nuevoPuntaje);

    // Iniciar partido si está pendiente
    if (partido.estado === 'pendiente') {
      await api.post('/partidos/estado', {
        partido_id: partido.partido_id,
        estado: 'en_juego'
      });
      setPartido({ ...partido, estado: 'en_juego' });
      setIsPaused(false);
    }

    if (verificarGanador(puntosLocal, nuevoPuntaje)) {
      finalizarPartido();
    }
  };

  const restarPuntoLocal = () => {
    if (puntosLocal > 0) {
      setPuntosLocal(puntosLocal - 1);
    }
  };

  const restarPuntoVisitante = () => {
    if (puntosVisitante > 0) {
      setPuntosVisitante(puntosVisitante - 1);
    }
  };

  const togglePausa = () => {
    setIsPaused(!isPaused);
  };

  const guardarScore = async (finalizar = false) => {
    if (!partido) return;

    try {
      let terminadoPor = null;
      if (finalizar) {
        if (puntosLocal >= 25 || puntosVisitante >= 25) {
          terminadoPor = 'puntos';
        } else if (puntoDeOro) {
          terminadoPor = 'punto_oro';
        } else {
          terminadoPor = 'tiempo';
        }
      }

      await api.post('/partidos/score', {
        partido_id: partido.partido_id,
        puntos_local: puntosLocal,
        puntos_visitante: puntosVisitante,
        punto_de_oro: puntoDeOro,
        terminado_por: terminadoPor,
        tiempo_jugado: (14 * 60) - tiempo
      });

      if (finalizar) {
        await api.post(`/partidos/${partido.partido_id}/finalizar`);
      }
    } catch (error) {
      console.error('Error guardando score:', error);
    }
  };

  const finalizarPartido = async () => {
    setIsPaused(true);
    await guardarScore(true);

    // Mostrar resultado final brevemente
    setTimeout(() => {
      cargarProximoPartido();
      setPuntosLocal(0);
      setPuntosVisitante(0);
      setTiempo(14 * 60);
      setPuntoDeOro(false);
    }, 3000);
  };

  const registrarWalkOver = async (equipoAusente) => {
    if (!partido) return;

    try {
      // Determinar puntaje según quién faltó
      const esLocalAusente = equipoAusente === 'local';
      const puntosLocal = esLocalAusente ? 0 : 25;
      const puntosVisitante = esLocalAusente ? 25 : 0;

      // Actualizar estado a en_juego primero
      await api.post('/partidos/estado', {
        partido_id: partido.partido_id,
        estado: 'en_juego'
      });

      // Guardar score de WO (25-0)
      await api.post('/partidos/score', {
        partido_id: partido.partido_id,
        puntos_local: puntosLocal,
        puntos_visitante: puntosVisitante,
        punto_de_oro: false,
        terminado_por: 'walkover',
        tiempo_jugado: 0
      });

      // Finalizar partido
      await api.post(`/partidos/${partido.partido_id}/finalizar`);

      // Cerrar modal
      setMostrarModalWO(false);

      // Mostrar resultado brevemente y cargar siguiente
      setPuntosLocal(puntosLocal);
      setPuntosVisitante(puntosVisitante);
      setTimeout(() => {
        cargarProximoPartido();
        setPuntosLocal(0);
        setPuntosVisitante(0);
        setTiempo(14 * 60);
        setPuntoDeOro(false);
      }, 2000);

    } catch (error) {
      console.error('Error registrando WO:', error);
      alert('Error al registrar Walk Over');
    }
  };

  const formatearTiempo = (segundos) => {
    const mins = Math.floor(segundos / 60);
    const secs = segundos % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  if (loading) {
    return <div className="scoreboard-loading">Cargando partido...</div>;
  }

  if (!partido) {
    return (
      <div className="scoreboard-mensaje">
        <h2>{mensaje}</h2>
        <button onClick={onLogout} className="btn-logout">Cerrar Sesión</button>
      </div>
    );
  }

  return (
    <div className="scoreboard">
      {/* Header */}
      <div className="scoreboard-header">
        <div className="info">
          <span className="cancha">CANCHA {cancha}</span>
          <span className="horario">
            Día {partido.dia} - Slot {partido.numero_slot} - {partido.hora_inicio}
          </span>
        </div>
        <button onClick={onLogout} className="btn-logout-mini">✕</button>
      </div>

      {/* Cronómetro */}
      <div className={`cronometro ${tiempo <= 60 ? 'warning' : ''} ${tiempo === 0 ? 'finished' : ''}`}>
        <div className="tiempo">{formatearTiempo(tiempo)}</div>
        <div className="cronometro-controls">
          <button
            onClick={togglePausa}
            className={`btn-pause ${isPaused ? 'paused' : ''}`}
          >
            {isPaused ? '▶ CONTINUAR' : '⏸ PAUSE'}
          </button>
          <button
            onClick={() => setMostrarModalWO(true)}
            className="btn-wo"
            disabled={partido.estado === 'finalizado'}
          >
            WO
          </button>
        </div>
      </div>

      {/* Punto de Oro Alert */}
      {puntoDeOro && (
        <div className="punto-oro-alert">
          🏆 PUNTO DE ORO 🏆
        </div>
      )}

      {/* Scoreboard principal */}
      <div className="score-area">
        {/* Local */}
        <div
          className="team-side local"
          onClick={sumarPuntoLocal}
        >
          <div className="watermark">{partido.equipo_local}</div>
          <div className="team-info">
            <h2 className="team-name">{partido.equipo_local}</h2>
            <div className="score">{puntosLocal}</div>
          </div>
          <button
            className="btn-minus"
            onClick={(e) => {
              e.stopPropagation();
              restarPuntoLocal();
            }}
          >
            −
          </button>
        </div>

        {/* VS Divider */}
        <div className="vs-divider">VS</div>

        {/* Visitante */}
        <div
          className="team-side visitante"
          onClick={sumarPuntoVisitante}
        >
          <div className="watermark">{partido.equipo_visitante}</div>
          <div className="team-info">
            <h2 className="team-name">{partido.equipo_visitante}</h2>
            <div className="score">{puntosVisitante}</div>
          </div>
          <button
            className="btn-minus"
            onClick={(e) => {
              e.stopPropagation();
              restarPuntoVisitante();
            }}
          >
            −
          </button>
        </div>
      </div>

      {/* Botón Finalizar */}
      <div className="footer">
        <button
          onClick={finalizarPartido}
          className="btn-fin"
          disabled={partido.estado === 'pendiente'}
        >
          ✓ FINALIZAR PARTIDO
        </button>
      </div>

      {/* Modal WalkOver */}
      {mostrarModalWO && (
        <div className="modal-overlay" onClick={() => setMostrarModalWO(false)}>
          <div className="modal-wo" onClick={(e) => e.stopPropagation()}>
            <h2>Walk Over (WO)</h2>
            <p>Selecciona el equipo que NO se presentó:</p>
            <div className="modal-buttons">
              <button
                onClick={() => registrarWalkOver('local')}
                className="btn-wo-equipo local"
              >
                {partido.equipo_local}
                <span className="resultado-wo">Pierde 0-25</span>
              </button>
              <button
                onClick={() => registrarWalkOver('visitante')}
                className="btn-wo-equipo visitante"
              >
                {partido.equipo_visitante}
                <span className="resultado-wo">Pierde 0-25</span>
              </button>
            </div>
            <button
              onClick={() => setMostrarModalWO(false)}
              className="btn-cancelar"
            >
              Cancelar
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default Scoreboard;

import { useState, useEffect } from 'react';
import { api } from '../utils/api';
import './PanelPublico.css';

const PanelPublico = ({ onLogout }) => {
  const [vista, setVista] = useState('en-vivo'); // 'en-vivo', 'standings', 'resultados'
  const [partidosEnVivo, setPartidosEnVivo] = useState([]);
  const [standings, setStandings] = useState([]);
  const [resultados, setResultados] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    cargarDatos();
    const interval = setInterval(cargarDatos, 3000); // Actualizar cada 3s
    return () => clearInterval(interval);
  }, [vista]);

  const cargarDatos = async () => {
    try {
      if (vista === 'en-vivo') {
        const data = await api.get('/partidos/en-vivo');
        setPartidosEnVivo(data);
      } else if (vista === 'standings') {
        const data = await api.get('/standings');
        setStandings(data);
      } else if (vista === 'resultados') {
        const data = await api.get('/partidos/resultados');
        setResultados(data);
      }
      setLoading(false);
    } catch (error) {
      console.error('Error cargando datos:', error);
    }
  };

  return (
    <div className="panel-publico">
      {/* Header */}
      <div className="panel-header">
        <h1 className="panel-title">🏐 WALLY CHAMPIONSHIP 2025</h1>
        <div className="panel-nav">
          <button 
            className={vista === 'en-vivo' ? 'active' : ''}
            onClick={() => setVista('en-vivo')}
          >
            EN VIVO
          </button>
          <button 
            className={vista === 'standings' ? 'active' : ''}
            onClick={() => setVista('standings')}
          >
            TABLA
          </button>
          <button 
            className={vista === 'resultados' ? 'active' : ''}
            onClick={() => setVista('resultados')}
          >
            RESULTADOS
          </button>
        </div>
        <button onClick={onLogout} className="btn-exit">✕</button>
      </div>

      {/* Content */}
      <div className="panel-content">
        {vista === 'en-vivo' && (
          <div className="en-vivo-grid">
            {partidosEnVivo.length === 0 ? (
              <div className="no-data">No hay partidos en juego en este momento</div>
            ) : (
              partidosEnVivo.map(partido => (
                <div key={partido.partido_id} className="partido-vivo">
                  <div className="partido-header">
                    <span className="cancha-badge">CANCHA {partido.cancha}</span>
                    <span className="tiempo-badge">EN JUEGO</span>
                  </div>
                  <div className="partido-score">
                    <div className="equipo">
                      <div className="nombre">{partido.equipo_local}</div>
                      <div className="puntos">{partido.puntos_local || 0}</div>
                    </div>
                    <div className="vs">VS</div>
                    <div className="equipo">
                      <div className="nombre">{partido.equipo_visitante}</div>
                      <div className="puntos">{partido.puntos_visitante || 0}</div>
                    </div>
                  </div>
                  {partido.punto_de_oro && (
                    <div className="punto-oro-badge">🏆 PUNTO DE ORO</div>
                  )}
                </div>
              ))
            )}
          </div>
        )}

        {vista === 'standings' && (
          <div className="standings-table">
            <table>
              <thead>
                <tr>
                  <th>Pos</th>
                  <th>Equipo</th>
                  <th>PJ</th>
                  <th>G</th>
                  <th>E</th>
                  <th>P</th>
                  <th>PF</th>
                  <th>PC</th>
                  <th>Dif</th>
                  <th>Pts</th>
                </tr>
              </thead>
              <tbody>
                {standings.map((equipo, index) => (
                  <tr key={equipo.id} className={index < 4 ? 'clasificado' : ''}>
                    <td className="pos">{index + 1}</td>
                    <td className="equipo">{equipo.nombre}</td>
                    <td>{equipo.jugados}</td>
                    <td>{equipo.ganados}</td>
                    <td>{equipo.empatados}</td>
                    <td>{equipo.perdidos}</td>
                    <td>{equipo.puntos_favor}</td>
                    <td>{equipo.puntos_contra}</td>
                    <td className={equipo.diferencia > 0 ? 'positivo' : equipo.diferencia < 0 ? 'negativo' : ''}>
                      {equipo.diferencia > 0 ? '+' : ''}{equipo.diferencia}
                    </td>
                    <td className="puntos">{equipo.puntos}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {vista === 'resultados' && (
          <div className="resultados-grid">
            {resultados.length === 0 ? (
              <div className="no-data">No hay resultados disponibles</div>
            ) : (
              resultados.map(partido => (
                <div key={partido.partido_id} className="resultado-item">
                  <div className="resultado-header">
                    <span>Cancha {partido.cancha}</span>
                    <span>Día {partido.dia} - {partido.hora_inicio}</span>
                  </div>
                  <div className="resultado-score">
                    <div className={`equipo ${partido.puntos_local > partido.puntos_visitante ? 'ganador' : ''}`}>
                      <span className="nombre">{partido.equipo_local}</span>
                      <span className="puntos">{partido.puntos_local}</span>
                    </div>
                    <div className={`equipo ${partido.puntos_visitante > partido.puntos_local ? 'ganador' : ''}`}>
                      <span className="nombre">{partido.equipo_visitante}</span>
                      <span className="puntos">{partido.puntos_visitante}</span>
                    </div>
                  </div>
                  {partido.punto_de_oro && (
                    <div className="badge-oro">Punto de Oro</div>
                  )}
                </div>
              ))
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default PanelPublico;

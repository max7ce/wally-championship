import { useState } from 'react';
import { api } from '../utils/api';
import './Sorteo.css';

const Sorteo = ({ onComplete, onLogout }) => {
  const [equipos, setEquipos] = useState(Array(8).fill(''));
  const [sorteando, setSorteando] = useState(false);
  const [resultado, setResultado] = useState(null);
  const [error, setError] = useState('');

  const handleInputChange = (index, value) => {
    const nuevosEquipos = [...equipos];
    nuevosEquipos[index] = value;
    setEquipos(nuevosEquipos);
  };

  const realizarSorteo = async () => {
    // Validar que todos los equipos tengan nombre
    if (equipos.some(eq => !eq.trim())) {
      setError('Todos los equipos deben tener nombre');
      return;
    }

    // Validar nombres únicos
    const nombresUnicos = new Set(equipos.map(eq => eq.trim().toLowerCase()));
    if (nombresUnicos.size !== 8) {
      setError('Los nombres de los equipos deben ser únicos');
      return;
    }

    setError('');
    setSorteando(true);

    try {
      // Animación de sorteo (3 segundos)
      await new Promise(resolve => setTimeout(resolve, 3000));

      // Llamar al backend
      const response = await api.post('/equipos/sorteo', {
        equipos: equipos.map(eq => eq.trim())
      });

      setResultado(response.equipos);
      
      // Auto-continuar después de 5 segundos
      setTimeout(() => {
        if (onComplete) onComplete();
      }, 5000);

    } catch (err) {
      setError('Error al realizar el sorteo: ' + err.message);
      setSorteando(false);
    }
  };

  if (resultado) {
    return (
      <div className="sorteo-container">
        <div className="sorteo-resultado">
          <h1 className="sorteo-title">🎲 SORTEO COMPLETADO</h1>
          <div className="resultado-grid">
            {resultado.map((equipo, index) => (
              <div key={equipo.id} className="resultado-item">
                <div className="posicion">EQ{equipo.posicion}</div>
                <div className="nombre">{equipo.nombre}</div>
              </div>
            ))}
          </div>
          <p className="sorteo-info">El fixture ha sido actualizado con los equipos sorteados</p>
          <button onClick={onComplete} className="btn-continuar">
            CONTINUAR →
          </button>
        </div>
      </div>
    );
  }

  if (sorteando) {
    return (
      <div className="sorteo-container">
        <div className="sorteo-loading">
          <h1 className="sorteo-title">🎲 SORTEANDO...</h1>
          <div className="spinner"></div>
          <p>Mezclando equipos al azar...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="sorteo-container">
      <div className="sorteo-box">
        <div className="sorteo-header">
          <h1 className="sorteo-title">🎲 SORTEO DE EQUIPOS</h1>
          <button onClick={onLogout} className="btn-exit-small">✕</button>
        </div>
        
        <p className="sorteo-instrucciones">
          Ingrese los nombres de los 8 equipos participantes. El sistema realizará el sorteo 
          y asignará aleatoriamente las posiciones (EQ1 a EQ8) que se utilizarán en el fixture.
        </p>

        <div className="equipos-grid">
          {equipos.map((equipo, index) => (
            <div key={index} className="equipo-input-group">
              <label>Equipo {index + 1}</label>
              <input
                type="text"
                value={equipo}
                onChange={(e) => handleInputChange(index, e.target.value)}
                placeholder={`Nombre del equipo ${index + 1}`}
                maxLength={50}
              />
            </div>
          ))}
        </div>

        {error && <div className="error-message">{error}</div>}

        <button 
          onClick={realizarSorteo}
          className="btn-sortear"
          disabled={equipos.some(eq => !eq.trim())}
        >
          🎲 REALIZAR SORTEO
        </button>
      </div>
    </div>
  );
};

export default Sorteo;

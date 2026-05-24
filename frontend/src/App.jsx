import { useState } from 'react';
import Login from './components/Login';
import Scoreboard from './components/Scoreboard';
import PanelPublico from './components/PanelPublico';
import Sorteo from './components/Sorteo';
import './App.css';

function App() {
  const [user, setUser] = useState(null);
  const [mostrarSorteo, setMostrarSorteo] = useState(false);

  const handleLogin = (userData) => {
    setUser(userData);
  };

  const handleLogout = () => {
    localStorage.removeItem('auth');
    setUser(null);
  };

  const handleSorteoComplete = () => {
    setMostrarSorteo(false);
  };

  // No autenticado
  if (!user) {
    return <Login onLogin={handleLogin} />;
  }

  // Mostrar sorteo (solo admin)
  if (mostrarSorteo && user.tipo === 'admin') {
    return (
      <Sorteo 
        onComplete={handleSorteoComplete}
        onLogout={handleLogout}
      />
    );
  }

  // Vista según tipo de usuario
  if (user.tipo === 'publico') {
    return <PanelPublico onLogout={handleLogout} />;
  }

  if (user.cancha) {
    return (
      <Scoreboard 
        cancha={user.cancha}
        onLogout={handleLogout}
      />
    );
  }

  // Admin - Panel de control
  return (
    <div className="admin-panel">
      <h1>Panel de Administración</h1>
      <div className="admin-options">
        <button onClick={() => setMostrarSorteo(true)}>
          🎲 Realizar Sorteo de Equipos
        </button>
        <button onClick={() => setUser({ ...user, tipo: 'publico' })}>
          📊 Ver Panel Público
        </button>
        <button onClick={handleLogout}>
          🚪 Cerrar Sesión
        </button>
      </div>
    </div>
  );
}

export default App;

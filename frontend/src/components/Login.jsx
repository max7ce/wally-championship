import { useState } from 'react';
import './Login.css';

const Login = ({ onLogin }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    
    try {
      // Guardar credenciales
      localStorage.setItem('auth', JSON.stringify({ username, password }));
      
      // Determinar tipo de usuario
      let tipo = username.toLowerCase();
      let cancha = null;
      
      if (tipo.includes('cancha')) {
        cancha = parseInt(tipo.replace('cancha', ''));
      }
      
      onLogin({ username, tipo, cancha });
    } catch (err) {
      setError('Error al iniciar sesión');
    }
  };

  return (
    <div className="login-container">
      <div className="login-box">
        <h1 className="login-title">🏐 WALLY CHAMPIONSHIP</h1>
        <h2 className="login-subtitle">Control de Cancha</h2>
        
        <form onSubmit={handleSubmit} className="login-form">
          <div className="form-group">
            <label>Usuario</label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="cancha1, cancha2, cancha3, publico"
              required
              autoFocus
            />
          </div>
          
          <div className="form-group">
            <label>Contraseña</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Contraseña"
              required
            />
          </div>
          
          {error && <div className="error-message">{error}</div>}
          
          <button type="submit" className="btn-login">
            INGRESAR
          </button>
        </form>
        
        <div className="login-help">
          <p>Usuarios por defecto:</p>
          <ul>
            <li><strong>cancha1</strong> / cancha1</li>
            <li><strong>cancha2</strong> / cancha2</li>
            <li><strong>cancha3</strong> / cancha3</li>
            <li><strong>publico</strong> / publico</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default Login;

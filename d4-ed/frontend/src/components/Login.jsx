import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { styles } from '../styles';

const API_URL = 'http://127.0.0.1:5000/api';

export default function Login({ setUser }) {
  const [usernameInput, setUsernameInput] = useState('');
  const [statusMsg, setStatusMsg] = useState('');
  const navigate = useNavigate();

  const handleLogin = async () => {
    const res = await fetch(`${API_URL}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username: usernameInput }),
    });
    const data = await res.json();
    
    if (data.success) {
      setUser({ role: data.role, token: data.token, username: usernameInput });
      if (data.role === 'ADMIN') navigate('/admin');
      else if (data.role === 'OPERATOR') navigate('/operator');
      else navigate('/public');
    } else {
      setStatusMsg('Login failed. Try "public", "operator", or "admin".');
    }
  };

  return (
    <div style={{ ...styles.section, borderTop: '5px solid #95a5a6', marginTop: '50px' }}>
      <h2 style={styles.h2}>System Login</h2>
      <p style={styles.p}>Available default accounts: <strong>public</strong>, <strong>operator</strong>, <strong>admin</strong></p>
      <div style={{ display: 'flex', gap: '10px' }}>
        <input type="text" placeholder="Enter username..." value={usernameInput} onChange={(e) => setUsernameInput(e.target.value)} style={{ ...styles.input, marginBottom: 0, flex: 1 }} />
        <button onClick={handleLogin} style={styles.btn}>Authenticate</button>
      </div>
      <p style={{ color: '#e74c3c', fontWeight: 'bold', marginTop: '10px' }}>{statusMsg}</p>
    </div>
  );
}
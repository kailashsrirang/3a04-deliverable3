import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate, Link } from 'react-router-dom';
import { styles } from './styles';

import Login from './components/Login';
import PublicDashboard from './components/PublicDashboard';
import OperatorDashboard from './components/OperatorDashboard';
import AdminDashboard from './components/AdminDashboard';
import SystemLogs from './components/SystemLogs';
import RolePermissions from './components/RolePermissions';
import MapDashboard from './components/MapDashboard'; // NEW IMPORT

const API_URL = 'http://127.0.0.1:5000/api';

const ProtectedRoute = ({ user, allowedRoles, children }) => {
  if (!user) return <Navigate to="/login" replace />;
  if (!allowedRoles.includes(user.role)) return <Navigate to={`/${user.role.toLowerCase()}`} replace />;
  return children;
};

export default function App() {
  const [user, setUser] = useState(null);
  const [publicData, setPublicData] = useState([]);
  const [systemStatus, setSystemStatus] = useState({ logs: [], alerts: [], thresholds: {}, raw_telemetry: [] });
  const [isDark, setIsDark] = useState(false);

  const toggleTheme = () => {
    const newTheme = !isDark;
    setIsDark(newTheme);
    document.documentElement.setAttribute('data-theme', newTheme ? 'dark' : 'light');
  };

  const fetchAllData = async () => {
    const pubRes = await fetch(`${API_URL}/data/public`);
    const pubData = await pubRes.json();
    setPublicData(pubData.aggregated_telemetry);

    if (user) {
      const sysRes = await fetch(`${API_URL}/system/status`);
      const sysData = await sysRes.json();
      setSystemStatus(sysData);
    }
  };

  useEffect(() => {
    fetchAllData();
    const interval = setInterval(fetchAllData, 5000);
    return () => clearInterval(interval);
  }, [user]);

  const deleteAlert = async (id) => {
    await fetch(`${API_URL}/alerts/delete`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ role: user.role, username: user.username, id }),
    });
    fetchAllData();
  };

  return (
    <BrowserRouter>
      <div style={styles.container}>
        {user && (
          <nav style={styles.nav}>
            <div>
              <strong style={{ fontSize: '1.2rem' }}>SCEMAS</strong>
              <Link to={`/${user.role.toLowerCase()}`} style={styles.link}>Dashboard</Link>
              
              {/* NEW: Map and Logs are now available to BOTH Operators and Admins */}
              {(user.role === 'ADMIN' || user.role === 'OPERATOR') && (
                <>
                  <Link to="/map" style={styles.link}>City Map</Link>
                  <Link to="/logs" style={styles.link}>System Logs</Link>
                </>
              )}
              
              {user.role === 'ADMIN' && (
                <Link to="/roles" style={styles.link}>Role Permissions</Link>
              )}
            </div>
            
            <div style={{ display: 'flex', alignItems: 'center', gap: '15px' }}>
              <button onClick={toggleTheme} style={{...styles.btn, background: '#95a5a6', padding: '5px 10px', color: 'white'}}>
                {isDark ? '☀️ Light' : '🌙 Dark'}
              </button>
              <span>Logged in as: <strong>{user.username}</strong> ({user.role})</span>
              <button onClick={() => setUser(null)} style={{...styles.btn, background: '#e74c3c', padding: '5px 10px'}}>Logout</button>
            </div>
          </nav>
        )}

        <Routes>
          <Route path="/" element={<Navigate to={user ? `/${user.role.toLowerCase()}` : "/login"} replace />} />
          <Route path="/login" element={<Login setUser={setUser} />} />

          <Route path="/public" element={
            <ProtectedRoute user={user} allowedRoles={['PUBLIC', 'OPERATOR', 'ADMIN']}>
              <PublicDashboard publicData={publicData} alerts={systemStatus.alerts} user={user} deleteAlert={deleteAlert} />
            </ProtectedRoute>
          } />

          <Route path="/operator" element={
            <ProtectedRoute user={user} allowedRoles={['OPERATOR', 'ADMIN']}>
              <OperatorDashboard publicData={publicData} systemStatus={systemStatus} refreshData={fetchAllData} user={user} deleteAlert={deleteAlert} />
            </ProtectedRoute>
          } />

          <Route path="/admin" element={
            <ProtectedRoute user={user} allowedRoles={['ADMIN']}>
              <AdminDashboard user={user} publicData={publicData} systemStatus={systemStatus} refreshData={fetchAllData} deleteAlert={deleteAlert} />
            </ProtectedRoute>
          } />

          {/* NEW: Logs accessibility updated */}
          <Route path="/logs" element={
            <ProtectedRoute user={user} allowedRoles={['OPERATOR', 'ADMIN']}>
              <SystemLogs logs={systemStatus.logs} />
            </ProtectedRoute>
          } />

          {/* NEW: Map Route added */}
          <Route path="/map" element={
            <ProtectedRoute user={user} allowedRoles={['OPERATOR', 'ADMIN']}>
              <MapDashboard rawTelemetry={systemStatus.raw_telemetry} />
            </ProtectedRoute>
          } />

          <Route path="/roles" element={
            <ProtectedRoute user={user} allowedRoles={['ADMIN']}>
              <RolePermissions user={user} />
            </ProtectedRoute>
          } />
        </Routes>
      </div>
    </BrowserRouter>
  );
}
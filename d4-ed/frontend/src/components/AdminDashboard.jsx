import React, { useState } from 'react';
import OperatorDashboard from './OperatorDashboard';
import { styles } from '../styles';

const API_URL = 'http://127.0.0.1:5000/api';

export default function AdminDashboard({ user, publicData, systemStatus, refreshData, deleteAlert }) {
  const [editSensor, setEditSensor] = useState('TEMPERATURE');
  const [editMin, setEditMin] = useState('');
  const [editMax, setEditMax] = useState('');

  const updateThreshold = async () => {
    const res = await fetch(`${API_URL}/thresholds/update`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ role: user.role, sensor: editSensor, min: editMin, max: editMax }),
    });
    const data = await res.json();
    if (data.success) window.alert(`Success! Thresholds for ${editSensor} updated to:\nMin: ${editMin}\nMax: ${editMax}`);
    else window.alert(`Error: ${data.message}`);
    refreshData();
  };

  const wipeDatabase = async () => {
    const confirmed = window.confirm("WARNING: Are you sure you want to completely wipe all historical data (telemetry, alerts, logs)? This action cannot be undone.");
    if (!confirmed) return;
    const res = await fetch(`${API_URL}/system/wipe`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ role: user.role }),
    });
    const data = await res.json();
    window.alert(data.message);
    refreshData();
  };

  const wipeTelemetry = async () => {
    const confirmed = window.confirm("WARNING: Are you sure you want to wipe ONLY the raw sensor data?");
    if (!confirmed) return;
    const res = await fetch(`${API_URL}/system/wipe_telemetry`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ role: user.role }),
    });
    const data = await res.json();
    window.alert(data.message);
    refreshData();
  };

  return (
    <div>
      <OperatorDashboard publicData={publicData} systemStatus={systemStatus} refreshData={refreshData} user={user} deleteAlert={deleteAlert} />

      <div style={{ ...styles.section, borderTop: '5px solid #9b59b6' }}>
        <h2 style={styles.h2}>Administrator Panel</h2>
        <div style={styles.grid}>
          
          <div>
            <h3 style={styles.h3}>Edit Thresholds</h3>
            <select value={editSensor} onChange={(e) => setEditSensor(e.target.value)} style={styles.input}>
              <option value="TEMPERATURE">Temperature</option>
              <option value="NOISE">Noise Level</option>
              <option value="AIR_QUALITY">Air Quality</option>
            </select>
            <div style={{ display: 'flex', gap: '10px' }}>
              <input type="number" placeholder="New Min" value={editMin} onChange={(e) => setEditMin(e.target.value)} style={styles.input} />
              <input type="number" placeholder="New Max" value={editMax} onChange={(e) => setEditMax(e.target.value)} style={styles.input} />
            </div>
            <button onClick={updateThreshold} style={{...styles.btn, background: '#9b59b6', width: '100%'}}>Save Thresholds</button>
          </div>

          <div style={{ borderTop: '2px solid #e74c3c' }}>
            <h3 style={{ color: '#c0392b', margin: '15px 0 5px 0' }}>Danger Zone</h3>
            <p style={styles.p}>Manage system data retention.</p>
            <div style={{ display: 'flex', gap: '10px' }}>
              <button onClick={wipeTelemetry} style={{...styles.btn, background: '#e67e22', width: '100%', fontWeight: 'bold'}}>WIPE SENSOR DATA</button>
              <button onClick={wipeDatabase} style={{...styles.btn, background: '#c0392b', width: '100%', fontWeight: 'bold'}}>WIPE DATABASE</button>
            </div>
          </div>
          
        </div>
      </div>
    </div>
  );
}
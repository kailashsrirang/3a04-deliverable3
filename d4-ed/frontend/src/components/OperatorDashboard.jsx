import React, { useState } from 'react';
import PublicDashboard from './PublicDashboard';
import { styles } from '../styles';

const API_URL = 'http://127.0.0.1:5000/api';

export default function OperatorDashboard({ publicData, systemStatus, refreshData, user, deleteAlert }) {
  const [sensorType, setSensorType] = useState('TEMPERATURE');
  const [sensorValue, setSensorValue] = useState('');
  const [sensorX, setSensorX] = useState('');
  const [sensorY, setSensorY] = useState('');
  const [statusMsg, setStatusMsg] = useState('');

  const submitManualTelemetry = async () => {
    const res = await fetch(`${API_URL}/data/ingest`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ type: sensorType, value: sensorValue, x: sensorX, y: sensorY }),
    });
    const data = await res.json();
    setStatusMsg(data.message);
    if (data.success) {
      setSensorValue(''); setSensorX(''); setSensorY('');
    }
    refreshData();
  };

  return (
    <div>
      <PublicDashboard publicData={publicData} alerts={systemStatus.alerts} user={user} deleteAlert={deleteAlert} />

      <div style={{ ...styles.section, borderTop: '5px solid #2ecc71' }}>
        <h2 style={styles.h2}>Operator Controls</h2>
        <div style={styles.grid}>
          <div>
            <h3 style={styles.h3}>Manual Sensor Ingestion</h3>
            <select value={sensorType} onChange={(e) => setSensorType(e.target.value)} style={styles.input}>
              <option value="TEMPERATURE">Temperature (°C)</option>
              <option value="NOISE">Noise Level (dB)</option>
              <option value="AIR_QUALITY">Air Quality (AQI)</option>
            </select>
            <input type="number" placeholder="Sensor Value" value={sensorValue} onChange={(e) => setSensorValue(e.target.value)} style={styles.input} />
            
            <div style={{ display: 'flex', gap: '10px' }}>
              <input type="number" placeholder="X (-1000 to 1000)" value={sensorX} onChange={(e) => setSensorX(e.target.value)} style={styles.input} />
              <input type="number" placeholder="Y (-1000 to 1000)" value={sensorY} onChange={(e) => setSensorY(e.target.value)} style={styles.input} />
            </div>

            <button onClick={submitManualTelemetry} style={{...styles.btn, width: '100%', background: '#2ecc71'}}>Submit Telemetry</button>
            <p style={{ fontWeight: 'bold', color: '#27ae60', marginTop: '10px' }}>{statusMsg}</p>
          </div>

          <div>
            <h3 style={styles.h3}>Current Alert Thresholds</h3>
            <ul style={{ background: 'var(--bg-box)', padding: '15px', borderRadius: '5px', margin: 0, listStyle: 'none' }}>
              {Object.entries(systemStatus.thresholds || {}).map(([key, val]) => (
                <li key={key} style={{ marginBottom: '8px', borderBottom: `1px solid var(--border-color)`, paddingBottom: '5px', color: 'var(--text-main)' }}>
                  <strong>{key}:</strong> <br/>
                  Min: <span style={{color: '#3498db', fontWeight: 'bold'}}>{val.min}</span> | Max: <span style={{color: '#e74c3c', fontWeight: 'bold'}}>{val.max}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>

        <div style={{ marginTop: '20px' }}>
          <h3 style={styles.h3}>Raw Sensor Data Stream</h3>
          <div style={{ ...styles.box, height: '135px' }}>
            {systemStatus.raw_telemetry?.length === 0 ? <p>No data recorded yet.</p> : null}
            {[...(systemStatus.raw_telemetry || [])].reverse().map((d, i) => (
              <div key={i}><strong>[{d.time}]</strong> {d.type} in Zone {d.zone} ({d.x}, {d.y}): {d.value}</div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
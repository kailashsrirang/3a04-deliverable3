import React from 'react';
import { styles } from '../styles';

export default function PublicDashboard({ publicData, alerts, user, deleteAlert }) {
  return (
    <div style={styles.grid}>
      <div style={{ ...styles.section, borderTop: '5px solid #3498db' }}>
        <h2 style={styles.h2}>Public Environmental Data</h2>
        <p style={styles.p}>Aggregated average of the last 5 readings per geographic zone.</p>
        
        <table style={{ width: '100%', borderCollapse: 'collapse', marginTop: '10px' }}>
          <thead>
            <tr>
              <th style={styles.th}>Zone</th>
              <th style={styles.th}>Temp (°C)</th>
              <th style={styles.th}>Noise (dB)</th>
              <th style={styles.th}>AQI</th>
            </tr>
          </thead>
          <tbody>
            {publicData.length === 0 ? <tr><td colSpan="4" style={{...styles.td, textAlign: 'center'}}>No data available.</td></tr> : null}
            {publicData.map((row, i) => (
              <tr key={i}>
                <td style={styles.td}><strong>{row.zone}</strong></td>
                <td style={styles.td}>{row.TEMPERATURE}</td>
                <td style={styles.td}>{row.NOISE}</td>
                <td style={styles.td}>{row.AIR_QUALITY}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div style={{ ...styles.section, borderTop: '5px solid #e67e22' }}>
        <h2 style={styles.h2}>Active System Alerts</h2>
        <div style={styles.alertBox}>
          {alerts?.length === 0 ? "No active alerts." : null}
          {alerts?.map((alert) => (
            <div key={alert.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px', borderBottom: '1px solid #ffcccc', paddingBottom: '4px' }}>
              <span><strong>{alert.text}</strong></span>
              
              {/* NEW: Changed 'Delete' to 'Resolve' and made it green */}
              {user && (user.role === 'ADMIN' || user.role === 'OPERATOR') && (
                <button onClick={() => deleteAlert(alert.id)} style={{...styles.btn, background: '#27ae60', padding: '2px 8px', fontSize: '12px'}}>Resolve</button>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
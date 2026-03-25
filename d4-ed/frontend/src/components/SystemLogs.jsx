import React from 'react';
import { styles } from '../styles';

export default function SystemLogs({ logs }) {
  return (
    <div style={{ ...styles.section, borderTop: '5px solid #34495e' }}>
      <h2 style={styles.h2}>System Audit Logs</h2>
      <p style={styles.p}>Secure, read-only system event tracking.</p>
      <div style={{ ...styles.box, height: '600px', fontSize: '14px' }}>
        {logs.length === 0 ? "No logs generated yet." : null}
        {[...logs].reverse().map((log, i) => <div key={i}>{log}</div>)}
      </div>
    </div>
  );
}
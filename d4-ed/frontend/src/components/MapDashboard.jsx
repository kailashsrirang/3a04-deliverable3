import React from 'react';
import { styles } from '../styles';

export default function MapDashboard({ rawTelemetry }) {
  // Extract only unique X and Y combinations
  const uniqueSensors = [];
  const seen = new Set();
  
  (rawTelemetry || []).forEach(d => {
    const key = `${d.x},${d.y}`;
    if (!seen.has(key)) {
      seen.add(key);
      uniqueSensors.push(d);
    }
  });

  return (
    <div style={{ ...styles.section, borderTop: '5px solid #16a085' }}>
      <h2 style={styles.h2}>City Sensor Map</h2>
      <p style={styles.p}>Live view of active sensor coordinates. Displaying {uniqueSensors.length} unique nodes.</p>
      
      {/* 4x4 Grid Container */}
      <div style={{ 
        position: 'relative', 
        width: '100%', 
        maxWidth: '600px', 
        aspectRatio: '1/1', 
        margin: '20px auto',
        background: 'var(--bg-box)', 
        border: '2px solid var(--border-color)',
        // This generates the 4x4 background grid mathematically
        backgroundImage: 'linear-gradient(to right, var(--border-color) 1px, transparent 1px), linear-gradient(to bottom, var(--border-color) 1px, transparent 1px)',
        backgroundSize: '25% 25%'
      }}>
        
        {/* Center Axis Lines (Crosshairs) */}
        <div style={{ position: 'absolute', top: 0, bottom: 0, left: '50%', width: '2px', background: '#e74c3c', zIndex: 1 }} />
        <div style={{ position: 'absolute', top: '50%', left: 0, right: 0, height: '2px', background: '#e74c3c', zIndex: 1 }} />

        {/* Plotting the Sensors */}
        {uniqueSensors.map((s, i) => {
          // Math to convert -1000/1000 scale into 0% to 100% relative CSS positioning
          const left = `${((s.x + 1000) / 2000) * 100}%`;
          const top = `${((1000 - s.y) / 2000) * 100}%`;
          
          return (
            <div key={i} style={{
              position: 'absolute',
              left: left,
              top: top,
              width: '14px',
              height: '14px',
              background: '#3498db',
              borderRadius: '50%',
              transform: 'translate(-50%, -50%)',
              zIndex: 2,
              boxShadow: '0 0 5px rgba(0,0,0,0.5)',
              cursor: 'pointer'
            }} title={`Zone ${s.zone}\nCoordinates: (${s.x}, ${s.y})`} />
          );
        })}
      </div>
      
      <div style={{ textAlign: 'center', fontSize: '12px', color: 'var(--text-muted)' }}>
        Hover over a node to view its Zone and Exact Coordinates.
      </div>
    </div>
  );
}
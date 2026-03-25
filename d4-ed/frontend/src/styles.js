export const styles = {
  container: { maxWidth: '1000px', margin: '0 auto', fontFamily: 'sans-serif', padding: '20px' },
  
  // Use the CSS variables for backgrounds and text!
  section: { background: 'var(--bg-card)', color: 'var(--text-main)', padding: '20px', borderRadius: '8px', marginBottom: '20px', boxShadow: '0 2px 5px rgba(0,0,0,0.1)', transition: 'all 0.3s ease' },
  
  grid: { display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' },
  
  // The terminal-style boxes stay dark, but everything else adapts
  box: { background: '#1e1e1e', color: '#0f0', padding: '10px', height: '150px', overflowY: 'auto', fontSize: '12px', fontFamily: 'monospace', borderRadius: '4px' },
  alertBox: { background: '#ffe6e6', color: '#cc0000', padding: '10px', height: '150px', overflowY: 'auto', border: '1px solid #cc0000', borderRadius: '4px' },
  
  btn: { padding: '8px 16px', background: '#3498db', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' },
  
  input: { 
    padding: '8px', width: '100%', marginBottom: '10px', boxSizing: 'border-box', 
    backgroundColor: 'var(--bg-input)', color: 'var(--text-main)', 
    border: '1px solid var(--border-color)', borderRadius: '4px' 
  },
  
  nav: { display: 'flex', justifyContent: 'space-between', background: 'var(--nav-bg)', padding: '15px 20px', borderRadius: '8px', color: 'white', marginBottom: '20px', alignItems: 'center', transition: 'all 0.3s ease' },
  link: { color: '#ecf0f1', textDecoration: 'none', marginLeft: '20px', fontWeight: 'bold' },
  
  h2: { color: 'var(--text-main)', margin: '0 0 15px 0', borderBottom: '2px solid var(--border-color)', paddingBottom: '10px' },
  h3: { color: 'var(--text-main)', margin: '0 0 10px 0' },
  p: { color: 'var(--text-muted)', margin: '0 0 15px 0' },
  
  th: { backgroundColor: 'var(--nav-bg)', color: 'white', padding: '10px', textAlign: 'left', fontSize: '14px' },
  td: { padding: '10px', borderBottom: '1px solid var(--border-color)', color: 'var(--text-main)', fontSize: '14px' }
};
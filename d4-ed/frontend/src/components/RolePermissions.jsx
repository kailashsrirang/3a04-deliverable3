import React, { useState, useEffect } from 'react';
import { styles } from '../styles';

const API_URL = 'http://127.0.0.1:5000/api';

export default function RolePermissions({ user }) {
  const [users, setUsers] = useState([]);
  const [newUsername, setNewUsername] = useState('');
  const [newRole, setNewRole] = useState('OPERATOR');
  
  const [editingId, setEditingId] = useState(null);
  const [editUsername, setEditUsername] = useState('');
  const [editRole, setEditRole] = useState('');

  const fetchUsers = async () => {
    const res = await fetch(`${API_URL}/rbac/users`);
    const data = await res.json();
    setUsers(data.users);
  };

  useEffect(() => { fetchUsers(); }, []);

  const handleAdd = async () => {
    if (!newUsername) return;
    const res = await fetch(`${API_URL}/rbac/add`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ admin_role: user.role, username: newUsername, role: newRole }),
    });
    const data = await res.json();
    window.alert(data.message);
    if (data.success) { setNewUsername(''); fetchUsers(); }
  };

  const startEdit = (u) => { setEditingId(u.id); setEditUsername(u.username); setEditRole(u.role); };

  const saveEdit = async () => {
    const res = await fetch(`${API_URL}/rbac/edit`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ admin_role: user.role, id: editingId, username: editUsername, role: editRole }),
    });
    const data = await res.json();
    window.alert(data.message);
    if (data.success) { setEditingId(null); fetchUsers(); }
  };

  const handleDelete = async (id, username) => {
    if (!window.confirm(`Are you sure you want to delete user '${username}'?`)) return;
    const res = await fetch(`${API_URL}/rbac/delete`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ admin_role: user.role, id }),
    });
    const data = await res.json();
    window.alert(data.message);
    fetchUsers();
  };

  return (
    <div style={{ ...styles.section, borderTop: '5px solid #f39c12' }}>
      <h2 style={styles.h2}>Role Permissions</h2>
      <p style={styles.p}>Manage system users and their associated authority levels.</p>
      
      <div style={{ background: 'var(--bg-box)', padding: '15px', borderRadius: '8px', marginBottom: '20px', border: `1px solid var(--border-color)` }}>
        <h3 style={styles.h3}>Add New User</h3>
        <div style={{ display: 'flex', gap: '10px' }}>
          <input type="text" placeholder="Username" value={newUsername} onChange={(e) => setNewUsername(e.target.value)} style={{...styles.input, marginBottom: 0}} />
          <select value={newRole} onChange={(e) => setNewRole(e.target.value)} style={{...styles.input, marginBottom: 0, width: '200px'}}>
            <option value="PUBLIC">PUBLIC</option>
            <option value="OPERATOR">OPERATOR</option>
            <option value="ADMIN">ADMIN</option>
          </select>
          <button onClick={handleAdd} style={{...styles.btn, background: '#f39c12', whiteSpace: 'nowrap', color: 'white'}}>Add User</button>
        </div>
      </div>

      <div style={{ ...styles.box, height: '400px' }}>
        <table style={{ width: '100%', textAlign: 'left', borderCollapse: 'collapse' }}>
          <thead>
            <tr>
              <th style={styles.th}>ID</th>
              <th style={styles.th}>Username</th>
              <th style={styles.th}>Role</th>
              <th style={styles.th}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {users.map(u => (
              <tr key={u.id}>
                <td style={{...styles.td, color: '#0f0'}}>{u.id}</td>
                {editingId === u.id ? (
                  <>
                    <td style={styles.td}><input value={editUsername} onChange={e => setEditUsername(e.target.value)} style={{...styles.input, width:'90%', padding: '4px', marginBottom: 0}} /></td>
                    <td style={styles.td}>
                      <select value={editRole} onChange={e => setEditRole(e.target.value)} style={{ ...styles.input, padding: '4px', marginBottom: 0 }}>
                        <option value="PUBLIC">PUBLIC</option><option value="OPERATOR">OPERATOR</option><option value="ADMIN">ADMIN</option>
                      </select>
                    </td>
                    <td style={styles.td}>
                      <button onClick={saveEdit} style={{...styles.btn, background:'#2ecc71', padding:'4px 8px', marginRight:'5px'}}>Save</button>
                      <button onClick={() => setEditingId(null)} style={{...styles.btn, background:'#7f8c8d', padding:'4px 8px'}}>Cancel</button>
                    </td>
                  </>
                ) : (
                  <>
                    <td style={{...styles.td, color: '#0f0'}}>{u.username}</td>
                    <td style={{...styles.td, color: '#0f0'}}>{u.role}</td>
                    <td style={styles.td}>
                      {!u.is_editable ? (
                        <span style={{ color: '#7f8c8d', fontStyle: 'italic' }}>System Default</span>
                      ) : (
                        <>
                          <button onClick={() => startEdit(u)} style={{...styles.btn, background:'#3498db', padding:'4px 8px', marginRight:'5px'}}>Edit</button>
                          <button onClick={() => handleDelete(u.id, u.username)} style={{...styles.btn, background:'#e74c3c', padding:'4px 8px'}}>Delete</button>
                        </>
                      )}
                    </td>
                  </>
                )}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
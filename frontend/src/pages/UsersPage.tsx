import React, { useEffect, useState } from 'react';
import api from '../services/api';

interface User {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  full_name: string;
  role: string;
  department: string;
  is_active: boolean;
}

const UsersPage: React.FC = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchUsers = async () => {
      try {
        const res = await api.get('/users');
        setUsers(res.data.users);
      } catch { /* handle */ } finally {
        setLoading(false);
      }
    };
    fetchUsers();
  }, []);

  if (loading) return <div>Loading users...</div>;

  return (
    <div>
      <h1 style={{ fontSize: '24px', fontWeight: 700, color: '#1e3a5f', marginBottom: '24px' }}>User Management</h1>
      <div style={{ backgroundColor: 'white', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)', overflow: 'hidden' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ backgroundColor: '#f9fafb', borderBottom: '2px solid #e5e7eb' }}>
              {['Name', 'Email', 'Role', 'Department', 'Status'].map(h => (
                <th key={h} style={{ textAlign: 'left', padding: '10px 14px', fontSize: '12px', fontWeight: 600, color: '#6b7280', textTransform: 'uppercase' }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {users.map(user => (
              <tr key={user.id} style={{ borderBottom: '1px solid #f3f4f6' }}>
                <td style={{ padding: '10px 14px', fontSize: '13px', fontWeight: 500 }}>{user.full_name}</td>
                <td style={{ padding: '10px 14px', fontSize: '13px', color: '#3b82f6' }}>{user.email}</td>
                <td style={{ padding: '10px 14px' }}>
                  <span style={{ padding: '2px 8px', borderRadius: '10px', fontSize: '11px', fontWeight: 600, color: 'white', textTransform: 'capitalize',
                    backgroundColor: user.role === 'admin' ? '#8b5cf6' : user.role === 'manager' ? '#3b82f6' : '#6b7280' }}>
                    {user.role}
                  </span>
                </td>
                <td style={{ padding: '10px 14px', fontSize: '13px', color: '#6b7280' }}>{user.department || '—'}</td>
                <td style={{ padding: '10px 14px' }}>
                  <span style={{ padding: '2px 8px', borderRadius: '10px', fontSize: '11px', fontWeight: 600, color: 'white', backgroundColor: user.is_active ? '#10b981' : '#ef4444' }}>
                    {user.is_active ? 'Active' : 'Inactive'}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default UsersPage;

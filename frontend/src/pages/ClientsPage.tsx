import React, { useEffect, useState } from 'react';
import api from '../services/api';

interface Client {
  id: number;
  name: string;
  code: string;
  industry: string;
  contact_person: string;
  contact_email: string;
  contact_phone: string;
  is_active: boolean;
}

const ClientsPage: React.FC = () => {
  const [clients, setClients] = useState<Client[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchClients = async () => {
      try {
        const res = await api.get('/clients');
        setClients(res.data.clients);
      } catch { /* handle */ } finally {
        setLoading(false);
      }
    };
    fetchClients();
  }, []);

  if (loading) return <div>Loading clients...</div>;

  return (
    <div>
      <h1 style={{ fontSize: '24px', fontWeight: 700, color: '#1e3a5f', marginBottom: '24px' }}>Clients</h1>
      <div style={{ backgroundColor: 'white', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)', overflow: 'hidden' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ backgroundColor: '#f9fafb', borderBottom: '2px solid #e5e7eb' }}>
              {['Code', 'Name', 'Industry', 'Contact', 'Email', 'Status'].map(h => (
                <th key={h} style={{ textAlign: 'left', padding: '10px 14px', fontSize: '12px', fontWeight: 600, color: '#6b7280', textTransform: 'uppercase' }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {clients.length === 0 ? (
              <tr><td colSpan={6} style={{ padding: '40px', textAlign: 'center', color: '#9ca3af' }}>No clients found.</td></tr>
            ) : clients.map(client => (
              <tr key={client.id} style={{ borderBottom: '1px solid #f3f4f6' }}>
                <td style={{ padding: '10px 14px', fontSize: '13px', fontWeight: 600 }}>{client.code}</td>
                <td style={{ padding: '10px 14px', fontSize: '13px' }}>{client.name}</td>
                <td style={{ padding: '10px 14px', fontSize: '13px', color: '#6b7280' }}>{client.industry || '—'}</td>
                <td style={{ padding: '10px 14px', fontSize: '13px' }}>{client.contact_person || '—'}</td>
                <td style={{ padding: '10px 14px', fontSize: '13px', color: '#3b82f6' }}>{client.contact_email || '—'}</td>
                <td style={{ padding: '10px 14px' }}>
                  <span style={{ padding: '2px 8px', borderRadius: '10px', fontSize: '11px', fontWeight: 600, color: 'white', backgroundColor: client.is_active ? '#10b981' : '#6b7280' }}>
                    {client.is_active ? 'Active' : 'Inactive'}
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

export default ClientsPage;

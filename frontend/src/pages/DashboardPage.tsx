import React, { useEffect, useState } from 'react';
import api from '../services/api';
import { useAuth } from '../services/AuthContext';
import { formatHours } from '../utils/helpers';

interface Summary {
  total_hours: number;
  billable_hours: number;
  non_billable_hours: number;
  utilization_rate: number;
  entry_count: number;
  by_project: Record<string, { total: number; billable: number }>;
  by_status: Record<string, number>;
}

const DashboardPage: React.FC = () => {
  const { user } = useAuth();
  const [summary, setSummary] = useState<Summary | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchSummary = async () => {
      try {
        const res = await api.get('/reports/my-summary');
        setSummary(res.data.summary);
      } catch {
        // Handle error silently on dashboard
      } finally {
        setLoading(false);
      }
    };
    fetchSummary();
  }, []);

  if (loading) return <div style={{ padding: '20px' }}>Loading dashboard...</div>;

  return (
    <div>
      <h1 style={{ fontSize: '24px', fontWeight: 700, color: '#1e3a5f', marginBottom: '8px' }}>
        Welcome, {user?.first_name}
      </h1>
      <p style={{ color: '#6b7280', marginBottom: '24px' }}>Here's your timesheet summary for this week</p>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '16px', marginBottom: '32px' }}>
        {[
          { label: 'Total Hours', value: formatHours(summary?.total_hours || 0), color: '#1e3a5f' },
          { label: 'Billable Hours', value: formatHours(summary?.billable_hours || 0), color: '#10b981' },
          { label: 'Utilization Rate', value: `${summary?.utilization_rate || 0}%`, color: '#3b82f6' },
          { label: 'Entries', value: String(summary?.entry_count || 0), color: '#8b5cf6' },
        ].map((card) => (
          <div key={card.label} style={{
            backgroundColor: 'white',
            borderRadius: '8px',
            padding: '20px',
            boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
            borderTop: `3px solid ${card.color}`,
          }}>
            <p style={{ fontSize: '13px', color: '#6b7280', marginBottom: '8px' }}>{card.label}</p>
            <p style={{ fontSize: '28px', fontWeight: 700, color: card.color }}>{card.value}</p>
          </div>
        ))}
      </div>

      {summary?.by_project && Object.keys(summary.by_project).length > 0 && (
        <div style={{ backgroundColor: 'white', borderRadius: '8px', padding: '20px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
          <h2 style={{ fontSize: '16px', fontWeight: 600, marginBottom: '16px', color: '#1e3a5f' }}>Hours by Project</h2>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ borderBottom: '2px solid #e5e7eb' }}>
                <th style={{ textAlign: 'left', padding: '8px', fontSize: '13px', color: '#6b7280' }}>Project</th>
                <th style={{ textAlign: 'right', padding: '8px', fontSize: '13px', color: '#6b7280' }}>Total</th>
                <th style={{ textAlign: 'right', padding: '8px', fontSize: '13px', color: '#6b7280' }}>Billable</th>
              </tr>
            </thead>
            <tbody>
              {Object.entries(summary.by_project).map(([name, data]) => (
                <tr key={name} style={{ borderBottom: '1px solid #f3f4f6' }}>
                  <td style={{ padding: '8px', fontSize: '14px' }}>{name}</td>
                  <td style={{ textAlign: 'right', padding: '8px', fontSize: '14px' }}>{formatHours(data.total)}</td>
                  <td style={{ textAlign: 'right', padding: '8px', fontSize: '14px' }}>{formatHours(data.billable)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default DashboardPage;

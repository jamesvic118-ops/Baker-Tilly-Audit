import React, { useEffect, useState } from 'react';
import api from '../services/api';
import { formatHours } from '../utils/helpers';

interface TeamMember {
  user_id: number;
  name: string;
  total_hours: number;
  billable_hours: number;
  non_billable_hours: number;
  utilization_rate: number;
  entry_count: number;
}

interface TeamSummary {
  period: { start: string; end: string };
  team: TeamMember[];
}

const ReportsPage: React.FC = () => {
  const [summary, setSummary] = useState<TeamSummary | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchReport = async () => {
      try {
        const res = await api.get('/reports/team');
        setSummary(res.data.summary);
      } catch { /* handle */ } finally {
        setLoading(false);
      }
    };
    fetchReport();
  }, []);

  if (loading) return <div>Loading reports...</div>;

  return (
    <div>
      <h1 style={{ fontSize: '24px', fontWeight: 700, color: '#1e3a5f', marginBottom: '8px' }}>Team Reports</h1>
      {summary && (
        <p style={{ color: '#6b7280', marginBottom: '24px', fontSize: '14px' }}>
          Period: {summary.period.start} to {summary.period.end}
        </p>
      )}

      <div style={{ backgroundColor: 'white', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)', overflow: 'hidden' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ backgroundColor: '#f9fafb', borderBottom: '2px solid #e5e7eb' }}>
              {['Team Member', 'Total Hours', 'Billable', 'Non-Billable', 'Utilization', 'Entries'].map(h => (
                <th key={h} style={{ textAlign: 'left', padding: '10px 14px', fontSize: '12px', fontWeight: 600, color: '#6b7280', textTransform: 'uppercase' }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {(!summary || summary.team.length === 0) ? (
              <tr><td colSpan={6} style={{ padding: '40px', textAlign: 'center', color: '#9ca3af' }}>No data for this period.</td></tr>
            ) : summary.team.map(member => (
              <tr key={member.user_id} style={{ borderBottom: '1px solid #f3f4f6' }}>
                <td style={{ padding: '10px 14px', fontSize: '13px', fontWeight: 500 }}>{member.name}</td>
                <td style={{ padding: '10px 14px', fontSize: '13px' }}>{formatHours(member.total_hours)}</td>
                <td style={{ padding: '10px 14px', fontSize: '13px', color: '#10b981' }}>{formatHours(member.billable_hours)}</td>
                <td style={{ padding: '10px 14px', fontSize: '13px', color: '#ef4444' }}>{formatHours(member.non_billable_hours)}</td>
                <td style={{ padding: '10px 14px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <div style={{ backgroundColor: '#e5e7eb', borderRadius: '4px', height: '6px', width: '60px', overflow: 'hidden' }}>
                      <div style={{ backgroundColor: member.utilization_rate >= 70 ? '#10b981' : '#f59e0b', height: '100%', width: `${Math.min(member.utilization_rate, 100)}%` }} />
                    </div>
                    <span style={{ fontSize: '12px', fontWeight: 600 }}>{member.utilization_rate}%</span>
                  </div>
                </td>
                <td style={{ padding: '10px 14px', fontSize: '13px' }}>{member.entry_count}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default ReportsPage;

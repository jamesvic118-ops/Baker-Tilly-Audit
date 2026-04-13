import React, { useEffect, useState, useCallback } from 'react';
import api from '../services/api';
import { formatDate, getStatusColor, toISODate, getWeekStart } from '../utils/helpers';

interface TimesheetEntry {
  id: number;
  project_name: string;
  project_code: string;
  date: string;
  hours: number;
  description: string;
  is_billable: boolean;
  status: string;
}

interface Project {
  id: number;
  name: string;
  code: string;
}

const TimesheetPage: React.FC = () => {
  const [entries, setEntries] = useState<TimesheetEntry[]>([]);
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({ project_id: '', date: toISODate(new Date()), hours: '', description: '', is_billable: true });
  const [error, setError] = useState('');

  const fetchEntries = useCallback(async () => {
    try {
      const weekStart = getWeekStart();
      const weekEnd = new Date(weekStart);
      weekEnd.setDate(weekEnd.getDate() + 6);
      const res = await api.get(`/timesheets?start_date=${toISODate(weekStart)}&end_date=${toISODate(weekEnd)}`);
      setEntries(res.data.entries);
    } catch {
      setError('Failed to load timesheet entries');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchEntries();
    api.get('/projects').then(res => setProjects(res.data.projects)).catch(() => {});
  }, [fetchEntries]);

  const handleSubmitEntry = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    try {
      await api.post('/timesheets', {
        ...formData,
        project_id: Number(formData.project_id),
        hours: Number(formData.hours),
      });
      setShowForm(false);
      setFormData({ project_id: '', date: toISODate(new Date()), hours: '', description: '', is_billable: true });
      fetchEntries();
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to create entry');
    }
  };

  const handleSubmitForApproval = async (ids: number[]) => {
    try {
      await api.post('/timesheets/submit', { entry_ids: ids });
      fetchEntries();
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to submit entries');
    }
  };

  const draftEntries = entries.filter(e => e.status === 'draft');

  if (loading) return <div>Loading timesheets...</div>;

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
        <h1 style={{ fontSize: '24px', fontWeight: 700, color: '#1e3a5f' }}>My Timesheets</h1>
        <div style={{ display: 'flex', gap: '8px' }}>
          {draftEntries.length > 0 && (
            <button
              onClick={() => handleSubmitForApproval(draftEntries.map(e => e.id))}
              style={{ padding: '8px 16px', backgroundColor: '#f59e0b', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer', fontSize: '13px', fontWeight: 600 }}
            >
              Submit All Drafts ({draftEntries.length})
            </button>
          )}
          <button
            onClick={() => setShowForm(!showForm)}
            style={{ padding: '8px 16px', backgroundColor: '#1e3a5f', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer', fontSize: '13px', fontWeight: 600 }}
          >
            + New Entry
          </button>
        </div>
      </div>

      {error && (
        <div style={{ backgroundColor: '#fef2f2', border: '1px solid #fecaca', color: '#dc2626', padding: '10px 14px', borderRadius: '4px', marginBottom: '16px', fontSize: '13px' }}>
          {error}
        </div>
      )}

      {showForm && (
        <div style={{ backgroundColor: 'white', borderRadius: '8px', padding: '20px', marginBottom: '24px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
          <h2 style={{ fontSize: '16px', fontWeight: 600, marginBottom: '16px' }}>New Time Entry</h2>
          <form onSubmit={handleSubmitEntry} style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '12px' }}>
            <div>
              <label style={{ display: 'block', fontSize: '12px', fontWeight: 500, marginBottom: '4px' }}>Project</label>
              <select value={formData.project_id} onChange={e => setFormData({ ...formData, project_id: e.target.value })} required
                style={{ width: '100%', padding: '8px', border: '1px solid #d1d5db', borderRadius: '4px', fontSize: '13px' }}>
                <option value="">Select project</option>
                {projects.map(p => <option key={p.id} value={p.id}>{p.name} ({p.code})</option>)}
              </select>
            </div>
            <div>
              <label style={{ display: 'block', fontSize: '12px', fontWeight: 500, marginBottom: '4px' }}>Date</label>
              <input type="date" value={formData.date} onChange={e => setFormData({ ...formData, date: e.target.value })} required
                style={{ width: '100%', padding: '8px', border: '1px solid #d1d5db', borderRadius: '4px', fontSize: '13px' }} />
            </div>
            <div>
              <label style={{ display: 'block', fontSize: '12px', fontWeight: 500, marginBottom: '4px' }}>Hours</label>
              <input type="number" step="0.25" min="0.25" max="24" value={formData.hours}
                onChange={e => setFormData({ ...formData, hours: e.target.value })} required
                style={{ width: '100%', padding: '8px', border: '1px solid #d1d5db', borderRadius: '4px', fontSize: '13px' }} />
            </div>
            <div style={{ gridColumn: '1 / -1' }}>
              <label style={{ display: 'block', fontSize: '12px', fontWeight: 500, marginBottom: '4px' }}>Description</label>
              <textarea value={formData.description} onChange={e => setFormData({ ...formData, description: e.target.value })}
                rows={2} style={{ width: '100%', padding: '8px', border: '1px solid #d1d5db', borderRadius: '4px', fontSize: '13px', resize: 'vertical' }} />
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
              <label style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '13px' }}>
                <input type="checkbox" checked={formData.is_billable} onChange={e => setFormData({ ...formData, is_billable: e.target.checked })} />
                Billable
              </label>
              <button type="submit" style={{ padding: '8px 20px', backgroundColor: '#10b981', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer', fontSize: '13px', fontWeight: 600 }}>
                Save Entry
              </button>
            </div>
          </form>
        </div>
      )}

      <div style={{ backgroundColor: 'white', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)', overflow: 'hidden' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ backgroundColor: '#f9fafb', borderBottom: '2px solid #e5e7eb' }}>
              {['Date', 'Project', 'Hours', 'Description', 'Billable', 'Status'].map(h => (
                <th key={h} style={{ textAlign: 'left', padding: '10px 14px', fontSize: '12px', fontWeight: 600, color: '#6b7280', textTransform: 'uppercase' }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {entries.length === 0 ? (
              <tr><td colSpan={6} style={{ padding: '40px', textAlign: 'center', color: '#9ca3af' }}>No entries this week. Click "+ New Entry" to get started.</td></tr>
            ) : entries.map(entry => (
              <tr key={entry.id} style={{ borderBottom: '1px solid #f3f4f6' }}>
                <td style={{ padding: '10px 14px', fontSize: '13px' }}>{formatDate(entry.date)}</td>
                <td style={{ padding: '10px 14px', fontSize: '13px' }}>{entry.project_name} <span style={{ color: '#9ca3af' }}>({entry.project_code})</span></td>
                <td style={{ padding: '10px 14px', fontSize: '13px', fontWeight: 600 }}>{entry.hours}h</td>
                <td style={{ padding: '10px 14px', fontSize: '13px', color: '#6b7280', maxWidth: '200px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{entry.description || '—'}</td>
                <td style={{ padding: '10px 14px', fontSize: '13px' }}>{entry.is_billable ? 'Yes' : 'No'}</td>
                <td style={{ padding: '10px 14px' }}>
                  <span style={{ padding: '2px 8px', borderRadius: '10px', fontSize: '11px', fontWeight: 600, color: 'white', backgroundColor: getStatusColor(entry.status), textTransform: 'capitalize' }}>
                    {entry.status}
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

export default TimesheetPage;

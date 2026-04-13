import React, { useEffect, useState } from 'react';
import api from '../services/api';
import { getStatusColor } from '../utils/helpers';

interface Project {
  id: number;
  name: string;
  code: string;
  client_name: string;
  manager_name: string;
  status: string;
  budget_hours: number;
  total_hours_logged: number;
  budget_utilization: number;
  engagement_type: string;
  is_billable: boolean;
}

const ProjectsPage: React.FC = () => {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState('active');

  useEffect(() => {
    const fetchProjects = async () => {
      try {
        const res = await api.get(`/projects?status=${statusFilter}`);
        setProjects(res.data.projects);
      } catch { /* handle */ } finally {
        setLoading(false);
      }
    };
    fetchProjects();
  }, [statusFilter]);

  if (loading) return <div>Loading projects...</div>;

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
        <h1 style={{ fontSize: '24px', fontWeight: 700, color: '#1e3a5f' }}>Projects</h1>
        <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}
          style={{ padding: '8px 12px', border: '1px solid #d1d5db', borderRadius: '4px', fontSize: '13px' }}>
          <option value="all">All Statuses</option>
          <option value="active">Active</option>
          <option value="completed">Completed</option>
          <option value="on_hold">On Hold</option>
        </select>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(350px, 1fr))', gap: '16px' }}>
        {projects.map(project => (
          <div key={project.id} style={{ backgroundColor: 'white', borderRadius: '8px', padding: '20px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '12px' }}>
              <div>
                <h3 style={{ fontSize: '16px', fontWeight: 600, color: '#1e3a5f' }}>{project.name}</h3>
                <p style={{ fontSize: '12px', color: '#9ca3af' }}>{project.code}</p>
              </div>
              <span style={{ padding: '2px 8px', borderRadius: '10px', fontSize: '11px', fontWeight: 600, color: 'white', backgroundColor: getStatusColor(project.status), textTransform: 'capitalize' }}>
                {project.status}
              </span>
            </div>
            <div style={{ fontSize: '13px', color: '#6b7280' }}>
              <p><strong>Client:</strong> {project.client_name}</p>
              <p><strong>Manager:</strong> {project.manager_name || 'Unassigned'}</p>
              <p><strong>Type:</strong> {project.engagement_type || 'N/A'}</p>
              <div style={{ marginTop: '12px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', marginBottom: '4px' }}>
                  <span>Budget: {project.budget_hours}h</span>
                  <span>{project.budget_utilization}%</span>
                </div>
                <div style={{ backgroundColor: '#e5e7eb', borderRadius: '4px', height: '6px', overflow: 'hidden' }}>
                  <div style={{ backgroundColor: project.budget_utilization > 90 ? '#ef4444' : '#10b981', height: '100%', width: `${Math.min(project.budget_utilization, 100)}%`, borderRadius: '4px' }} />
                </div>
              </div>
            </div>
          </div>
        ))}
        {projects.length === 0 && (
          <p style={{ color: '#9ca3af', gridColumn: '1 / -1', textAlign: 'center', padding: '40px' }}>No projects found.</p>
        )}
      </div>
    </div>
  );
};

export default ProjectsPage;

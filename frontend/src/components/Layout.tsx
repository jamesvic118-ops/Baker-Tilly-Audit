import React from 'react';
import { Outlet, NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../services/AuthContext';

const navItems = [
  { path: '/', label: 'Dashboard', roles: ['admin', 'manager', 'staff'] },
  { path: '/timesheets', label: 'Timesheets', roles: ['admin', 'manager', 'staff'] },
  { path: '/projects', label: 'Projects', roles: ['admin', 'manager', 'staff'] },
  { path: '/clients', label: 'Clients', roles: ['admin', 'manager', 'staff'] },
  { path: '/reports', label: 'Reports', roles: ['admin', 'manager'] },
  { path: '/users', label: 'Users', roles: ['admin'] },
];

const Layout: React.FC = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const visibleItems = navItems.filter(
    (item) => user && item.roles.includes(user.role)
  );

  return (
    <div style={{ display: 'flex', minHeight: '100vh' }}>
      <aside style={{
        width: '240px',
        backgroundColor: '#1e3a5f',
        color: 'white',
        padding: '20px 0',
        display: 'flex',
        flexDirection: 'column',
      }}>
        <div style={{ padding: '0 20px 20px', borderBottom: '1px solid rgba(255,255,255,0.1)' }}>
          <h2 style={{ fontSize: '18px', fontWeight: 700 }}>Baker Tilly</h2>
          <p style={{ fontSize: '12px', opacity: 0.7, marginTop: '4px' }}>Liberia Timesheet</p>
        </div>

        <nav style={{ flex: 1, padding: '16px 0' }}>
          {visibleItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              end={item.path === '/'}
              style={({ isActive }) => ({
                display: 'block',
                padding: '10px 20px',
                color: 'white',
                textDecoration: 'none',
                fontSize: '14px',
                backgroundColor: isActive ? 'rgba(255,255,255,0.15)' : 'transparent',
                borderLeft: isActive ? '3px solid #60a5fa' : '3px solid transparent',
              })}
            >
              {item.label}
            </NavLink>
          ))}
        </nav>

        <div style={{ padding: '16px 20px', borderTop: '1px solid rgba(255,255,255,0.1)' }}>
          <p style={{ fontSize: '13px', fontWeight: 500 }}>{user?.full_name}</p>
          <p style={{ fontSize: '11px', opacity: 0.7, textTransform: 'capitalize' }}>{user?.role}</p>
          <button
            onClick={handleLogout}
            style={{
              marginTop: '10px',
              padding: '6px 12px',
              backgroundColor: 'rgba(255,255,255,0.1)',
              color: 'white',
              border: '1px solid rgba(255,255,255,0.2)',
              borderRadius: '4px',
              cursor: 'pointer',
              fontSize: '12px',
              width: '100%',
            }}
          >
            Sign Out
          </button>
        </div>
      </aside>

      <main style={{ flex: 1, backgroundColor: '#f3f4f6', padding: '24px' }}>
        <Outlet />
      </main>
    </div>
  );
};

export default Layout;

import { BrowserRouter, Link, Route, Routes, Navigate, useLocation } from 'react-router-dom';
import { useEffect, useState } from 'react';
import Login from './pages/Login';
import Chat from './pages/Chat';
import Dashboard from './pages/Dashboard';
import Knowledge from './pages/Knowledge';
import './App.css';

function RequireAuth({ children }: { children: React.ReactNode }) {
  const token = localStorage.getItem('token');
  if (!token) return <Navigate to="/login" replace />;
  return <>{children}</>;
}

function Sidebar() {
  const location = useLocation();
  const [username, setUsername] = useState('');

  useEffect(() => {
    const name = localStorage.getItem('username') || 'User';
    setUsername(name);
  }, []);

  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('username');
    window.location.href = '/login';
  };

  const navItems = [
    { path: '/', label: '对话', icon: '💬' },
    { path: '/dashboard', label: '仪表盘', icon: '📊' },
    { path: '/knowledge', label: '知识库', icon: '📚' },
  ];

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <div className="logo">🏭</div>
        <h1>智造 Agent</h1>
      </div>
      <nav className="sidebar-nav">
        {navItems.map((item) => (
          <Link
            key={item.path}
            to={item.path}
            className={`nav-item ${location.pathname === item.path ? 'active' : ''}`}
          >
            <span className="nav-icon">{item.icon}</span>
            <span>{item.label}</span>
          </Link>
        ))}
      </nav>
      <div className="sidebar-footer">
        <div className="user-info">
          <div className="avatar">{username[0]?.toUpperCase()}</div>
          <span className="username">{username}</span>
        </div>
        <button className="logout-btn" onClick={logout}>退出</button>
      </div>
    </aside>
  );
}

function AppLayout() {
  return (
    <div className="app-layout">
      <Sidebar />
      <main className="main-content">
        <Routes>
          <Route path="/" element={<Chat />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/knowledge" element={<Knowledge />} />
        </Routes>
      </main>
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route
          path="/*"
          element={
            <RequireAuth>
              <AppLayout />
            </RequireAuth>
          }
        />
      </Routes>
    </BrowserRouter>
  );
}

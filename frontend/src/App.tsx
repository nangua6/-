import { BrowserRouter, Link, Route, Routes } from 'react-router-dom';
import Login from './pages/Login';
import Chat from './pages/Chat';
import Dashboard from './pages/Dashboard';
import Knowledge from './pages/Knowledge';

export default function App() {
  return (
    <BrowserRouter>
      <div style={{ display: 'flex', height: '100vh' }}>
        <aside style={{ width: 220, borderRight: '1px solid #eee', padding: 16 }}>
          <h3>Manufacturing Agent</h3>
          <nav style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            <Link to="/">Chat</Link>
            <Link to="/dashboard">Dashboard</Link>
            <Link to="/knowledge">Knowledge</Link>
            <Link to="/login">Login</Link>
          </nav>
        </aside>
        <main style={{ flex: 1, padding: 16 }}>
          <Routes>
            <Route path="/" element={<Chat />} />
            <Route path="/login" element={<Login />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/knowledge" element={<Knowledge />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}

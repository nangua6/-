import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api';

export default function Login() {
  const [username, setUsername] = useState('admin');
  const [password, setPassword] = useState('Admin123!');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const login = async () => {
    setError('');
    setLoading(true);
    try {
      const res = await api.post('/api/auth/login', { username, password });
      localStorage.setItem('token', res.data.access_token);
      localStorage.setItem('username', username);
      navigate('/');
    } catch (err: any) {
      setError(err.response?.data?.detail || '登录失败，请检查用户名和密码');
    } finally {
      setLoading(false);
    }
  };

  const handleKey = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') login();
  };

  return (
    <div className="login-page">
      <div className="login-card">
        <div className="logo-area">
          <div className="icon">🏭</div>
          <h1>智造 Agent 平台</h1>
          <p>制造业企业 AI Agent · 自然语言访问业务数据</p>
        </div>

        {error && <div className="login-error">{error}</div>}

        <div className="form-group">
          <label>用户名</label>
          <input
            className="input"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            onKeyDown={handleKey}
            placeholder="请输入用户名"
          />
        </div>

        <div className="form-group">
          <label>密码</label>
          <input
            className="input"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            onKeyDown={handleKey}
            placeholder="请输入密码"
          />
        </div>

        <button className="btn btn-primary" onClick={login} disabled={loading}>
          {loading ? '登录中...' : '登 录'}
        </button>

        <div style={{ marginTop: 20, fontSize: 12, color: '#6c757d', textAlign: 'center' }}>
          <div>管理员: admin / Admin123!</div>
          <div>操作员: operator / Operator123!</div>
        </div>
      </div>
    </div>
  );
}

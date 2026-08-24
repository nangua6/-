import { useState } from 'react';
import api from '../api';

export default function Login() {
  const [username, setUsername] = useState('operator');
  const [password, setPassword] = useState('Operator123!');
  const [message, setMessage] = useState('');

  const login = async () => {
    const res = await api.post('/api/auth/login', { username, password });
    localStorage.setItem('token', res.data.access_token);
    setMessage('登录成功');
  };

  return (
    <div style={{ maxWidth: 360 }}>
      <h2>Login</h2>
      <input value={username} onChange={(e) => setUsername(e.target.value)} placeholder="username" />
      <input value={password} onChange={(e) => setPassword(e.target.value)} placeholder="password" type="password" />
      <button onClick={login}>登录</button>
      {message && <p>{message}</p>}
    </div>
  );
}

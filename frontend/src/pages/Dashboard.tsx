import { useEffect, useState } from 'react';
import api from '../api';

interface Metrics {
  ai_requests: number;
  task_success_rate: number;
  tool_success_rate: number;
  average_latency_ms: number;
  total_tokens: number;
  estimated_cost: number;
  orders: number;
  products: number;
}

export default function Dashboard() {
  const [metrics, setMetrics] = useState<Metrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    setLoading(true);
    api.get('/api/dashboard')
      .then((res) => setMetrics(res.data))
      .catch((err) => setError(err.response?.data?.detail || '加载失败'))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="loading">加载中...</div>;
  if (error) return <div className="login-error">{error}</div>;
  if (!metrics) return null;

  const stats = [
    { label: 'AI 请求总数', value: metrics.ai_requests, icon: '🤖', sub: '所有 Agent 调用' },
    { label: '任务成功率', value: `${(metrics.task_success_rate * 100).toFixed(1)}%`, icon: '✅', sub: '成功 / 总数' },
    { label: '工具成功率', value: `${(metrics.tool_success_rate * 100).toFixed(1)}%`, icon: '🔧', sub: '工具调用成功' },
    { label: '平均延迟', value: `${metrics.average_latency_ms.toFixed(0)} ms`, icon: '⚡', sub: '端到端响应' },
    { label: '总 Tokens', value: metrics.total_tokens.toLocaleString(), icon: '📊', sub: '输入 + 输出' },
    { label: '预估成本', value: `$${metrics.estimated_cost.toFixed(4)}`, icon: '💰', sub: '基于 Token 计费' },
    { label: '订单数量', value: metrics.orders, icon: '📦', sub: '销售订单' },
    { label: '产品数量', value: metrics.products, icon: '🏭', sub: '产品目录' },
  ];

  return (
    <>
      <div className="page-header">
        <h2>📊 运营仪表盘</h2>
        <p>AI Agent 运行指标和业务数据概览</p>
      </div>

      <div className="grid-4">
        {stats.map((s) => (
          <div key={s.label} className="stat-card">
            <div className="label">{s.icon} {s.label}</div>
            <div className="value">{s.value}</div>
            <div className="sub">{s.sub}</div>
          </div>
        ))}
      </div>
    </>
  );
}

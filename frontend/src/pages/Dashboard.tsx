import { useEffect, useState } from 'react';
import api from '../api';

export default function Dashboard() {
  const [metrics, setMetrics] = useState<any>(null);

  useEffect(() => {
    api.get('/api/dashboard').then((res) => setMetrics(res.data));
  }, []);

  if (!metrics) return <div>Loading...</div>;

  return (
    <div>
      <h2>Dashboard</h2>
      <ul>
        <li>AI Requests: {metrics.ai_requests}</li>
        <li>Task Success Rate: {(metrics.task_success_rate * 100).toFixed(1)}%</li>
        <li>Tool Success Rate: {(metrics.tool_success_rate * 100).toFixed(1)}%</li>
        <li>Average Latency: {metrics.average_latency_ms.toFixed(1)} ms</li>
        <li>Total Tokens: {metrics.total_tokens}</li>
        <li>Estimated Cost: ${metrics.estimated_cost.toFixed(4)}</li>
      </ul>
    </div>
  );
}

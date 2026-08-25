import { useState } from 'react';
import api from '../api';

interface Citation {
  index: number;
  source_title?: string;
  section_title?: string;
  page_number?: number;
  chunk_id?: string;
}

interface ChatItem {
  role: string;
  content: string;
  citations?: Citation[];
  tools_called?: string[];
  trace_id?: string;
  model?: string;
  input_tokens?: number;
  output_tokens?: number;
  latency_ms?: number;
}

const QUICK_PROMPTS = [
  '查询GREE-CMP-001压缩机库存',
  'SO20260801订单延期风险',
  '查看SO20260804订单详情',
  '生产异常如何处理？',
];

export default function Chat() {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [message, setMessage] = useState('');
  const [items, setItems] = useState<ChatItem[]>([]);
  const [active, setActive] = useState<ChatItem | null>(null);
  const [sending, setSending] = useState(false);
  const [error, setError] = useState('');

  const ensureSession = async () => {
    if (sessionId) return sessionId;
    const res = await api.post('/api/sessions', { title: 'Web Chat' });
    setSessionId(res.data.id);
    return res.data.id as string;
  };

  const send = async (text?: string) => {
    const msg = text || message;
    if (!msg.trim() || sending) return;

    setError('');
    setSending(true);
    const userItem: ChatItem = { role: 'user', content: msg };
    setItems((prev) => [...prev, userItem]);

    try {
      const sid = await ensureSession();
      const start = performance.now();
      const res = await api.post('/api/agent/completions', { session_id: sid, message: msg });
      const latency_ms = Math.round(performance.now() - start);
      const data = res.data;

      const assistantItem: ChatItem = {
        role: 'assistant',
        content: data.answer,
        citations: data.citations,
        tools_called: data.tools_called,
        trace_id: data.trace_id,
        model: data.model,
        input_tokens: data.input_tokens,
        output_tokens: data.output_tokens,
        latency_ms,
      };
      setItems((prev) => [...prev, assistantItem]);
      setActive(assistantItem);
      setMessage('');
    } catch (err: any) {
      setError(err.response?.data?.detail || '请求失败，请检查后端服务');
      // Remove the user message on error
      setItems((prev) => prev.slice(0, -1));
    } finally {
      setSending(false);
    }
  };

  const handleKey = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      send();
    }
  };

  return (
    <>
      <div className="page-header">
        <h2>💬 智能对话</h2>
        <p>用自然语言查询库存、订单、生产等业务数据</p>
      </div>

      <div className="chat-layout">
        <div className="chat-main card">
          <div className="card-header">
            <span>对话</span>
            {items.length > 0 && (
              <button className="btn btn-ghost" onClick={() => { setItems([]); setActive(null); setSessionId(null); }}>
                清空
              </button>
            )}
          </div>

          <div className="chat-messages">
            {items.length === 0 && (
              <div className="empty-state">
                <div className="icon">🤖</div>
                <p>开始对话吧！试试下面的快捷提问</p>
                <div style={{ marginTop: 16, display: 'flex', flexWrap: 'wrap', gap: 8, justifyContent: 'center' }}>
                  {QUICK_PROMPTS.map((p) => (
                    <button key={p} className="btn btn-ghost" onClick={() => send(p)} style={{ fontSize: 13 }}>
                      {p}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {items.map((item, idx) => (
              <div key={idx} className={`message ${item.role}`}>
                <div className="msg-avatar">
                  {item.role === 'user' ? '👤' : '🤖'}
                </div>
                <div className="msg-body" onClick={() => item.role === 'assistant' && setActive(item)} style={{ cursor: item.role === 'assistant' ? 'pointer' : 'default' }}>
                  {item.content}
                </div>
              </div>
            ))}

            {sending && (
              <div className="message assistant">
                <div className="msg-avatar">🤖</div>
                <div className="msg-body">
                  <div className="loading" style={{ padding: 0 }}>思考中...</div>
                </div>
              </div>
            )}
          </div>

          {error && <div style={{ padding: '0 20px' }}><div className="login-error">{error}</div></div>}

          <div className="chat-input-area">
            <div className="chat-input-row">
              <input
                className="input"
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                onKeyDown={handleKey}
                placeholder="输入消息，如：查询A001当前库存..."
                disabled={sending}
              />
              <button className="btn btn-primary" onClick={() => send()} disabled={sending || !message.trim()}>
                {sending ? '...' : '发送'}
              </button>
            </div>
            <div className="chat-hint">
              按 Enter 发送 · 支持查询库存、订单、生产、采购等业务数据
            </div>
          </div>
        </div>

        <div className="chat-panel card">
          <div className="card-header">执行详情</div>
          <div className="card-body">
            {!active ? (
              <div className="empty-state" style={{ padding: 30 }}>
                <div className="icon" style={{ fontSize: 32 }}>📋</div>
                <p>发送消息后，这里展示工具调用、引用和 Trace 信息</p>
              </div>
            ) : (
              <>
                <div className="detail-section">
                  <h4>🔍 Trace</h4>
                  <div className="detail-item">
                    <span className="label">模型</span>
                    <span className="value">{active.model || '-'}</span>
                  </div>
                  <div className="detail-item">
                    <span className="label">延迟</span>
                    <span className="value">{active.latency_ms} ms</span>
                  </div>
                  <div className="detail-item">
                    <span className="label">输入 Tokens</span>
                    <span className="value">{active.input_tokens}</span>
                  </div>
                  <div className="detail-item">
                    <span className="label">输出 Tokens</span>
                    <span className="value">{active.output_tokens}</span>
                  </div>
                  <div className="detail-item">
                    <span className="label">Trace ID</span>
                    <span className="value" style={{ fontSize: 11, wordBreak: 'break-all' }}>{active.trace_id}</span>
                  </div>
                </div>

                <div className="detail-section">
                  <h4>🔧 工具调用</h4>
                  {active.tools_called && active.tools_called.length > 0 ? (
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4 }}>
                      {active.tools_called.map((t, i) => (
                        <span key={i} className="tool-tag">✓ {t}</span>
                      ))}
                    </div>
                  ) : (
                    <p style={{ fontSize: 13, color: '#6c757d' }}>无工具调用</p>
                  )}
                </div>

                <div className="detail-section">
                  <h4>📚 引用来源</h4>
                  {active.citations && active.citations.length > 0 ? (
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4 }}>
                      {active.citations.map((c) => (
                        <span key={c.index} className="citation-tag">
                          [{c.index}] {c.source_title}
                          {c.section_title ? ` - ${c.section_title}` : ''}
                        </span>
                      ))}
                    </div>
                  ) : (
                    <p style={{ fontSize: 13, color: '#6c757d' }}>无引用来源</p>
                  )}
                </div>
              </>
            )}
          </div>
        </div>
      </div>
    </>
  );
}

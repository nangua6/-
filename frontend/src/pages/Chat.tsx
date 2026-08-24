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

export default function Chat() {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [message, setMessage] = useState('查询A001当前库存');
  const [items, setItems] = useState<ChatItem[]>([]);
  const [active, setActive] = useState<ChatItem | null>(null);

  const ensureSession = async () => {
    if (sessionId) return sessionId;
    const res = await api.post('/api/sessions', { title: 'Web Chat' });
    setSessionId(res.data.id);
    return res.data.id as string;
  };

  const send = async () => {
    const sid = await ensureSession();
    const userItem: ChatItem = { role: 'user', content: message };
    setItems((prev) => [...prev, userItem]);

    const start = performance.now();
    const res = await api.post('/api/agent/completions', { session_id: sid, message });
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
  };

  return (
    <div style={{ display: 'grid', gridTemplateColumns: '1fr 360px', gap: 16, height: '100%' }}>
      <div>
        <h2>Chat</h2>
        <div style={{ display: 'flex', gap: 8 }}>
          <input style={{ flex: 1 }} value={message} onChange={(e) => setMessage(e.target.value)} />
          <button onClick={send}>发送</button>
        </div>
        <div style={{ marginTop: 16 }}>
          {items.map((item, idx) => (
            <div key={idx} style={{ marginBottom: 12, cursor: 'pointer' }} onClick={() => item.role === 'assistant' && setActive(item)}>
              <div><strong>{item.role}</strong></div>
              <div style={{ whiteSpace: 'pre-wrap' }}>{item.content}</div>
            </div>
          ))}
        </div>
      </div>

      <aside style={{ borderLeft: '1px solid #eee', paddingLeft: 16 }}>
        <h3>执行详情</h3>
        {!active && <div>发送一条消息后，这里会展示工具、引用和 Trace。</div>}
        {active && (
          <div>
            <section>
              <h4>Trace</h4>
              <div>trace_id: {active.trace_id}</div>
              <div>model: {active.model}</div>
              <div>latency: {active.latency_ms} ms</div>
              <div>input_tokens: {active.input_tokens}</div>
              <div>output_tokens: {active.output_tokens}</div>
            </section>

            <section>
              <h4>Tool Calling</h4>
              {active.tools_called && active.tools_called.length > 0 ? (
                <ul>
                  {active.tools_called.map((t, i) => (
                    <li key={i}>✓ {t}</li>
                  ))}
                </ul>
              ) : (
                <div>无工具调用</div>
              )}
            </section>

            <section>
              <h4>RAG Sources</h4>
              {active.citations && active.citations.length > 0 ? (
                <ul>
                  {active.citations.map((c) => (
                    <li key={c.index}>[{c.index}] {c.source_title} {c.section_title ? `- ${c.section_title}` : ''}</li>
                  ))}
                </ul>
              ) : (
                <div>无引用来源</div>
              )}
            </section>
          </div>
        )}
      </aside>
    </div>
  );
}

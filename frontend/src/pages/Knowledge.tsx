import { useEffect, useState, useRef } from 'react';
import api from '../api';

interface Document {
  id: string;
  title: string;
  source_type: string;
  created_at: string;
}

export default function Knowledge() {
  const [docs, setDocs] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState('');
  const [toast, setToast] = useState('');
  const fileRef = useRef<HTMLInputElement>(null);

  const loadDocs = () => {
    setLoading(true);
    api.get('/api/knowledge/documents')
      .then((res) => setDocs(res.data))
      .catch((err) => setError(err.response?.data?.detail || '加载失败'))
      .finally(() => setLoading(false));
  };

  useEffect(() => { loadDocs(); }, []);

  const showToast = (msg: string) => {
    setToast(msg);
    setTimeout(() => setToast(''), 3000);
  };

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      await api.post('/api/knowledge/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      showToast(`"${file.name}" 上传成功`);
      loadDocs();
    } catch (err: any) {
      showToast(err.response?.data?.detail || '上传失败');
    } finally {
      setUploading(false);
      if (fileRef.current) fileRef.current.value = '';
    }
  };

  return (
    <>
      {toast && <div className="toast toast-success">{toast}</div>}

      <div className="page-header">
        <h2>📚 知识库管理</h2>
        <p>上传文档，AI 会自动分块、向量化，用于 RAG 检索</p>
      </div>

      <div className="upload-area" onClick={() => fileRef.current?.click()}>
        <div className="icon">{uploading ? '⏳' : '📄'}</div>
        <p>{uploading ? '上传中...' : '点击上传文档（支持 .md / .txt / .pdf / .docx）'}</p>
        <input
          ref={fileRef}
          type="file"
          accept=".md,.txt,.pdf,.docx"
          onChange={handleUpload}
          style={{ display: 'none' }}
        />
      </div>

      <div className="card">
        <div className="card-header">
          <span>文档列表</span>
          <span className="badge badge-info">{docs.length} 个文档</span>
        </div>
        <div className="card-body">
          {loading ? (
            <div className="loading">加载中...</div>
          ) : error ? (
            <div className="login-error">{error}</div>
          ) : docs.length === 0 ? (
            <div className="empty-state">
              <div className="icon">📭</div>
              <p>暂无文档，上传第一个文档开始吧</p>
            </div>
          ) : (
            <div className="doc-list">
              {docs.map((d) => (
                <div key={d.id} className="doc-item">
                  <div className="doc-info">
                    <div className="doc-icon">
                      {d.source_type === 'pdf' ? '📕' : d.source_type === 'docx' ? '📘' : '📝'}
                    </div>
                    <div>
                      <div className="doc-title">{d.title}</div>
                      <div className="doc-meta">
                        {d.source_type.toUpperCase()} · {new Date(d.created_at).toLocaleDateString('zh-CN')}
                      </div>
                    </div>
                  </div>
                  <span className="badge badge-success">已索引</span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </>
  );
}

import { useEffect, useState } from 'react';
import api from '../api';

export default function Knowledge() {
  const [docs, setDocs] = useState<any[]>([]);

  useEffect(() => {
    api.get('/api/knowledge/documents').then((res) => setDocs(res.data));
  }, []);

  return (
    <div>
      <h2>Knowledge</h2>
      <ul>
        {docs.map((d) => (
          <li key={d.id}>{d.title} - {d.source_type}</li>
        ))}
      </ul>
    </div>
  );
}

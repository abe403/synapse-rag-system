import { useState, useRef, useEffect } from 'react';
import './App.css';

function App() {
  const [query, setQuery] = useState('');
  const [chatHistory, setChatHistory] = useState<{ role: 'user' | 'ai'; text: string }[]>([]);
  const [loading, setLoading] = useState(false);
  const endOfMessagesRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    endOfMessagesRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [chatHistory]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    const userMessage = query;
    setChatHistory(prev => [...prev, { role: 'user', text: userMessage }]);
    setQuery('');
    setLoading(true);

    try {
      const apiHost = window.location.hostname;
      const response = await fetch(`http://${apiHost}:8000/api/chat?query=${encodeURIComponent(userMessage)}`, {
        method: 'POST',
      });

      if (!response.body) throw new Error("No response body");

      const reader = response.body.getReader();
      const decoder = new TextDecoder("utf-8");
      
      setChatHistory(prev => [...prev, { role: 'ai', text: '' }]);

      let done = false;
      while (!done) {
        const { value, done: readerDone } = await reader.read();
        done = readerDone;
        if (value) {
          const chunk = decoder.decode(value, { stream: true });
          const lines = chunk.split('\n');
          for (const line of lines) {
            if (line.startsWith('data: ') && line !== 'data: [DONE]') {
              const text = line.replace('data: ', '');
              setChatHistory(prev => {
                const newHistory = [...prev];
                const lastMsg = newHistory[newHistory.length - 1];
                lastMsg.text += text;
                return newHistory;
              });
            }
          }
        }
      }
    } catch (error) {
      console.error("Error fetching chat:", error);
      setChatHistory(prev => [...prev, { role: 'ai', text: 'Error connecting to Synapse API.' }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-container">
      <header className="header">
        <h1>Synapse - Context-Aware Enterprise AI</h1>
        <p>Multi-Document RAG System</p>
      </header>

      <div className="main-content">
        <div className="chat-pane">
          <div className="chat-history">
            {chatHistory.map((msg, idx) => (
              <div key={idx} className={`message ${msg.role}`}>
                <strong>{msg.role === 'user' ? 'You' : 'Synapse'}: </strong>
                <span>{msg.text}</span>
              </div>
            ))}
            {loading && <div className="message ai">Thinking...</div>}
            <div ref={endOfMessagesRef} />
          </div>

          <form onSubmit={handleSubmit} className="input-form">
            <input 
              type="text" 
              value={query} 
              onChange={(e) => setQuery(e.target.value)} 
              placeholder="Ask about enterprise documents..."
              disabled={loading}
            />
            <button type="submit" disabled={loading || !query.trim()}>Send</button>
          </form>
        </div>

        <div className="context-pane">
          <h2>Data Lineage & Citations</h2>
          <div className="citation-box">
            <p className="hint">When you submit a query, the MCP Retrieval Server fetches relevant chunks via FAISS.</p>
            <p><strong>Latency Requirement:</strong> Sub-200ms</p>
            <p><strong>Vector Engine:</strong> PyTorch Embeddings</p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;

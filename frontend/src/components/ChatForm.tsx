import { useState, useRef, useEffect } from 'react';
import { askQuestion, submitClaim } from '../api';

type Claim = { id: string; text: string; weight: number };
type Message = {
  role: 'user' | 'bot';
  text?: string;
  files?: File[];
  buttons?: string[];
};

export default function ChatForm() {
  const [question, setQuestion] = useState('');
  const [files, setFiles] = useState<File[]>([]);
  const [messages, setMessages] = useState<Message[]>([]);
  const [lastQuestion, setLastQuestion] = useState('');
  const [lastFiles, setLastFiles] = useState<File[]>([]);
  const [claimOptions, setClaimOptions] = useState<Claim[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!question.trim() && files.length === 0) return;

    const newMessage: Message = {
      role: 'user',
      text: question.trim() || undefined,
      files: files.length > 0 ? files : undefined
    };
    setMessages(prev => [...prev, newMessage]);

    setLastQuestion(question.trim());
    setLastFiles(files);
    setQuestion('');
    setFiles([]);
    if (fileInputRef.current) fileInputRef.current.value = '';

    try {
      const res = await askQuestion(question, files);

      if (Array.isArray(res)) {
        if (res.length === 1) {
          const claim = res[0];
          setMessages(prev => [...prev, { role: 'bot', text: `${claim.text}` }]);
        } else {
          const claimTexts = res.map(c => `${c.text}`);
          setClaimOptions(res);
          setMessages(prev => [
            ...prev,
            {
              role: 'bot',
              text: 'Sono stati trovati più claim con lo stesso peso. Scegli quello che vuoi approfondire:',
              buttons: claimTexts
            }
          ]);
        }
      } else {
        setMessages(prev => [...prev, { role: 'bot', text: res }]);
      }
    } catch (err) {
      setMessages(prev => [...prev, { role: 'bot', text: 'Errore nella richiesta' }]);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newFiles = Array.from(e.target.files || []);
    setFiles(prev => {
      const allFiles = [...prev, ...newFiles];
      const uniqueFiles = Array.from(new Map(allFiles.map(f => [f.name, f])).values());
      return uniqueFiles;
    });
  };

  const handleClaimClick = async (claimText: string) => {
    const selected = claimOptions.find(c => `${c.text}` === claimText);

    setMessages(prev => [
      ...prev.filter(m => !m.buttons),
      { role: 'bot', text: `${claimText}` }
    ]);

    if (selected) {
      try {
        const res = await submitClaim(lastQuestion, lastFiles, selected.id);
        if (res) {
          setMessages(prev => [...prev, { role: 'bot', text: String(res) }]);
        }
      } catch (err) {
        setMessages(prev => [...prev, { role: 'bot', text: 'Errore durante il salvataggio del claim' }]);
      }
    }
  };

  return (
    <div style={{
      maxWidth: '700px',
      margin: '40px auto',
      fontFamily: 'system-ui, sans-serif',
      display: 'flex',
      flexDirection: 'column',
      gap: '12px'
    }}>
      <h2 style={{ textAlign: 'center', color: '#333', fontSize: '22px' }}>💬 Chatbot con Fact-Checking</h2>

      <div style={{
        border: '1px solid #ddd',
        borderRadius: '14px',
        padding: '18px',
        height: '420px',
        overflowY: 'auto',
        background: '#fefefe',
        boxShadow: '0 2px 6px rgba(0,0,0,0.05)'
      }}>
        {messages.map((m, idx) => (
          <div key={idx} style={{
            display: 'flex',
            justifyContent: m.role === 'user' ? 'flex-end' : 'flex-start',
            marginBottom: '12px'
          }}>
            <div style={{
              maxWidth: '75%',
              padding: '14px 16px',
              borderRadius: '20px',
              background: m.role === 'user' ? 'linear-gradient(135deg, #007bff, #3399ff)' : '#f0f0f0',
              color: m.role === 'user' ? '#fff' : '#333',
              boxShadow: '0 1px 4px rgba(0,0,0,0.1)',
              whiteSpace: 'pre-wrap',
              fontSize: '15px'
            }}>
              {m.text && <div>{m.text}</div>}
              {m.files && (
                <div style={{ marginTop: '8px' }}>
                  <strong>📎 File allegati:</strong>
                  <ul style={{ paddingLeft: '20px', margin: '5px 0' }}>
                    {m.files.map((file, i) => (
                      <li key={i}>{file.name}</li>
                    ))}
                  </ul>
                </div>
              )}
              {m.buttons && (
                <div style={{ marginTop: '10px', display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                  {m.buttons.map((btnText, i) => (
                    <button
                      key={i}
                      onClick={() => handleClaimClick(btnText)}
                      style={{
                        padding: '8px 14px',
                        borderRadius: '8px',
                        border: '1px solid #007bff',
                        background: '#fff',
                        color: '#007bff',
                        cursor: 'pointer',
                        fontSize: '14px',
                        transition: 'all 0.2s ease'
                      }}
                      onMouseOver={e => e.currentTarget.style.background = '#e6f0ff'}
                      onMouseOut={e => e.currentTarget.style.background = '#fff'}
                    >
                      {btnText}
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      <form onSubmit={handleSubmit} style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
        <textarea
          value={question}
          onChange={e => setQuestion(e.target.value)}
          onKeyDown={e => {
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault();
              handleSubmit(e);
            }
          }}
          placeholder="Scrivi la tua domanda..."
          rows={2}
          style={{
            flex: 1,
            padding: '12px',
            borderRadius: '10px',
            border: '1px solid #ccc',
            fontSize: '15px',
            resize: 'none'
          }}
        />

        <div style={{ position: 'relative' }}>
          <button
            type="button"
            onClick={() => fileInputRef.current?.click()}
            style={{
              width: '38px',
              height: '38px',
              borderRadius: '50%',
              background: '#007bff',
              color: '#fff',
              border: 'none',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              transition: 'background 0.2s ease'
            }}
            onMouseOver={e => e.currentTarget.style.background = '#0056b3'}
            onMouseOut={e => e.currentTarget.style.background = '#007bff'}
            title="Aggiungi file"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="20"
              height="20"
              fill="currentColor"
              viewBox="0 0 16 16"
            >
              <path d="M8 4a.5.5 0 0 1 .5.5v3h3a.5.5 0 0 1 0 1h-3v3a.5.5 0 0 1-1 0v-3h-3a.5.5 0 0 1 0-1h3v-3A.5.5 0 0 1 8 4z"/>
            </svg>
          </button>

          <input
            type="file"
            multiple
            ref={fileInputRef}
            onChange={handleFileChange}
            style={{
              position: 'absolute',
              left: 0,
              top: 0,
              width: '100%',
              height: '100%',
                            opacity: 0,
              pointerEvents: 'none'
            }}
          />
        </div>

        <button
  type="submit"
  style={{
    width: '38px',
    height: '38px',
    borderRadius: '50%',
    background: '#007bff',
    color: '#fff',
    border: 'none',
    cursor: 'pointer',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    transition: 'background 0.2s ease'
  }}
  onMouseOver={e => e.currentTarget.style.background = '#0056b3'}
  onMouseOut={e => e.currentTarget.style.background = '#007bff'}
  title="Invia"
>
  <svg
    xmlns="http://www.w3.org/2000/svg"
    width="18"
    height="18"
    fill="currentColor"
    viewBox="0 0 16 16"
  >
    <path fillRule="evenodd" d="M8 12a.5.5 0 0 0 .5-.5V5.707l2.15 2.147a.5.5 0 0 0 .7-.708l-3-3a.5.5 0 0 0-.7 0l-3 3a.5.5 0 0 0 .7.708L7.5 5.707V11.5A.5.5 0 0 0 8 12z"/>
  </svg>
</button>
      </form>

      {files.length > 0 && (
        <div style={{ fontSize: '14px', color: '#555' }}>
          <strong>📎 File selezionati:</strong>
          <ul style={{ margin: '6px 0 0 20px' }}>
            {files.map((file, i) => (
              <li key={i}>{file.name}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

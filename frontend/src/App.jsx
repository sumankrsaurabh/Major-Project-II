import { useState, useEffect } from 'react';
import './App.css';
import FileUpload from './components/FileUpload';
import ChatWindow from './components/ChatWindow';
import ServerStatus from './components/ServerStatus';
import { FileText } from 'lucide-react';

function App() {
  const [isReady, setIsReady] = useState(false);
  const [serverStatus, setServerStatus] = useState('checking');
  const [fileName, setFileName] = useState('');

  useEffect(() => {
    const checkHealth = async () => {
      try {
        const response = await fetch('http://localhost:8000/health');
        if (response.ok) {
          const data = await response.json();
          setServerStatus(data.status);
        } else {
          setServerStatus('error');
        }
      } catch (err) {
        setServerStatus('offline');
      }
    };

    checkHealth();
    const interval = setInterval(checkHealth, 30000);
    return () => clearInterval(interval);
  }, []);

  const handleUploadSuccess = (file) => {
    setIsReady(true);
    setFileName(file);
  };

  return (
    <div className="min-h-screen bg-white flex flex-col">
      {/* Header */}
      <header className="border-b border-gray-200 bg-white">
        <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-blue-600 flex items-center justify-center">
              <FileText size={24} className="text-white" />
            </div>
            <div>
              <h1 className="text-xl font-semibold text-gray-900">Chat with PDF</h1>
              <p className="text-xs text-gray-500 mt-0.5">AI-powered document analysis</p>
            </div>
          </div>
          <ServerStatus status={serverStatus} />
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 flex flex-col max-w-6xl mx-auto w-full px-6 py-8">
        {!isReady ? (
          <>
            {/* Upload Section */}
            <div className="flex-1 flex items-center justify-center">
              <div className="w-full max-w-md">
                <FileUpload onUploadSuccess={handleUploadSuccess} />
              </div>
            </div>

            {/* Features Section */}
            <div className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-8">
              <div className="text-center">
                <div className="text-3xl mb-3">⚡</div>
                <h3 className="font-semibold text-gray-900 mb-1">Fast Processing</h3>
                <p className="text-sm text-gray-600">Get answers instantly</p>
              </div>
              <div className="text-center">
                <div className="text-3xl mb-3">🎯</div>
                <h3 className="font-semibold text-gray-900 mb-1">Accurate Results</h3>
                <p className="text-sm text-gray-600">Source-backed answers</p>
              </div>
              <div className="text-center">
                <div className="text-3xl mb-3">🔒</div>
                <h3 className="font-semibold text-gray-900 mb-1">Private & Secure</h3>
                <p className="text-sm text-gray-600">Local processing only</p>
              </div>
            </div>
          </>
        ) : (
          <div className="flex-1 flex flex-col bg-white rounded-lg border border-gray-200 overflow-hidden">
            {/* Chat Header */}
            <div className="border-b border-gray-200 bg-gray-50 px-6 py-4 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-2 h-2 rounded-full bg-green-500"></div>
                <span className="text-sm font-medium text-gray-900">{fileName ? `📄 ${fileName}` : 'Document ready'}</span>
              </div>
              <button
                onClick={() => {
                  setIsReady(false);
                  setFileName('');
                }}
                className="text-sm px-3 py-1.5 text-gray-600 hover:text-gray-900 border border-gray-300 rounded-md hover:bg-gray-50 transition-colors"
              >
                New PDF
              </button>
            </div>

            {/* Chat Window */}
            <div className="flex-1 overflow-hidden">
              <ChatWindow onUploadNew={() => {
                setIsReady(false);
                setFileName('');
              }} />
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-gray-200 bg-gray-50">
        <div className="max-w-6xl mx-auto px-6 py-4 text-center text-xs text-gray-600">
          Powered by FastAPI • LangChain • FAISS • Groq & Gemini LLMs
        </div>
      </footer>
    </div>
  );
}

export default App;

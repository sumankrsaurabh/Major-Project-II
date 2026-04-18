import React, { useState } from 'react';
import './App.css';
import FileUpload from './components/FileUpload';
import ChatInterface from './components/ChatInterface';

function App() {
  const [pdfUploaded, setPdfUploaded] = useState(false);
  const [uploadedFileName, setUploadedFileName] = useState('');

  const handleUploadSuccess = (fileName) => {
    setPdfUploaded(true);
    setUploadedFileName(fileName);
  };

  const handleReset = () => {
    setPdfUploaded(false);
    setUploadedFileName('');
  };

  return (
    <div className="app">
      <header className="header">
        <div className="header-content">
          <h1>📄 Chat with PDF</h1>
          <p>AI-powered document question answering with RAG</p>
        </div>
      </header>

      <main className="main-content">
        <div className="container">
          {!pdfUploaded ? (
            <FileUpload onUploadSuccess={handleUploadSuccess} />
          ) : (
            <div className="chat-section">
              <div className="uploaded-file-info">
                <span className="file-icon">✓</span>
                <div className="file-details">
                  <p className="file-name">{uploadedFileName}</p>
                  <p className="file-status">Ready for questions</p>
                </div>
                <button className="reset-btn" onClick={handleReset} title="Upload new PDF">
                  ↻
                </button>
              </div>
              <ChatInterface />
            </div>
          )}
        </div>
      </main>

      <footer className="footer">
        <p>Powered by RAG (Retrieval Augmented Generation) with LLMs</p>
      </footer>
    </div>
  );
}

export default App;

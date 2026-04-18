import React, { useState, useCallback } from 'react';
import './App.css';
import Navbar from './components/Navbar';
import Sidebar from './components/Sidebar';
import RightPanel from './components/RightPanel';
import FileUpload from './components/FileUpload';
import ChatInterface from './components/ChatInterface';
import LoadingAnimation from './components/LoadingAnimation';

function App() {
  const [pdfUploaded, setPdfUploaded] = useState(false);
  const [uploadedFileName, setUploadedFileName] = useState('');
  const [sessionId, setSessionId] = useState(null);
  const [uploadStatus, setUploadStatus] = useState('idle');
  const [stats, setStats] = useState({ total: 0, avgConfidence: 0, activeTime: '0s' });
  const [currentMessage, setCurrentMessage] = useState(null);

  const handleUploadSuccess = useCallback((fileName) => {
    setPdfUploaded(true);
    setUploadedFileName(fileName);
    const newSessionId = Math.random().toString(36).substring(7);
    setSessionId(newSessionId);
    setUploadStatus('idle');
  }, []);

  const handleReset = useCallback(() => {
    setPdfUploaded(false);
    setUploadedFileName('');
    setSessionId(null);
    setCurrentMessage(null);
  }, []);

  const handleStatsUpdate = useCallback((newStats) => {
    setStats(prev => ({ ...prev, ...newStats }));
  }, []);

  return (
    <div className="mui-app-root">
      <Navbar 
        pdfUploaded={pdfUploaded} 
        uploadedFileName={uploadedFileName} 
        onReset={handleReset} 
      />

      <div className="mui-layout-body">
        {pdfUploaded && <Sidebar sessionId={sessionId} />}

        <main className="mui-container">
          {!pdfUploaded ? (
            <div className="mui-container-upload">
              <div className="mui-typography-center">
                <h2 className="mui-h4 mui-upload-title">Welcome to RAG Chat</h2>
                <p className="mui-subtitle1">Upload a PDF document to begin the analysis</p>
              </div>
              
              <div className="mui-card-wrapper">
                <FileUpload 
                  onUploadSuccess={handleUploadSuccess}
                  onStatusChange={setUploadStatus}
                />
              </div>

              {uploadStatus !== 'idle' && (
                <div className="mui-loading-wrapper">
                  <LoadingAnimation 
                    status={uploadStatus}
                    message={
                      uploadStatus === 'validating' ? 'Validating PDF format...' :
                      uploadStatus === 'uploading' ? 'Uploading securely...' :
                      uploadStatus === 'processing' ? 'Processing PDF vectors...' :
                      'Upload complete!'
                    }
                  />
                </div>
              )}
            </div>
          ) : (
            <div className="mui-container-chat">
              <ChatInterface 
                onStatsUpdate={handleStatsUpdate} 
                onMessageUpdate={(msg) => setCurrentMessage(msg)} 
                sessionId={sessionId}
              />
            </div>
          )}
        </main>

        {pdfUploaded && <RightPanel currentMessage={currentMessage} stats={stats} />}
      </div>
    </div>
  );
}

export default App;

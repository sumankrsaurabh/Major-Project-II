import { useEffect, useMemo, useState } from 'react'
import './App.css'
import Sidebar from './components/Sidebar'
import FileUpload from './components/FileUpload'
import { chatService, pdfService } from './services/api'

const initialStatus = {
  pdf_uploaded: false,
  filename: 'No file uploaded',
  chunks: 0,
  file_size_mb: 0,
  server_status: 'idle',
  models_loaded: false,
}

function App() {
  const [workspaceId] = useState(() => {
    const storageKey = 'yuktara.chatwithpdf.workspace.v1'
    let id = window.localStorage.getItem(storageKey)
    if (!id) {
      id = window.crypto.randomUUID()
      window.localStorage.setItem(storageKey, id)
    }
    return id
  })
  const [sessionId] = useState(() => window.crypto.randomUUID())
  const [activeTab, setActiveTab] = useState('upload')
  const [pdfStatus, setPdfStatus] = useState(initialStatus)
  const [chatQuery, setChatQuery] = useState('')
  const [chatHistory, setChatHistory] = useState([])
  const [isChatLoading, setIsChatLoading] = useState(false)
  const [errorMessage, setErrorMessage] = useState('')

  useEffect(() => {
    const loadStatus = async () => {
      try {
        const response = await pdfService.getStatus(workspaceId)
        if (response && response.server_status) {
          setPdfStatus((prev) => ({
            ...prev,
            ...response,
            pdf_uploaded: response.pdf_uploaded ?? prev.pdf_uploaded,
            filename: response.filename || prev.filename,
            chunks: response.chunks ?? prev.chunks,
            file_size_mb: response.file_size_mb ?? prev.file_size_mb,
            server_status: response.server_status || prev.server_status,
            models_loaded: response.models_loaded ?? prev.models_loaded,
          }))
        }
      } catch (error) {
        console.warn('Unable to load PDF status', error)
      }
    }

    loadStatus()
  }, [workspaceId])

  const handleUploadSuccess = (status) => {
    if (status) {
      setPdfStatus((prev) => ({ ...prev, ...status, pdf_uploaded: true }))
    }
    setActiveTab('chat')
  }

  const handleSendChat = async () => {
    const text = chatQuery.trim()
    if (!text || !pdfStatus.pdf_uploaded) {
      return
    }

    const userMessage = {
      id: `user-${Date.now()}`,
      role: 'user',
      text,
    }

    setChatHistory((history) => [...history, userMessage])
    setChatQuery('')
    setErrorMessage('')
    setIsChatLoading(true)

    try {
      const response = await chatService.askQuestion(text, sessionId, workspaceId)
      const answerText = response?.answer || response?.message || response?.data || 'No answer available.'
      const assistantMessage = {
        id: `ai-${Date.now()}`,
        role: 'assistant',
        text: answerText,
      }
      setChatHistory((history) => [...history, assistantMessage])
    } catch (error) {
      setErrorMessage(error.message || 'Unable to send message. Please try again.')
    } finally {
      setIsChatLoading(false)
    }
  }

  const selectedFeature = useMemo(() => {
    if (activeTab === 'upload') return 'Upload documents and build your knowledge base.'
    if (activeTab === 'chat') return 'Ask your PDF direct questions with AI-powered context.'
    if (activeTab === 'analytics') return 'Review insights, document structure, and relevance scoring.'
    return 'Access developer tools for fine-grained control and diagnostics.'
  }, [activeTab])

  return (
    <div className="app-shell">
      <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} pdfStatus={pdfStatus} />
      <main className="app-content">
        <div className="page-header glass-panel">
          <div className="header-copy">
            <span className="eyebrow">AI Document Intelligence</span>
            <h1>Secure local PDF analysis built for modern workflows</h1>
            <p>
              Upload PDFs, extract semantic embeddings, and ask context-aware questions from a responsive AI dashboard with developer-focused controls.
            </p>
          </div>
          <div className="header-actions">
            <div className="status-pill">
              <span className="status-dot" /> {pdfStatus.server_status || 'idle'}
            </div>
            <div className="header-metrics">
              <div>
                <strong>{pdfStatus.chunks}</strong>
                <span>Context nodes</span>
              </div>
              <div>
                <strong>{Math.round(pdfStatus.file_size_mb)}</strong>
                <span>File MB</span>
              </div>
              <div>
                <strong>{pdfStatus.models_loaded ? 'Active' : 'Loading'}</strong>
                <span>Model status</span>
              </div>
            </div>
          </div>
        </div>

        <div className="section-grid">
          <div className="section-card glass-panel">
            <h2>Current Workspace</h2>
            <p>{selectedFeature}</p>
            <div className="card-pill-group">
              <span>{pdfStatus.pdf_uploaded ? 'File loaded' : 'Waiting for upload'}</span>
              <span>{pdfStatus.filename}</span>
            </div>
          </div>

          <div className="section-card glass-panel quick-actions">
            <h2>Ready to build</h2>
            <p>
              The platform is already configured for fast uploads, AI chat, and analytics. Use the sidebar to switch modes.
            </p>
            <div className="action-list">
              <div>
                <strong>Upload</strong>
                <p>Drop a PDF to start a new knowledge session.</p>
              </div>
              <div>
                <strong>Chat</strong>
                <p>Ask questions about the document once it's processed.</p>
              </div>
              <div>
                <strong>Inspect</strong>
                <p>View analytics and debug server health anytime.</p>
              </div>
            </div>
          </div>
        </div>

        <section className="tab-panel glass-panel">
          <div className="tab-title-row">
            <div>
              <h2>{activeTab === 'upload' ? 'Upload Experience' : activeTab === 'chat' ? 'AI Chat Assistant' : activeTab === 'analytics' ? 'Analytics Overview' : 'Developer Toolkit'}</h2>
              <p>{selectedFeature}</p>
            </div>
            <span className="tab-badge">Current mode</span>
          </div>

          {activeTab === 'upload' && (
            <FileUpload workspaceId={workspaceId} pdfStatus={pdfStatus} setPdfStatus={setPdfStatus} onUploadSuccess={handleUploadSuccess} />
          )}

          {activeTab === 'chat' && (
            <div className="chat-panel">
              <div className="chat-info">
                <div>
                  <h3>Ask your document anything</h3>
                  <p>Send a question and get answers directly from the uploaded PDF context.</p>
                </div>
                <div className={`chat-tag ${pdfStatus.pdf_uploaded ? 'enabled' : 'disabled'}`}>
                  {pdfStatus.pdf_uploaded ? 'Ready to chat' : 'Upload a PDF first'}
                </div>
              </div>

              <div className="chat-window">
                {!pdfStatus.pdf_uploaded ? (
                  <div className="empty-state">
                    <h4>Upload a PDF to enable chat</h4>
                    <p>The chat engine will become interactive after your document has been processed.</p>
                  </div>
                ) : (
                  chatHistory.length > 0 ? (
                    chatHistory.map((message) => (
                      <div key={message.id} className={`chat-message ${message.role}`}>
                        <span className="message-author">{message.role === 'user' ? 'You' : 'AI'}</span>
                        <p>{message.text}</p>
                      </div>
                    ))
                  ) : (
                    <div className="empty-state">
                      <h4>Start the conversation</h4>
                      <p>Type a question below and press Send to query the uploaded content.</p>
                    </div>
                  )
                )}
              </div>

              <div className="chat-input-row">
                <textarea
                  className="form-input chat-input"
                  rows={2}
                  value={chatQuery}
                  onChange={(event) => setChatQuery(event.target.value)}
                  placeholder={pdfStatus.pdf_uploaded ? 'Ask a question about the uploaded document...' : 'Upload a document to begin chatting.'}
                  disabled={!pdfStatus.pdf_uploaded || isChatLoading}
                />
                <button
                  className="btn btn-primary"
                  onClick={handleSendChat}
                  disabled={!pdfStatus.pdf_uploaded || !chatQuery.trim() || isChatLoading}
                >
                  {isChatLoading ? 'Sending...' : 'Send Question'}
                </button>
              </div>

              {errorMessage && <div className="error-banner">{errorMessage}</div>}
            </div>
          )}

          {activeTab === 'analytics' && (
            <div className="analytics-panel">
              <div className="analytics-grid">
                <article className="analytics-card">
                  <h3>Document summary</h3>
                  <p>Capture structured insights from the loaded PDF once processing is complete.</p>
                </article>
                <article className="analytics-card">
                  <h3>Vector embeddings</h3>
                  <p>Track context nodes, retrieval readiness, and semantic coverage at a glance.</p>
                </article>
                <article className="analytics-card">
                  <h3>Performance</h3>
                  <p>Monitor indexing speed and backend readiness for large PDF workloads.</p>
                </article>
              </div>
            </div>
          )}

          {activeTab === 'tools' && (
            <div className="developer-tools">
              <div className="tool-card">
                <h3>Backend health</h3>
                <p>Server status is proxied through the API and updated automatically.</p>
              </div>
              <div className="tool-card">
                <h3>Session control</h3>
                <p>Clear conversations, retry uploads, and monitor file ingestion.
                </p>
              </div>
              <div className="tool-card">
                <h3>Developer notes</h3>
                <p>Use the built-in services to extend analysis capabilities or add custom NLP pipelines.</p>
              </div>
            </div>
          )}
        </section>
      </main>

      <div className="glow-blob blob-1" />
      <div className="glow-blob blob-2" />
    </div>
  )
}

export default App

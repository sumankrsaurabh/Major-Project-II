import { useState } from 'react'

function App() {
  const [files, setFiles] = useState([])
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [question, setQuestion] = useState('')
  const [answer, setAnswer] = useState(null)
  const [selectedIndex, setSelectedIndex] = useState(0)
  const [error, setError] = useState('')

  const handleFileChange = (event) => {
    setFiles(event.target.files)
  }

  const handleUpload = async () => {
    setError('')
    if (!files || files.length === 0) {
      setError('Please select one or more PDF files first.')
      return
    }

    const formData = new FormData()
    Array.from(files).forEach((file) => formData.append('files', file))

    setLoading(true)
    try {
      const response = await fetch('/api/upload', {
        method: 'POST',
        body: formData,
      })
      if (!response.ok) {
        throw new Error('Upload failed. Check backend logs.')
      }
      const data = await response.json()
      setResult(data)
      setSelectedIndex(0)
      setAnswer(null)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleAsk = async () => {
    setError('')
    if (!question.trim()) {
      setError('Please type a question to ask the PDF.')
      return
    }
    if (!result || !result.documents?.length) {
      setError('Please upload a PDF document before asking a question.')
      return
    }

    const documentText = result.documents[selectedIndex]?.text || ''
    setLoading(true)
    try {
      const response = await fetch('/api/qa', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question, document_text: documentText }),
      })
      if (!response.ok) {
        throw new Error('Question failed. Please try again.')
      }
      const data = await response.json()
      setAnswer(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const document = result?.documents?.[selectedIndex]

  return (
    <div className="app-shell">
      <header className="hero">
        <div>
          <p className="eyebrow">AI PDF Intelligence</p>
          <h1>Turn documents into answers, insights, and visuals.</h1>
          <p className="hero-copy">
            Upload PDFs, summarize content instantly, extract images and graphs, and ask targeted questions with a clean modern interface.
          </p>
        </div>

        <div className="hero-actions">
          <button onClick={handleUpload} disabled={loading}>
            {loading ? 'Processing documents...' : 'Start by uploading PDFs'}
          </button>
          <span className="hero-tag">Supports single or multiple PDFs</span>
        </div>
      </header>

      <section className="panel-grid">
        <article className="panel-card upload-card">
          <div className="panel-title">
            <h2>Upload PDFs</h2>
            <p>Choose one or more PDF files to analyze in a single workflow.</p>
          </div>
          <input type="file" accept="application/pdf" multiple onChange={handleFileChange} />
          <button className="action-button" onClick={handleUpload} disabled={loading}>
            {loading ? 'Uploading...' : 'Upload and Analyze'}
          </button>
          {error && <div className="error-banner">{error}</div>}
        </article>

        <article className="panel-card stats-card">
          <div className="panel-title">
            <h2>Capabilities</h2>
            <p>Professional-level insights built with NLP, computer vision, and document intelligence.</p>
          </div>
          <div className="stats-grid">
            <div className="stat-item">
              <strong>Summaries</strong>
              <span>Quick, concise document overviews</span>
            </div>
            <div className="stat-item">
              <strong>QA</strong>
              <span>Ask questions from any uploaded PDF</span>
            </div>
            <div className="stat-item">
              <strong>Image OCR</strong>
              <span>Extract text from charts, figures, and diagrams</span>
            </div>
            <div className="stat-item">
              <strong>Graph data</strong>
              <span>Keyword frequency analytics</span>
            </div>
          </div>
        </article>
      </section>

      {document && (
        <section className="results-shell">
          <aside className="sidebar-panel">
            <h3>Documents</h3>
            <div className="document-tabs">
              {result.documents.map((doc, index) => (
                <button
                  key={`${doc.name}-${index}`}
                  className={selectedIndex === index ? 'tab active' : 'tab'}
                  onClick={() => {
                    setSelectedIndex(index)
                    setAnswer(null)
                  }}
                >
                  {doc.name}
                </button>
              ))}
            </div>
          </aside>

          <main className="insights-panel">
            <div className="document-header">
              <div>
                <p className="section-label">Document summary</p>
                <h2>{document.name}</h2>
              </div>
              <p className="document-metadata">Loaded document {selectedIndex + 1} of {result.documents.length}</p>
            </div>

            <div className="summary-card">
              <h3>Summary</h3>
              <p>{document.summary}</p>
              <div className="chip-row">
                {document.key_phrases.map((phrase, idx) => (
                  <span key={idx} className="chip">{phrase}</span>
                ))}
              </div>
            </div>

            <div className="insight-grid">
              <article className="info-card">
                <h4>Key insights</h4>
                <ul>
                  {document.key_insights.map((insight, idx) => (
                    <li key={idx}>{insight}</li>
                  ))}
                </ul>
              </article>

              <article className="info-card section-card">
                <div className="section-card-header">
                  <h4>Top sections</h4>
                  <span>{document.sections.length} sections</span>
                </div>
                <div className="section-list">
                  {document.sections.map((section, idx) => (
                    <div key={idx} className="section-item">
                      <div className="section-item-top">
                        <strong>{section.title}</strong>
                        <span>{section.relevance.toFixed(2)}</span>
                      </div>
                      <p>{section.preview}</p>
                    </div>
                  ))}
                </div>
              </article>
            </div>

            <div className="image-grid modern">
              <h3>Extracted images</h3>
              {document.images.length > 0 ? (
                document.images.map((image, idx) => (
                  <div key={idx} className="image-card">
                    <img src={image.base64} alt={image.name} />
                    <div className="image-meta">
                      <span>{image.name}</span>
                      {image.ocr_text && <p>{image.ocr_text}</p>}
                    </div>
                  </div>
                ))
              ) : (
                <p className="empty-state">No images found in this document.</p>
              )}
            </div>

            <section className="qa-panel modern-qa">
              <div className="panel-title">
                <h3>Ask a question</h3>
                <p>Use the extracted text to query the document instantly.</p>
              </div>
              <textarea
                value={question}
                onChange={(event) => setQuestion(event.target.value)}
                placeholder="Ask about the uploaded PDF content..."
              />
              <button className="action-button" onClick={handleAsk} disabled={loading}>
                {loading ? 'Generating answer...' : 'Get Answer'}
              </button>
              {answer && (
                <div className="answer-box modern-answer">
                  <h4>Answer</h4>
                  <p>{answer.answer}</p>
                  <div className="answer-meta">
                    <strong>Source preview</strong>
                    <pre>{answer.source}</pre>
                  </div>
                  {answer.context && (
                    <details>
                      <summary>View evidence and context</summary>
                      <pre>{answer.context}</pre>
                    </details>
                  )}
                </div>
              )}
            </section>
          </main>
        </section>
      )}
    </div>
  )
}

export default App

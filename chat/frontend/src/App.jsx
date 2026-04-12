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

  return (
    <div className="app-shell">
      <header>
        <h1>Chat With Your PDF</h1>
        <p>Upload one or more PDFs to summarize, extract images, ask questions, and explore knowledge.</p>
      </header>

      <section className="upload-panel">
        <input type="file" accept="application/pdf" multiple onChange={handleFileChange} />
        <button onClick={handleUpload} disabled={loading}>
          {loading ? 'Processing...' : 'Upload PDFs'}
        </button>
        {error && <div className="error">{error}</div>}
      </section>

      {result && result.documents?.length > 0 && (
        <section className="results-panel">
          <div className="document-tabs">
            {result.documents.map((doc, index) => (
              <button
                key={doc.name + index}
                className={selectedIndex === index ? 'active' : ''}
                onClick={() => {
                  setSelectedIndex(index)
                  setAnswer(null)
                }}
              >
                {doc.name}
              </button>
            ))}
          </div>

          <div className="document-summary">
            <h2>{result.documents[selectedIndex].name}</h2>
            <div>
              <strong>Summary</strong>
              <p>{result.documents[selectedIndex].summary}</p>
            </div>
            <div>
              <strong>Key Insights</strong>
              <ul>
                {result.documents[selectedIndex].key_insights.map((insight, idx) => (
                  <li key={idx}>{insight}</li>
                ))}
              </ul>
            </div>

            <div className="graph-card">
              <strong>Graph Data</strong>
              <div className="graph-grid">
                {result.documents[selectedIndex].graph_data.labels.map((label, idx) => (
                  <div key={label} className="graph-bar-item">
                    <div className="bar" style={{ width: `${Math.min(result.documents[selectedIndex].graph_data.values[idx] * 10, 100)}%` }} />
                    <span>{label} ({result.documents[selectedIndex].graph_data.values[idx]})</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="image-grid">
              <strong>Extracted Images</strong>
              {result.documents[selectedIndex].images.length > 0 ? (
                result.documents[selectedIndex].images.map((image, idx) => (
                  <div key={idx} className="image-card">
                    <img src={image.base64} alt={image.name} />
                    <div>{image.name}</div>
                    {image.ocr_text && <pre className="ocr-text">{image.ocr_text}</pre>}
                  </div>
                ))
              ) : (
                <p>No images found in this document.</p>
              )}
            </div>
          </div>

          <div className="qa-panel">
            <h3>Ask a question about this PDF</h3>
            <textarea
              value={question}
              onChange={(event) => setQuestion(event.target.value)}
              placeholder="Ask about the uploaded PDF content..."
            />
            <button onClick={handleAsk} disabled={loading}>
              {loading ? 'Thinking...' : 'Ask Question'}
            </button>
            {answer && (
              <div className="answer-box">
                <h4>Answer</h4>
                <p>{answer.answer}</p>
                <small>Source: {answer.source}</small>
              </div>
            )}
          </div>
        </section>
      )}
    </div>
  )
}

export default App

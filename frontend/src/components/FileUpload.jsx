import { useState, useRef } from 'react';
import { 
  FileUp, 
  FileText, 
  CheckCircle, 
  AlertCircle, 
  ArrowRight,
  HardDrive,
  Cpu,
  Layers,
  RefreshCw
} from 'lucide-react';
import { pdfService } from '../services/api';

export default function FileUpload({ workspaceId, pdfStatus, setPdfStatus, onUploadSuccess }) {
  const [dragActive, setDragActive] = useState(false);
  const [uploadState, setUploadState] = useState('idle'); // idle, uploading, processing, success, error
  const [uploadProgress, setUploadProgress] = useState(0);
  const [errorMsg, setErrorMsg] = useState('');
  const [selectedFile, setSelectedFile] = useState(null);
  const fileInputRef = useRef(null);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const processFile = async (file) => {
    if (!file.name.toLowerCase().endsWith('.pdf')) {
      setErrorMsg('Invalid file format. Please upload a PDF file only.');
      setUploadState('error');
      return;
    }

    // The server publishes its configured limit through /status.
    const maxFileSizeMb = Number(pdfStatus?.max_file_size_mb) || 500;
    const limitBytes = maxFileSizeMb * 1024 * 1024;
    if (file.size > limitBytes) {
      setErrorMsg(`File size exceeds the ${maxFileSizeMb}MB limit.`);
      setUploadState('error');
      return;
    }

    setSelectedFile(file);
    setUploadState('uploading');
    setUploadProgress(0);
    setErrorMsg('');

    try {
      const response = await pdfService.uploadPDF(file, workspaceId, (progressEvent) => {
        const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
        setUploadProgress(percentCompleted);
        if (percentCompleted === 100) {
          setUploadState('processing');
        }
      });

      if (response && response.status === 'ready') {
        setUploadState('success');
        const updatedStatus = {
          pdf_uploaded: true,
          filename: response.filename,
          chunks: response.chunks,
          file_size_mb: response.file_size_mb,
          server_status: 'running',
          models_loaded: true
        };
        setPdfStatus(updatedStatus);
        if (onUploadSuccess) {
          onUploadSuccess(updatedStatus);
        }
      } else {
        throw new Error(response?.message || 'Processing failed');
      }
    } catch (error) {
      console.error(error);
      setErrorMsg(error.message || 'An error occurred during file upload or processing.');
      setUploadState('error');
    }
  };

  const handleDeleteDocument = async (documentId) => {\n    try {\n      const response = await pdfService.deleteDocument(workspaceId, documentId);\n      const documents = response.documents || [];\n      setPdfStatus((previous) => ({\n        ...previous,\n        documents,\n        pdf_uploaded: documents.length > 0,\n        filename: documents.at(-1)?.filename || 'No file uploaded',\n        chunks: documents.reduce((total, item) => total + item.chunks, 0),\n      }));\n    } catch (error) {\n      setErrorMsg(error.message || 'Unable to delete document.');\n      setUploadState('error');\n    }\n  };\n\n  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      processFile(e.dataTransfer.files[0]);
    }
  };

  const handleChange = (e) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      processFile(e.target.files[0]);
    }
  };

  const triggerFileInput = () => {
    fileInputRef.current.click();
  };

  return (
    <div className="upload-view animate-fade-in" style={{
      display: 'flex',
      flexDirection: 'column',
      gap: '2rem',
      maxWidth: '850px',
      margin: '0 auto',
      padding: '1rem 0'
    }}>
      {/* Title block */}
      <div style={{ textAlign: 'center', marginBottom: '1rem' }}>
        <h2 style={{ fontSize: '2.2rem', fontWeight: 800, marginBottom: '0.5rem', fontFamily: 'var(--font-heading)' }}>
          Analyze Your Documents with Local AI
        </h2>
        <p style={{ color: 'var(--text-secondary)', fontSize: '1.05rem', maxWidth: '600px', margin: '0 auto' }}>
          Upload PDF files to segment text, retrieve vector embeddings, run advanced semantic analysis, and chat directly with contents offline.
        </p>
      </div>

      <div style={{
        display: 'grid',
        gridTemplateColumns: pdfStatus?.pdf_uploaded ? '1.2fr 1fr' : '1fr',
        gap: '2rem',
        alignItems: 'stretch'
      }}>
        {/* Dragzone Panel */}
        <div 
          onDragEnter={handleDrag}
          onDragOver={handleDrag}
          onDragLeave={handleDrag}
          onDrop={handleDrop}
          className="glass-panel"
          style={{
            padding: '2.5rem',
            borderRadius: 'var(--radius-lg)',
            border: '2px dashed',
            borderColor: dragActive ? 'var(--primary)' : 'var(--border-light)',
            background: dragActive ? 'rgba(139, 92, 246, 0.05)' : 'var(--bg-surface)',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            textAlign: 'center',
            cursor: uploadState === 'uploading' || uploadState === 'processing' ? 'not-allowed' : 'pointer',
            transition: 'var(--transition)',
            minHeight: '320px',
            position: 'relative'
          }}
          onClick={uploadState !== 'uploading' && uploadState !== 'processing' ? triggerFileInput : undefined}
        >
          <input 
            type="file" 
            ref={fileInputRef} 
            onChange={handleChange} 
            accept=".pdf" 
            style={{ display: 'none' }} 
          />

          {uploadState === 'idle' && (
            <>
              <div style={{
                background: 'rgba(255, 255, 255, 0.03)',
                width: '70px',
                height: '70px',
                borderRadius: '50%',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                marginBottom: '1.5rem',
                border: '1px solid var(--border-light)',
                boxShadow: 'var(--shadow-sm)'
              }}>
                <FileUp size={32} color="var(--primary)" />
              </div>
              <h3 style={{ fontSize: '1.25rem', fontWeight: 600, marginBottom: '0.5rem' }}>Drag & Drop PDF Here</h3>
              <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', marginBottom: '1.5rem' }}>
                or click to browse files (limit {Number(pdfStatus?.max_file_size_mb) || 500}MB)
              </p>
              <div style={{
                fontSize: '0.75rem',
                color: 'var(--text-muted)',
                background: 'rgba(0,0,0,0.2)',
                padding: '0.4rem 0.8rem',
                borderRadius: '20px',
                border: '1px solid var(--border-light)'
              }}>
                Only PDF documents supported
              </div>
            </>
          )}

          {uploadState === 'uploading' && (
            <div style={{ width: '100%' }}>
              <RefreshCw className="pulse-indicator" size={32} color="var(--primary)" style={{ animation: 'spin 2s linear infinite', marginBottom: '1.5rem' }} />
              <h3 style={{ fontSize: '1.15rem', fontWeight: 600, marginBottom: '0.5rem' }}>Uploading File...</h3>
              <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', marginBottom: '1.5rem' }}>
                {selectedFile?.name} ({Math.round(selectedFile?.size / (1024 * 1024) * 100) / 100} MB)
              </p>
              <div style={{
                width: '100%',
                height: '6px',
                backgroundColor: 'rgba(255, 255, 255, 0.05)',
                borderRadius: '3px',
                overflow: 'hidden',
                marginBottom: '0.5rem'
              }}>
                <div style={{
                  width: `${uploadProgress}%`,
                  height: '100%',
                  background: 'linear-gradient(90deg, var(--primary) 0%, var(--secondary) 100%)',
                  borderRadius: '3px',
                  transition: 'width 0.2s ease-out'
                }} />
              </div>
              <span style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--secondary)' }}>{uploadProgress}%</span>
            </div>
          )}

          {uploadState === 'processing' && (
            <div>
              <div className="pulse-indicator" style={{
                width: '60px',
                height: '60px',
                borderRadius: '50%',
                background: 'rgba(6, 182, 212, 0.1)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                margin: '0 auto 1.5rem'
              }}>
                <Cpu size={28} className="spin" style={{ animation: 'spin 4s linear infinite', color: 'var(--secondary)' }} />
              </div>
              <h3 style={{ fontSize: '1.15rem', fontWeight: 600, marginBottom: '0.5rem' }}>Segmenting & Build Index...</h3>
              <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
                Extracting PDF text layers and constructing localized vector embeddings. This may take up to a minute for large files...
              </p>
            </div>
          )}

          {uploadState === 'success' && (
            <div>
              <div style={{
                width: '60px',
                height: '60px',
                borderRadius: '50%',
                background: 'rgba(16, 185, 129, 0.1)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                margin: '0 auto 1.5rem',
                border: '1px solid rgba(16, 185, 129, 0.2)'
              }}>
                <CheckCircle size={30} color="var(--success)" />
              </div>
              <h3 style={{ fontSize: '1.25rem', fontWeight: 600, color: 'var(--success)', marginBottom: '0.5rem' }}>Processing Complete</h3>
              <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', marginBottom: '1.5rem', maxWidth: '300px', margin: '0 auto 1.5rem' }}>
                {selectedFile?.name} has been processed successfully.
              </p>
              <button 
                onClick={(e) => {
                  e.stopPropagation();
                  onUploadSuccess && onUploadSuccess();
                }}
                className="btn btn-primary"
              >
                Go to Chat <ArrowRight size={16} />
              </button>
            </div>
          )}

          {uploadState === 'error' && (
            <div>
              <div style={{
                width: '60px',
                height: '60px',
                borderRadius: '50%',
                background: 'rgba(239, 68, 68, 0.1)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                margin: '0 auto 1.5rem',
                border: '1px solid rgba(239, 68, 68, 0.2)'
              }}>
                <AlertCircle size={30} color="var(--danger)" />
              </div>
              <h3 style={{ fontSize: '1.15rem', fontWeight: 600, color: 'var(--danger)', marginBottom: '0.5rem' }}>Upload Failed</h3>
              <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', marginBottom: '1.5rem', padding: '0 1.5rem' }}>
                {errorMsg}
              </p>
              <button 
                onClick={(e) => {
                  e.stopPropagation();
                  setUploadState('idle');
                }}
                className="btn btn-secondary"
                style={{ fontSize: '0.8rem', padding: '0.5rem 1rem' }}
              >
                Try Again
              </button>
            </div>
          )}
        </div>

        {/* Existing file metadata card */}
        {pdfStatus?.pdf_uploaded && (
          <div className="glass-panel animate-fade-in" style={{
            padding: '2rem',
            display: 'flex',
            flexDirection: 'column',
            gap: '1.5rem',
            borderRadius: 'var(--radius-lg)'
          }}>
            <h3 style={{ fontSize: '1.25rem', fontWeight: 600, borderBottom: '1px solid var(--border-light)', paddingBottom: '0.75rem' }}>
              Active Document Context
            </h3>

            <div style={{ display: 'flex', alignItems: 'flex-start', gap: '1rem' }}>
              <div style={{
                background: 'rgba(255, 255, 255, 0.03)',
                padding: '0.75rem',
                borderRadius: 'var(--radius-md)',
                border: '1px solid var(--border-light)'
              }}>
                <FileText size={32} color="var(--primary)" />
              </div>
              <div style={{ overflow: 'hidden' }}>
                <h4 style={{
                  fontSize: '0.95rem',
                  fontWeight: 600,
                  whiteSpace: 'nowrap',
                  textOverflow: 'ellipsis',
                  overflow: 'hidden'
                }}>
                  {pdfStatus.filename}
                </h4>
                <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Status: Active RAG Index</span>
              </div>
            </div>

            <div style={{
              display: 'grid',
              gridTemplateColumns: '1fr 1fr',
              gap: '1rem',
              marginTop: '0.5rem'
            }}>
              <div className="glass-card" style={{ padding: '1rem' }}>
                <span style={{ fontSize: '0.7rem', color: 'var(--text-secondary)', textTransform: 'uppercase', display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                  <HardDrive size={12} /> File Size
                </span>
                <div style={{ fontSize: '1.3rem', fontWeight: 700, marginTop: '0.25rem', color: 'var(--secondary)' }}>
                  {pdfStatus.file_size_mb} <span style={{ fontSize: '0.8rem' }}>MB</span>
                </div>
              </div>

              <div className="glass-card" style={{ padding: '1rem' }}>
                <span style={{ fontSize: '0.7rem', color: 'var(--text-secondary)', textTransform: 'uppercase', display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                  <Layers size={12} /> Context Chunks
                </span>
                <div style={{ fontSize: '1.3rem', fontWeight: 700, marginTop: '0.25rem', color: 'var(--primary)' }}>
                  {pdfStatus.chunks} <span style={{ fontSize: '0.8rem' }}>nodes</span>
                </div>
              </div>
            </div>

            <div style={{
              marginTop: 'auto',
              background: 'rgba(16, 185, 129, 0.05)',
              border: '1px solid rgba(16, 185, 129, 0.15)',
              borderRadius: 'var(--radius-md)',
              padding: '0.85rem',
              fontSize: '0.8rem',
              color: 'var(--success)',
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem'
            }}>
              <CheckCircle size={16} />
              <span>Vectors loaded successfully. Chat and Analytics are enabled.</span>
            </div>
          </div>
        )}
      </div>
      
      {/* CSS Spin style insertion (if not present) */}
      <style>{`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
        .spin {
          animation: spin 1s linear infinite;
        }
      `}</style>
    </div>
  );
}

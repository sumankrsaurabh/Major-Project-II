import { useState, useRef } from 'react';
import { Upload, CheckCircle, AlertCircle, Loader2, X } from 'lucide-react';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const MAX_RETRIES = 3;
const RETRY_DELAY = 1000;

export default function FileUpload({ onUploadSuccess }) {
  const [file, setFile] = useState(null);
  const [status, setStatus] = useState('idle');
  const [errorMsg, setErrorMsg] = useState('');
  const [progress, setProgress] = useState(0);
  const [retryCount, setRetryCount] = useState(0);
  const fileInputRef = useRef(null);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (!selectedFile) return;

    if (selectedFile.type !== 'application/pdf') {
      setFile(null);
      setStatus('error');
      setErrorMsg('Please select a PDF file.');
      return;
    }

    if (selectedFile.size > 50 * 1024 * 1024) {
      setFile(null);
      setStatus('error');
      setErrorMsg('File is too large (max 50MB).');
      return;
    }

    setFile(selectedFile);
    setStatus('idle');
    setErrorMsg('');
    setRetryCount(0);
  };

  const uploadWithRetry = async (attempt = 0) => {
    if (!file) return;

    setStatus('uploading');
    setProgress(Math.min(attempt * 30, 90));

    const formData = new FormData();
    formData.append('file', file);

    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 120000);

      const response = await fetch(`${API_URL}/upload`, {
        method: 'POST',
        body: formData,
        signal: controller.signal,
      });

      clearTimeout(timeoutId);
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || `Upload failed: ${response.status}`);
      }

      setProgress(100);
      setStatus('success');
      const fileName = file.name;
      setFile(null);
      setRetryCount(0);

      setTimeout(() => {
        onUploadSuccess(fileName);
      }, 1500);

      setTimeout(() => {
        setStatus('idle');
        setProgress(0);
      }, 3000);

    } catch (err) {
      console.error(`Upload attempt ${attempt + 1} failed:`, err);

      if (err.name === 'AbortError') {
        setErrorMsg('Upload timeout. Please try again.');
        setStatus('error');
      } else if (attempt < MAX_RETRIES - 1) {
        setRetryCount(attempt + 1);
        setErrorMsg(`Retrying... (${attempt + 1}/${MAX_RETRIES})`);
        await new Promise(resolve => setTimeout(resolve, RETRY_DELAY * (attempt + 1)));
        return uploadWithRetry(attempt + 1);
      } else {
        setStatus('error');
        setErrorMsg(err.message || 'Upload failed. Please try again.');
        setRetryCount(0);
      }
    }
  };

  const handleUpload = async () => {
    await uploadWithRetry(0);
  };

  const handleReset = () => {
    setFile(null);
    setStatus('idle');
    setErrorMsg('');
    setProgress(0);
    setRetryCount(0);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div className="w-full space-y-6">
      {/* Upload Area */}
      <div
        onClick={() => fileInputRef.current?.click()}
        className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center cursor-pointer hover:border-blue-400 hover:bg-blue-50 transition-all"
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf"
          className="hidden"
          onChange={handleFileChange}
        />

        <div className="flex justify-center mb-4">
          {status === 'success' ? (
            <CheckCircle className="w-12 h-12 text-green-600" />
          ) : status === 'error' ? (
            <AlertCircle className="w-12 h-12 text-red-600" />
          ) : status === 'uploading' ? (
            <Loader2 className="w-12 h-12 text-blue-600 animate-spin" />
          ) : (
            <Upload className="w-12 h-12 text-gray-400" />
          )}
        </div>

        <h3 className="font-semibold text-gray-900 mb-1">
          {status === 'success' ? 'All set!' : file ? file.name : 'Upload your PDF'}
        </h3>

        <p className="text-sm text-gray-600">
          {status === 'uploading' 
            ? 'Processing your document...' 
            : status === 'success' 
            ? 'Ready to chat!' 
            : 'Drag and drop your PDF here, or click to browse'}
        </p>

        {status === 'uploading' && (
          <div className="mt-4">
            <div className="h-1.5 bg-gray-200 rounded-full overflow-hidden">
              <div
                className="h-full bg-blue-600 transition-all duration-300"
                style={{ width: `${progress}%` }}
              />
            </div>
            <p className="text-xs text-gray-500 mt-2">{progress}%</p>
          </div>
        )}
      </div>

      {/* Error Message */}
      {status === 'error' && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-sm text-red-700">{errorMsg}</p>
        </div>
      )}

      {/* File Info */}
      {file && status === 'idle' && (
        <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <p className="text-sm text-gray-900">
            <span className="font-medium">{file.name}</span>
            <span className="text-gray-600"> • {(file.size / 1024 / 1024).toFixed(2)} MB</span>
          </p>
        </div>
      )}

      {/* Action Buttons */}
      <div className="flex gap-2">
        {file && status === 'idle' && (
          <>
            <button
              onClick={handleUpload}
              className="flex-1 px-4 py-2.5 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-colors"
            >
              Process Document
            </button>
            <button
              onClick={handleReset}
              className="px-4 py-2.5 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
            >
              Clear
            </button>
          </>
        )}

        {!file && status === 'idle' && (
          <button
            onClick={() => fileInputRef.current?.click()}
            className="w-full px-4 py-2.5 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-colors"
          >
            Select PDF
          </button>
        )}

        {status === 'error' && retryCount < MAX_RETRIES && (
          <button
            onClick={handleUpload}
            className="w-full px-4 py-2.5 bg-orange-600 text-white font-medium rounded-lg hover:bg-orange-700 transition-colors"
          >
            Retry ({retryCount}/{MAX_RETRIES})
          </button>
        )}
      </div>

      {/* Info */}
      <p className="text-xs text-gray-500 text-center">Maximum file size: 50MB • PDF format only</p>
    </div>
  );
}

import React, { useState, useRef } from 'react';
import { uploadPDF } from '../services/api';
import './FileUpload.css';

function FileUpload({ onUploadSuccess }) {
  const [isDragging, setIsDragging] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadStatus, setUploadStatus] = useState(''); // idle, validating, uploading, processing, success
  const fileInputRef = useRef(null);

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    const files = e.dataTransfer.files;
    if (files.length > 0) {
      handleFileUpload(files[0]);
    }
  };

  const handleFileChange = (e) => {
    const files = e.target.files;
    if (files.length > 0) {
      handleFileUpload(files[0]);
    }
  };

  const handleFileUpload = async (file) => {
    setError('');
    setUploadProgress(0);
    setUploadStatus('validating');

    // Validate file
    if (!file.name.toLowerCase().endsWith('.pdf')) {
      setError('❌ Please upload a PDF file. Other formats are not supported.');
      setUploadStatus('idle');
      return;
    }

    const fileSizeMB = file.size / (1024 * 1024);
    if (fileSizeMB > 500) {
      setError(`❌ File is ${fileSizeMB.toFixed(1)}MB. Maximum file size is 500MB.`);
      setUploadStatus('idle');
      return;
    }

    setIsLoading(true);
    setUploadStatus('uploading');

    try {
      // Simulate progress
      const progressInterval = setInterval(() => {
        setUploadProgress((prev) => {
          if (prev >= 80) {
            clearInterval(progressInterval);
            return prev;
          }
          return prev + Math.random() * 30;
        });
      }, 500);

      setUploadStatus('processing');
      const result = await uploadPDF(file);

      clearInterval(progressInterval);
      setUploadProgress(100);
      setUploadStatus('success');

      setTimeout(() => {
        onUploadSuccess(file.name);
      }, 800);
    } catch (err) {
      setError(`❌ ${err.message || 'Upload failed. Please try again.'}`);
      setUploadProgress(0);
      setUploadStatus('idle');
    } finally {
      setIsLoading(false);
    }
  };

  const handleClickUpload = () => {
    fileInputRef.current?.click();
  };

  const getStatusMessage = () => {
    switch (uploadStatus) {
      case 'validating':
        return '🔍 Validating PDF...';
      case 'uploading':
        return '📤 Uploading...';
      case 'processing':
        return '⚙️ Processing PDF...';
      case 'success':
        return '✅ Upload complete!';
      default:
        return '';
    }
  };

  return (
    <div className="file-upload-container">
      <div
        className={`upload-area ${isDragging ? 'dragging' : ''} ${isLoading ? 'loading' : ''}`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={!isLoading ? handleClickUpload : undefined}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf"
          onChange={handleFileChange}
          disabled={isLoading}
          style={{ display: 'none' }}
        />

        {!isLoading && (
          <>
            <div className="upload-icon">📋</div>
            <h2>Upload Your PDF</h2>
            <p className="upload-text">
              Drag and drop your PDF here, or click to browse
            </p>
            <p className="upload-hint">Maximum file size: 500MB • PDF format only</p>
            <button
              className="upload-btn"
              type="button"
              disabled={isLoading}
              onClick={handleClickUpload}
            >
              📁 Choose PDF
            </button>
          </>
        )}

        {isLoading && (
          <div className="loading-state">
            <div className="spinner"></div>
            <p className="status-message">{getStatusMessage()}</p>
            <div className="progress-bar">
              <div
                className="progress-fill"
                style={{ width: `${uploadProgress}%` }}
              ></div>
            </div>
            <p className="progress-text">{Math.round(uploadProgress)}%</p>
          </div>
        )}
      </div>

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      <div className="upload-features">
        <h3>✨ Features</h3>
        <ul>
          <li>🚀 Fast PDF processing with AI</li>
          <li>💬 Ask questions about your documents</li>
          <li>🧠 Intelligent context understanding</li>
          <li>📊 Confidence scoring on answers</li>
          <li>💾 Session-based conversation history</li>
        </ul>
      </div>
    </div>
  );
}

export default FileUpload;

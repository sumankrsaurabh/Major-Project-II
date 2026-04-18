import React, { useState, useRef } from 'react';
import { uploadPDF } from '../services/api';
import './FileUpload.css';

function FileUpload({ onUploadSuccess }) {
  const [isDragging, setIsDragging] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [uploadProgress, setUploadProgress] = useState(0);
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

    // Validate file
    if (!file.name.toLowerCase().endsWith('.pdf')) {
      setError('Please upload a PDF file');
      return;
    }

    if (file.size > 50 * 1024 * 1024) {
      setError('File size must be less than 50MB');
      return;
    }

    setIsLoading(true);
    try {
      // Simulate progress
      const progressInterval = setInterval(() => {
        setUploadProgress((prev) => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return prev;
          }
          return prev + Math.random() * 30;
        });
      }, 500);

      const result = await uploadPDF(file);

      clearInterval(progressInterval);
      setUploadProgress(100);

      setTimeout(() => {
        onUploadSuccess(file.name);
      }, 500);
    } catch (err) {
      setError(err.message || 'Upload failed. Please try again.');
      setUploadProgress(0);
    } finally {
      setIsLoading(false);
    }
  };

  const handleClickUpload = () => {
    fileInputRef.current?.click();
  };

  return (
    <div className="file-upload-container">
      <div
        className={`upload-area ${isDragging ? 'dragging' : ''} ${isLoading ? 'loading' : ''}`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={handleClickUpload}
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
            <p className="upload-hint">Maximum file size: 50MB</p>
            <button
              className="upload-btn"
              type="button"
              disabled={isLoading}
            >
              Choose PDF
            </button>
          </>
        )}

        {isLoading && (
          <div className="loading-state">
            <div className="spinner"></div>
            <p>Processing PDF...</p>
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
          <span className="error-icon">⚠️</span>
          {error}
        </div>
      )}
    </div>
  );
}

export default FileUpload;

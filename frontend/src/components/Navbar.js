import React from 'react';
import './Navbar.css';

function Navbar({ pdfUploaded, uploadedFileName, onReset }) {
  return (
    <header className="mui-app-bar mui-paper mui-elevation-4">
      <div className="mui-toolbar">
        <h1 className="mui-h6 mui-app-bar-title">Chat with PDF</h1>
        {pdfUploaded && (
          <div className="mui-app-bar-actions">
            <span className="mui-body2 mui-file-chip">
              {uploadedFileName}
            </span>
            <button 
              className="mui-button mui-button-outlined mui-button-small" 
              onClick={onReset}
            >
              NEW UPLOAD
            </button>
          </div>
        )}
      </div>
    </header>
  );
}

export default Navbar;

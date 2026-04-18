import React from 'react';
import './LoadingAnimation.css';

function LoadingAnimation({ status, message }) {
  return (
    <div className="loading-animation">
      <div className="mui-circular-progress" role="progressbar" style={{ width: 40, height: 40 }}>
        <svg className="mui-circular-progress-svg" viewBox="22 22 44 44">
          <circle 
            className="mui-circular-progress-circle" 
            cx="44" 
            cy="44" 
            r="20.2" 
            fill="none" 
            strokeWidth="3.6" 
          />
        </svg>
      </div>
      <p className="loading-text">{message || 'Loading...'}</p>
    </div>
  );
}

export default LoadingAnimation;

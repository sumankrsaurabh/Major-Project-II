import React from 'react';
import './RightPanel.css';
import ConversationStats from './ConversationStats';

function RightPanel({ currentMessage, stats }) {
  if (!currentMessage) return null;

  return (
    <aside className="mui-right-panel mui-paper">
      <div className="mui-panel-header">
        <h2 className="mui-h6">Analysis Details</h2>
      </div>

      <div className="mui-panel-content">
        <div className="mui-card mui-paper-outlined">
          <h3 className="mui-subtitle2">Confidence Score</h3>
          <div className="mui-confidence-meter">
            <div 
              className="mui-confidence-fill" 
              style={{ 
                width: `${currentMessage.confidence * 100}%`,
                backgroundColor: currentMessage.confidence > 0.8 ? 'var(--mui-success-main)' :
                                 currentMessage.confidence > 0.5 ? 'var(--mui-warning-main)' : 'var(--mui-error-main)'
              }}
            />
          </div>
          <p className="mui-body2">{(currentMessage.confidence * 100).toFixed(1)}% Certainty</p>
        </div>

        <div className="mui-card mui-paper-outlined">
          <h3 className="mui-subtitle2">Sources Found</h3>
          <div className="mui-sources-list">
            {currentMessage.source_documents?.map((doc, idx) => (
              <div key={idx} className="mui-source-item">
                <span className="mui-source-icon">📄</span>
                <div className="mui-source-text">
                  <span className="mui-body2">Page {doc.metadata.page}</span>
                </div>
              </div>
            ))}
            {(!currentMessage.source_documents || currentMessage.source_documents.length === 0) && (
              <p className="mui-body2" style={{ color: 'var(--mui-text-secondary)' }}>No specific sources cited.</p>
            )}
          </div>
        </div>

        {stats && (
          <div className="mui-card mui-paper-outlined">
             <ConversationStats stats={stats} />
          </div>
        )}
      </div>
    </aside>
  );
}

export default RightPanel;

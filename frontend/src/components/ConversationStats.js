import React from 'react';
import './ConversationStats.css';

function ConversationStats({ stats }) {
  if (!stats) return null;

  return (
    <div className="mui-stats-container">
      <h3 className="mui-subtitle2">Session Stats</h3>
      
      <div className="mui-stats-grid">
        <div className="mui-stat-item">
          <span className="mui-stat-value">{stats.total || 0}</span>
          <span className="mui-stat-label">Queries</span>
        </div>
        
        <div className="mui-stat-item">
          <span className="mui-stat-value">
            {stats.avgConfidence ? `${(stats.avgConfidence * 100).toFixed(0)}%` : '0%'}
          </span>
          <span className="mui-stat-label">Avg Conf</span>
        </div>
        
        <div className="mui-stat-item">
          <span className="mui-stat-value">{stats.activeTime || '0s'}</span>
          <span className="mui-stat-label">Time</span>
        </div>
      </div>
    </div>
  );
}

export default ConversationStats;

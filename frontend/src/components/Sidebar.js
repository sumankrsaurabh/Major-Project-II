import React from 'react';
import './Sidebar.css';

function Sidebar({ sessionId }) {
  if (!sessionId) return null;

  return (
    <nav className="mui-drawer mui-paper">
      <div className="mui-drawer-header">
        <h2 className="mui-h6">Chat History</h2>
      </div>
      
      <div className="mui-list">
        <div className="mui-list-item mui-list-item-active">
          <div className="mui-list-item-icon">💬</div>
          <div className="mui-list-item-text">
            <span>Current Session</span>
            <span className="mui-body2">{sessionId}</span>
          </div>
        </div>
      </div>
      
      <div className="mui-drawer-footer">
        <p className="mui-body2">All conversations are temporarily stored in memory.</p>
      </div>
    </nav>
  );
}

export default Sidebar;

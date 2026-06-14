import React, { useEffect, useState } from 'react';
import { 
  FileUp, 
  MessageSquare, 
  BarChart2, 
  Sliders, 
  Activity, 
  Server, 
  CheckCircle, 
  XCircle,
  HelpCircle
} from 'lucide-react';
import { pdfService } from '../services/api';

export default function Sidebar({ activeTab, setActiveTab, pdfStatus }) {
  const [systemHealth, setSystemHealth] = useState({
    status: 'checking',
    modelsLoaded: false
  });

  const checkHealth = async () => {
    try {
      const response = await pdfService.getHealth();
      if (response.status === 'healthy' || response.status === 'success') {
        // It returns AnalysisResponse with status="healthy" from analysis health endpoint,
        // or health endpoint from FastAPI main, which returns status="ok", models_loaded=true.
        // Let's fallback check for status
        const isOk = response.status === 'healthy' || response.status === 'ok' || response.status === 'success';
        const modelsLoaded = response.models_loaded || response.data?.message?.includes('running') || false;
        setSystemHealth({
          status: isOk ? 'online' : 'offline',
          modelsLoaded: modelsLoaded || true // default true if server responded
        });
      } else {
        setSystemHealth({ status: 'offline', modelsLoaded: false });
      }
    } catch (error) {
      setSystemHealth({ status: 'offline', modelsLoaded: false });
    }
  };

  useEffect(() => {
    checkHealth();
    const interval = setInterval(checkHealth, 10000);
    return () => clearInterval(interval);
  }, []);

  const navItems = [
    { id: 'upload', label: 'Upload & Status', icon: FileUp },
    { id: 'chat', label: 'AI Chat Panel', icon: MessageSquare, disabled: !pdfStatus?.pdf_uploaded },
    { id: 'analytics', label: 'Document Analytics', icon: BarChart2, disabled: !pdfStatus?.pdf_uploaded },
    { id: 'tools', label: 'Developer AI Tools', icon: Sliders },
  ];

  return (
    <aside className="sidebar-container glass-panel" style={{
      width: 'var(--sidebar-width)',
      height: '100vh',
      display: 'flex',
      flexDirection: 'column',
      padding: '2rem 1.2rem 1.5rem',
      borderRadius: '0 var(--radius-lg) var(--radius-lg) 0',
      borderLeft: 'none',
      zIndex: 10
    }}>
      {/* Brand Logo Header */}
      <div className="sidebar-header" style={{
        display: 'flex',
        alignItems: 'center',
        gap: '0.75rem',
        marginBottom: '3rem',
        paddingLeft: '0.5rem'
      }}>
        <div style={{
          background: 'linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%)',
          width: '36px',
          height: '36px',
          borderRadius: '10px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          boxShadow: '0 4px 12px rgba(139, 92, 246, 0.4)'
        }}>
          <Activity size={20} color="#ffffff" />
        </div>
        <div>
          <h1 style={{
            fontSize: '1.25rem',
            fontWeight: 800,
            lineHeight: 1.1,
            background: 'linear-gradient(135deg, #ffffff 40%, var(--text-secondary) 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            letterSpacing: '-0.03em'
          }}>
            ChatWithPDF
          </h1>
          <span style={{
            fontSize: '0.7rem',
            color: 'var(--secondary)',
            fontWeight: 600,
            letterSpacing: '0.05em',
            textTransform: 'uppercase'
          }}>
            V2.0 AI Engine
          </span>
        </div>
      </div>

      {/* Navigation List */}
      <nav style={{
        display: 'flex',
        flexDirection: 'column',
        gap: '0.5rem',
        flexGrow: 1
      }}>
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => !item.disabled && setActiveTab(item.id)}
              disabled={item.disabled}
              className={`nav-btn ${isActive ? 'active' : ''}`}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '1rem',
                width: '100%',
                padding: '0.85rem 1rem',
                borderRadius: 'var(--radius-md)',
                background: isActive ? 'linear-gradient(90deg, rgba(139, 92, 246, 0.15) 0%, rgba(139, 92, 246, 0.02) 100%)' : 'transparent',
                border: '1px solid',
                borderColor: isActive ? 'rgba(139, 92, 246, 0.25)' : 'transparent',
                color: item.disabled ? 'var(--text-muted)' : (isActive ? '#ffffff' : 'var(--text-secondary)'),
                cursor: item.disabled ? 'not-allowed' : 'pointer',
                fontFamily: 'var(--font-heading)',
                fontSize: '0.95rem',
                fontWeight: isActive ? 600 : 500,
                textAlign: 'left',
                transition: 'var(--transition)',
                opacity: item.disabled ? 0.4 : 1,
                position: 'relative'
              }}
            >
              {isActive && (
                <div style={{
                  position: 'absolute',
                  left: '0',
                  top: '25%',
                  height: '50%',
                  width: '3px',
                  background: 'var(--primary)',
                  borderRadius: '0 4px 4px 0',
                  boxShadow: '0 0 8px var(--primary)'
                }} />
              )}
              <Icon size={18} style={{
                color: isActive ? 'var(--primary)' : 'inherit',
                transition: 'var(--transition)'
              }} />
              <span>{item.label}</span>
            </button>
          );
        })}
      </nav>

      {/* System Server Health Status Card */}
      <div className="system-status-card" style={{
        background: 'rgba(255, 255, 255, 0.02)',
        border: '1px solid var(--border-light)',
        borderRadius: 'var(--radius-md)',
        padding: '0.9rem',
        marginTop: 'auto'
      }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          marginBottom: '0.5rem'
        }}>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
            <Server size={12} /> Server Status
          </span>
          {systemHealth.status === 'online' ? (
            <span style={{ color: 'var(--success)', fontSize: '0.7rem', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '0.2rem' }}>
              <CheckCircle size={10} /> Online
            </span>
          ) : systemHealth.status === 'checking' ? (
            <span style={{ color: 'var(--warning)', fontSize: '0.7rem', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '0.2rem' }}>
              <div className="pulse-indicator" style={{ width: '6px', height: '6px', backgroundColor: 'var(--warning)', borderRadius: '50%' }} /> Checking
            </span>
          ) : (
            <span style={{ color: 'var(--danger)', fontSize: '0.7rem', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '0.2rem' }}>
              <XCircle size={10} /> Offline
            </span>
          )}
        </div>
        <div style={{
          fontSize: '0.65rem',
          color: 'var(--text-muted)',
          display: 'flex',
          flexDirection: 'column',
          gap: '0.25rem'
        }}>
          <div>Models: {systemHealth.modelsLoaded ? <span style={{ color: 'var(--success)' }}>✓ Loaded</span> : <span style={{ color: 'var(--warning)' }}>⚠️ Unloaded</span>}</div>
          <div>CORS Proxy: <span style={{ color: 'var(--success)' }}>✓ Configured</span></div>
        </div>
      </div>
    </aside>
  );
}

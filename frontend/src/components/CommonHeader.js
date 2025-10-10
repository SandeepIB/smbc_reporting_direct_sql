import React from 'react';
import { useNavigate } from 'react-router-dom';
import './CommonHeader.css';

const CommonHeader = ({ title, showBackButton = true }) => {
  const navigate = useNavigate();

  return (
    <header className="common-header" style={{background: '#2c5530', color: 'white', padding: '1rem 2rem', boxShadow: '0 2px 10px rgba(0,0,0,0.1)'}}>
      <div className="header-content" style={{display: 'flex', alignItems: 'center', justifyContent: 'space-between', maxWidth: '1200px', margin: '0 auto'}}>
        <div className="header-left" style={{display: 'flex', alignItems: 'center', gap: '1rem'}}>
          {showBackButton && (
            <button 
              onClick={() => navigate('/')} 
              className="back-btn"
              style={{background: '#004d26', color: 'white', border: 'none', padding: '8px 16px', borderRadius: '20px', fontSize: '14px', cursor: 'pointer', fontWeight: '500'}}
              title="Back to Home"
            >
              ← Back
            </button>
          )}
          <div className="logo" onClick={() => navigate('/')} style={{cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '0.5rem'}}>
            <div className="logo-icon" style={{fontSize: '1.5rem'}}>🔍</div>
            <img src="/logo.JPG" alt="SMBC Logo" className="logo-image" style={{height: '40px', width: 'auto'}} />
          </div>
        </div>
        <h1 className="header-title" style={{margin: 0, fontSize: '1.8rem', fontWeight: 600, textAlign: 'center', flex: 1}}>{title}</h1>
        <div className="header-right" style={{width: '120px'}}></div>
      </div>
    </header>
  );
};

export default CommonHeader;
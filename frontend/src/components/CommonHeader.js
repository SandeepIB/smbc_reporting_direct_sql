import React from 'react';
import { useNavigate } from 'react-router-dom';
import './CommonHeader.css';

const CommonHeader = ({ title }) => {
  const navigate = useNavigate();

  return (
    <div className="common-header">
      <div className="header-left">
        <img 
          src="/logo.JPG" 
          alt="SMBC Logo" 
          className="header-logo" 
          onClick={() => navigate('/')}
        />
      </div>
      <h1 className="header-title">{title}</h1>
      <div className="header-right">
        <button className="back-button" onClick={() => navigate('/')}>
          ← Back
        </button>
      </div>
    </div>
  );
};

export default CommonHeader;
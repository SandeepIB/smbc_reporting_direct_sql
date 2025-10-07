import React from 'react';
import './LandingPage.css';

const LandingPage = ({ onOpenChat }) => {
  return (
    <div className="landing-page">
      <nav className="navbar">
        <div className="navbar-brand">SMBC</div>
        <div className="navbar-nav">
          <a href="#">Analytics Tools</a>
          <a href="#">Business Support Tools</a>
          <a href="#">Reporting Dashboard</a>
          <a href="#">Data Insights</a>
        </div>
      </nav>

      <div className="container-box">
        <h2 className="page-title">Prompts to Insights</h2>
        <p className="page-subtitle">Transform your natural language questions into actionable business insights</p>
        
        <div className="features-grid">
          <div className="feature-card">
            <div className="feature-icon">🔍</div>
            <h3>Natural Language Queries</h3>
            <p>Ask questions in plain English and get instant SQL-powered insights</p>
          </div>
          
          <div className="feature-card">
            <div className="feature-icon">📊</div>
            <h3>Real-time Analytics</h3>
            <p>Connect to your database and get live data analysis</p>
          </div>
          
          <div className="feature-card">
            <div className="feature-icon">📈</div>
            <h3>Executive Reports</h3>
            <p>Generate professional reports with charts and insights</p>
          </div>
        </div>

        <div className="cta-section">
          <h3>Ready to get started?</h3>
          <p>Click the chat button below to begin asking questions about your data</p>
        </div>
      </div>

      <button className="chatbot-btn" onClick={onOpenChat} title="Open Chat">
        💬
      </button>
    </div>
  );
};

export default LandingPage;
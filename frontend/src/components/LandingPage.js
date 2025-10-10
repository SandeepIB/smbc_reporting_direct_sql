import React, { useState, useEffect } from 'react';
import './LandingPage.css';

const LandingPage = ({ onOpenChat, onOpenAdmin }) => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [activeTab, setActiveTab] = useState('summary');
  const [activeSubTab, setActiveSubTab] = useState('trade-data');
  const [sampleData, setSampleData] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage] = useState(10);

  const toggleMenu = () => {
    setIsMenuOpen(!isMenuOpen);
    document.body.classList.toggle('no-scroll', !isMenuOpen);
  };

  const handleTabClick = (tab) => {
    setActiveTab(tab);
  };

  const handleSubTabClick = (subTab) => {
    setActiveSubTab(subTab);
  };

  useEffect(() => {
    const fetchSampleData = async () => {
      try {
        const API_BASE_URL = process.env.REACT_APP_BACKEND_URL || `http://${window.location.hostname}:8000`;
        const response = await fetch(`${API_BASE_URL}/api/sample-data`);
        const result = await response.json();
        if (result.success && result.data) {
          setSampleData(result.data);
        }
      } catch (error) {
        console.error('Error fetching sample data:', error);
        // Keep empty array as fallback
      } finally {
        setIsLoading(false);
      }
    };

    fetchSampleData();
  }, []);

  return (
    <div className="landing-page">
      <a href="#main-content" className="skip-link">Skip to main content</a>

      <header className="header" role="banner">
        <div className="logo">
          <img src="/logo.JPG" alt="SMBC Logo" className="logo-image" />
        </div>

        <button
          className="hamburger"
          aria-label="Toggle navigation menu"
          aria-controls="main-nav"
          aria-expanded={isMenuOpen}
          onClick={toggleMenu}
        >
          <span className="bar"></span>
          <span className="bar"></span>
          <span className="bar"></span>
        </button>

        <nav
          className={`nav ${isMenuOpen ? 'show' : ''}`}
          id="main-nav"
          role="navigation"
          aria-label="Main navigation"
        >
          <div className="nav-item" tabIndex="0" role="button">CCR Deck Assistant</div>
          <div className="nav-item" tabIndex="0" role="button">Analytics Tools</div>
          <div className="nav-item" tabIndex="0" role="button">Business Support Tools</div>
          <div className="nav-item" tabIndex="0" role="button">Reporting Dashboard</div>
          <div className="nav-item" tabIndex="0" role="button">Data Insights</div>
          <div className="nav-item" tabIndex="0" role="button">SQL Generator</div>
        </nav>

        <div className={`nav-right ${isMenuOpen ? 'show' : ''}`}>
          <button className="nav-link" onClick={onOpenAdmin}>Admin Panel</button>
          <div
            className="user-icon"
            tabIndex="0"
            role="button"
            aria-label="User menu"
          >
            <svg width="20" height="20" fill="white" viewBox="0 0 20 20">
              <path d="M10 10a4 4 0 100-8 4 4 0 000 8zm0 2c-4.42 0-8 1.79-8 4v2h16v-2c0-2.21-3.58-4-8-4z" />
            </svg>
          </div>
        </div>
      </header>

      <main id="main-content" className="container main-content" role="main">
        <div className="report-title-bar">
          <h1 className="report-title">Counterparty Risk Assistant</h1>
          <span className="env-tag">ENV: PROD</span>
        </div>
        
        <div className="report-content">
          <div className="report-data">
            <div className="report-header">
              <div className="controls-section">
                <div className="date-selector">
                  <label htmlFor="date-input" className="date-label">As Of Date:</label>
                  <input
                    type="date"
                    id="date-input"
                    className="date-input"
                    defaultValue="2025-01-27"
                    aria-label="Select as of date"
                  />
                </div>

                <div className="tab-btns tabs" role="tablist" aria-label="Report view tabs">
                  <button 
                    className={`tab-btn tab ${activeTab === 'summary' ? 'active' : ''}`} 
                    onClick={() => handleTabClick('summary')}
                  >
                    Summary
                  </button>
                  <button 
                    className={`tab-btn tab ${activeTab === 'detail' ? 'active' : ''}`} 
                    onClick={() => handleTabClick('detail')}
                  >
                    Detail
                  </button>
                </div>

                <div className="action-buttons">
                  <button className="btn btn-primary" onClick={onOpenChat}>
                    Ask Question
                  </button>
                  <button className="btn btn-secondary">
                    Sample Questions
                  </button>
                  <button className="btn btn-secondary">
                    Help & Guide
                  </button>
                </div>
              </div>
            </div>

            <div id="summary-content" className={`content-section tab-element tab-content ${activeTab === 'summary' ? 'active' : ''}`}>
              <div className="table-container" role="region" aria-live="polite" aria-label="Summary table">
                {isLoading ? (
                  <div className="empty-state">Loading data...</div>
                ) : (
                  <table>
                    <thead>
                      <tr>
                        <th scope="col">Entity</th>
                        <th scope="col">TradeCategory</th>
                        <th scope="col">TradeAssetClass</th>
                        <th scope="col">TradeType</th>
                        <th scope="col">TradeId</th>
                        <th scope="col">Analytics Addo</th>
                        <th scope="col">Analytics Input</th>
                        <th scope="col">Analytics Input</th>
                        <th scope="col">Analytics Output</th>
                        <th scope="col">Analytics Output</th>
                        <th scope="col">Reporting Status</th>
                      </tr>
                    </thead>
                    <tbody>
                      {sampleData.length > 0 ? (
                        sampleData
                          .slice((currentPage - 1) * itemsPerPage, currentPage * itemsPerPage)
                          .map((row, index) => (
                          <tr key={index}>
                            <td>{row.Entity}</td>
                            <td>{row.TradeCategory}</td>
                            <td>{row.TradeAssetClass}</td>
                            <td>{row.TradeType}</td>
                            <td>{row.TradeId}</td>
                            <td>{row['Analytics Addo']}</td>
                            <td>{row['Analytics Input']}</td>
                            <td>{row['Analytics Input2']}</td>
                            <td>{row['Analytics Output']}</td>
                            <td>{row['Analytics Output2']}</td>
                            <td>{row['Reporting Status']}</td>
                          </tr>
                        ))
                      ) : (
                        <tr>
                          <td colSpan="11" className="empty-state">No data available</td>
                        </tr>
                      )}
                    </tbody>
                  </table>
                )}
                
                {sampleData.length > itemsPerPage && (
                  <div className="pagination">
                    <button 
                      onClick={() => setCurrentPage(prev => Math.max(prev - 1, 1))}
                      disabled={currentPage === 1}
                      className="pagination-btn"
                    >
                      Previous
                    </button>
                    
                    <span className="pagination-info">
                      Page {currentPage} of {Math.ceil(sampleData.length / itemsPerPage)}
                    </span>
                    
                    <button 
                      onClick={() => setCurrentPage(prev => Math.min(prev + 1, Math.ceil(sampleData.length / itemsPerPage)))}
                      disabled={currentPage === Math.ceil(sampleData.length / itemsPerPage)}
                      className="pagination-btn"
                    >
                      Next
                    </button>
                  </div>
                )}
              </div>
            </div>

            <div id="detail-content" className={`content-section tab-element tab-content ${activeTab === 'detail' ? 'active' : ''}`}>
              <div className="detail-header">
                <div className="tab-btns sub-tabs" role="tablist" aria-label="Data view tabs">
                  <button 
                    className={`tab-btn sub-tab ${activeSubTab === 'trade-data' ? 'active' : ''}`} 
                    onClick={() => handleSubTabClick('trade-data')}
                  >
                    Getting Started
                  </button>
                  <button 
                    className={`tab-btn sub-tab ${activeSubTab === 'analytics' ? 'active' : ''}`} 
                    onClick={() => handleSubTabClick('analytics')}
                  >
                    Advanced Features
                  </button>
                </div>
                <div className="search-container">
                  <input
                    type="search"
                    className="search-input"
                    placeholder="Search features..."
                    aria-label="Search features"
                  />
                  <button className="search-btn" aria-label="Search">→</button>
                </div>
              </div>

              <div id="trade-data-content" className={`tab-element sub-tab-content ${activeSubTab === 'trade-data' ? 'active' : ''}`}>
                <div className="cta-section">
                  <h3>Ready to get started?</h3>
                  <p>Click "Start Chat Session" above to begin asking questions about your data. Transform your natural language questions into actionable business insights.</p>
                </div>
              </div>

              <div id="analytics-content" className={`tab-element sub-tab-content ${activeSubTab === 'analytics' ? 'active' : ''}`}>
                <div className="table-container" role="region" aria-live="polite" aria-label="Features table">
                  <table>
                    <thead>
                      <tr>
                        <th scope="col">Feature</th>
                        <th scope="col">Description</th>
                        <th scope="col">Use Case</th>
                        <th scope="col">Status</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr>
                        <td>SQL Generation</td>
                        <td>AI-powered SQL query generation</td>
                        <td>Data Analysis</td>
                        <td>Active</td>
                      </tr>
                      <tr>
                        <td>Real-time Chat</td>
                        <td>Interactive conversation interface</td>
                        <td>User Interaction</td>
                        <td>Active</td>
                      </tr>
                      <tr>
                        <td>Admin Dashboard</td>
                        <td>Feedback and training management</td>
                        <td>System Management</td>
                        <td>Active</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>

      <button className="chatbot-btn" onClick={onOpenChat} title="Start Chat">
        💬
      </button>
    </div>
  );
};

export default LandingPage;
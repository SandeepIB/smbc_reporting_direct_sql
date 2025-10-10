import React, { useState } from 'react';
import CommonHeader from './CommonHeader';
import './CCRDeckAssistantPage.css';

const CCRDeckAssistantPage = () => {
  const [files, setFiles] = useState([]);
  const [analysisResults, setAnalysisResults] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [uploadStatus, setUploadStatus] = useState('');
  const [cropConfig, setCropConfig] = useState({ rows: 2, cols: 3, enabled: true });

  const handleFileSelect = (e) => {
    const selectedFiles = Array.from(e.target.files);
    setFiles(selectedFiles);
    setUploadStatus(`${selectedFiles.length} files selected`);
  };

  const handleAnalyze = async () => {
    if (files.length === 0) {
      alert('Please select images first');
      return;
    }

    setIsAnalyzing(true);
    setUploadStatus('Uploading images...');

    try {
      const formData = new FormData();
      files.forEach(file => formData.append('files', file));

      await fetch('http://localhost:8001/upload-images', {
        method: 'POST',
        body: formData
      });

      setUploadStatus('Analyzing images with AI...');

      if (cropConfig.enabled) {
        await fetch('http://localhost:8001/configure-cropping', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(cropConfig)
        });
      }

      const response = await fetch('http://localhost:8001/analyze', {
        method: 'POST'
      });
      const results = await response.json();
      
      setAnalysisResults(results);
      setUploadStatus('Analysis complete!');
    } catch (error) {
      console.error('Analysis failed:', error);
      setUploadStatus(`Analysis failed: ${error.message || 'Please try again'}`);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleDownload = async () => {
    try {
      const response = await fetch('http://localhost:8001/download-report');
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `SMBC_Report_${new Date().toISOString().slice(0,10)}.pptx`;
      a.click();
    } catch (error) {
      console.error('Download failed:', error);
      alert('Download failed. Please try again.');
    }
  };

  return (
    <div className="ccr-page">
      <CommonHeader title="CCR Deck Assistant" showSearchIcon={false} />
      <main className="ccr-page-content">
        <div className="ccr-workflow">
          {/* Step 1: Upload */}
          <div className="workflow-step">
            <div className="step-header">
              <div className="step-number">1</div>
              <h2>Upload Chart Images</h2>
            </div>
            <div className="step-content">
              <div className="upload-area">
                <input
                  type="file"
                  multiple
                  accept="image/*"
                  onChange={handleFileSelect}
                  className="file-input"
                  id="ccr-file-input"
                />
                <label htmlFor="ccr-file-input" className="upload-zone">
                  <div className="upload-icon">📁</div>
                  <div className="upload-text">
                    <strong>Click to select images</strong>
                    <span>or drag and drop chart images here</span>
                  </div>
                </label>
              </div>
              
              {files.length > 0 && (
                <div className="selected-files">
                  <h3>{files.length} files selected</h3>
                  <div className="file-preview">
                    {files.slice(0, 3).map((file, index) => (
                      <img key={index} src={URL.createObjectURL(file)} alt={file.name} className="preview-thumb" />
                    ))}
                    {files.length > 3 && <div className="more-files">+{files.length - 3} more</div>}
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Step 2: Configure */}
          <div className="workflow-step">
            <div className="step-header">
              <div className="step-number">2</div>
              <h2>Analysis Settings</h2>
            </div>
            <div className="step-content">
              <div className="setting-item">
                <label className="setting-label">
                  <input 
                    type="checkbox" 
                    checked={cropConfig.enabled}
                    onChange={(e) => setCropConfig({...cropConfig, enabled: e.target.checked})}
                  />
                  <span>Enable automatic image cropping</span>
                </label>
                <p className="setting-desc">Automatically crop charts for better analysis accuracy</p>
              </div>
            </div>
          </div>

          {/* Step 3: Analyze */}
          <div className="workflow-step">
            <div className="step-header">
              <div className="step-number">3</div>
              <h2>Generate Analysis</h2>
            </div>
            <div className="step-content">
              <button 
                onClick={handleAnalyze}
                disabled={isAnalyzing || files.length === 0}
                className="analyze-button"
              >
                {isAnalyzing ? (
                  <>
                    <div className="spinner"></div>
                    Analyzing Images...
                  </>
                ) : (
                  <>
                    🔍 Analyze Charts
                  </>
                )}
              </button>
              
              {uploadStatus && (
                <div className="status-indicator">
                  {uploadStatus}
                </div>
              )}
            </div>
          </div>

          {/* Results Section */}
          {analysisResults && (
            <div className="results-panel">
              <div className="results-header">
                <h2>📊 Analysis Results</h2>
                <button onClick={handleDownload} className="download-button">
                  📥 Download Report
                </button>
              </div>
              
              <div className="results-grid">
                <div className="result-card executive">
                  <h3>Executive Summary</h3>
                  <div className="summary-item">
                    <strong>Trend:</strong> {analysisResults.executive_summary?.trend}
                  </div>
                  <div className="summary-item">
                    <strong>Recommendation:</strong> {analysisResults.executive_summary?.recommendation}
                  </div>
                </div>

                {analysisResults.graph_insights?.map((insight, index) => (
                  <div key={index} className="result-card insight">
                    <h4>{insight.title}</h4>
                    <div className="insight-detail">
                      <strong>Trend:</strong> {insight.trend}
                    </div>
                    <div className="insight-detail">
                      <strong>Recommendation:</strong> {insight.recommendation}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
};

export default CCRDeckAssistantPage;
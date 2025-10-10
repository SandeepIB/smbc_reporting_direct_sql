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

      await fetch('http://localhost:8001/upload', {
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

      const response = await fetch('http://localhost:8001/analyze');
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
      <CommonHeader title="CCR Deck Assistant" />
      <main className="ccr-page-content">
        <div className="ccr-container">
          <div className="upload-section">
            <div className="section-header">
              <h2>📊 Upload Images for Analysis</h2>
              <p>Select chart images to analyze and generate PowerPoint reports</p>
            </div>

            <div className="file-input-container">
              <input
                type="file"
                multiple
                accept="image/*"
                onChange={handleFileSelect}
                className="file-input"
                id="ccr-file-input"
              />
              <label htmlFor="ccr-file-input" className="file-input-label">
                📁 Select Images
              </label>
            </div>

            {files.length > 0 && (
              <div className="file-list">
                <h3>Selected Files ({files.length}):</h3>
                <div className="file-grid">
                  {files.map((file, index) => (
                    <div key={index} className="file-item">
                      <img 
                        src={URL.createObjectURL(file)} 
                        alt={file.name}
                        className="thumbnail"
                      />
                      <span className="file-name">{file.name}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            <div className="crop-config">
              <label className="crop-label">
                <input 
                  type="checkbox" 
                  checked={cropConfig.enabled}
                  onChange={(e) => setCropConfig({...cropConfig, enabled: e.target.checked})}
                />
                Enable image cropping
              </label>
            </div>

            <button 
              onClick={handleAnalyze}
              disabled={isAnalyzing || files.length === 0}
              className="analyze-btn"
            >
              {isAnalyzing ? 'Analyzing...' : 'Analyze Images'}
            </button>

            {uploadStatus && (
              <div className="status-message">
                {uploadStatus}
              </div>
            )}
          </div>

          {analysisResults && (
            <div className="results-section">
              <div className="section-header">
                <h2>📈 Analysis Results</h2>
              </div>
              
              <div className="executive-summary">
                <h3>Executive Summary</h3>
                <div className="summary-content">
                  <p><strong>Trend:</strong> {analysisResults.executive_summary?.trend}</p>
                  <p><strong>Recommendation:</strong> {analysisResults.executive_summary?.recommendation}</p>
                </div>
              </div>

              <div className="graph-insights">
                <h3>Graph Insights</h3>
                {analysisResults.graph_insights?.map((insight, index) => (
                  <div key={index} className="insight-card">
                    <h4>{insight.title}</h4>
                    <p><strong>Trend:</strong> {insight.trend}</p>
                    <p><strong>Recommendation:</strong> {insight.recommendation}</p>
                  </div>
                ))}
              </div>

              <button 
                onClick={handleDownload}
                disabled={isAnalyzing}
                className="download-btn"
              >
                📥 Download PowerPoint Report
              </button>
            </div>
          )}
        </div>
      </main>
    </div>
  );
};

export default CCRDeckAssistantPage;
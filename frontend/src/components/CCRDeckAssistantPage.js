import React, { useState } from 'react';
import CommonHeader from './CommonHeader';
import config from '../config/api';
import './CCRDeckAssistantPage.css';

const CCRDeckAssistantPage = () => {
  const [files, setFiles] = useState([]);
  const [analysisResults, setAnalysisResults] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [uploadStatus, setUploadStatus] = useState('');
  const [cropConfig, setCropConfig] = useState({ rows: 2, cols: 3, enabled: false });
  const [abortController, setAbortController] = useState(null);
  const [selectedImage, setSelectedImage] = useState(null);
  const [isEditing, setIsEditing] = useState(false);
  const [editableResults, setEditableResults] = useState(null);

  const handleReset = () => {
    setFiles([]);
    setAnalysisResults(null);
    setUploadStatus('');
    setCropConfig({ rows: 2, cols: 3, enabled: false });
    // Clear file input
    const fileInput = document.getElementById('ccr-file-input');
    if (fileInput) fileInput.value = '';
  };

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

    const controller = new AbortController();
    setAbortController(controller);
    setIsAnalyzing(true);
    setUploadStatus('Uploading images...');

    try {
      const formData = new FormData();
      files.forEach(file => formData.append('files', file));

      await fetch(`${config.CCR_API_URL}/upload-images`, {
        method: 'POST',
        body: formData,
        signal: controller.signal
      });

      setUploadStatus('Analyzing images with AI...');

      // Always send cropping configuration to backend
      await fetch(`${config.CCR_API_URL}/configure-cropping`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(cropConfig),
        signal: controller.signal
      });

      const response = await fetch(`${config.CCR_API_URL}/analyze`, {
        method: 'POST',
        signal: controller.signal
      });
      const results = await response.json();
      
      setAnalysisResults(results);
      setEditableResults(JSON.parse(JSON.stringify(results))); // Deep copy for editing
      setUploadStatus('Analysis complete!');
    } catch (error) {
      if (error.name === 'AbortError') {
        setUploadStatus('Analysis cancelled');
      } else {
        console.error('Analysis failed:', error);
        setUploadStatus(`Analysis failed: ${error.message || 'Please try again'}`);
      }
    } finally {
      setIsAnalyzing(false);
      setAbortController(null);
    }
  };

  const handleCancelAnalysis = () => {
    if (abortController) {
      abortController.abort();
    }
  };

  const handleDownload = async () => {
    try {
      // Send edited results to backend for report generation
      const response = await fetch(`${config.CCR_API_URL}/download-report`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ editedResults: editableResults || analysisResults })
      });
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

  const handleEditToggle = () => {
    if (!isEditing) {
      setEditableResults(JSON.parse(JSON.stringify(analysisResults))); // Fresh copy
    }
    setIsEditing(!isEditing);
  };

  const handleTextChange = (section, field, value) => {
    setEditableResults(prev => ({
      ...prev,
      [section]: {
        ...prev[section],
        [field]: value
      }
    }));
  };

  const handleInsightChange = (index, field, value) => {
    setEditableResults(prev => ({
      ...prev,
      graph_insights: prev.graph_insights.map((insight, i) => 
        i === index ? { ...insight, [field]: value } : insight
      )
    }));
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
                  <div className="files-header">
                    <h3>{files.length} files selected</h3>
                    <button onClick={handleReset} className="reset-button" title="Clear all files">
                      🗑️ Clear
                    </button>
                  </div>
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
              <div className="analyze-actions">
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
                
                {isAnalyzing && (
                  <button 
                    onClick={handleCancelAnalysis}
                    className="cancel-button"
                    title="Cancel current analysis"
                  >
                    ❌ Cancel Analysis
                  </button>
                )}
              </div>
              
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
                <div className="results-actions">
                  <button onClick={handleEditToggle} className={`edit-button ${isEditing ? 'editing' : ''}`}>
                    {isEditing ? '✅ Save Edits' : '✏️ Edit Text'}
                  </button>
                  <button onClick={handleReset} className="reset-button">
                    🔄 New Analysis
                  </button>
                  <button onClick={handleDownload} className="download-button">
                    📥 Download Report
                  </button>
                </div>
              </div>
              
              <div className="results-grid">
                <div className="result-card executive">
                  <h3>Executive Summary</h3>
                  <div className="summary-item">
                    <strong>Trend:</strong>
                    {isEditing ? (
                      <textarea
                        value={editableResults?.executive_summary?.trend || ''}
                        onChange={(e) => handleTextChange('executive_summary', 'trend', e.target.value)}
                        className="edit-textarea"
                        rows={4}
                      />
                    ) : (
                      <span>{(editableResults || analysisResults).executive_summary?.trend}</span>
                    )}
                  </div>
                  <div className="summary-item">
                    <strong>Recommendation:</strong>
                    {isEditing ? (
                      <textarea
                        value={editableResults?.executive_summary?.recommendation || ''}
                        onChange={(e) => handleTextChange('executive_summary', 'recommendation', e.target.value)}
                        className="edit-textarea"
                        rows={4}
                      />
                    ) : (
                      <span>{(editableResults || analysisResults).executive_summary?.recommendation}</span>
                    )}
                  </div>
                </div>

                {analysisResults.graph_insights?.map((insight, index) => (
                  <div key={index} className="result-card insight-with-image">
                    <div className="insight-layout">
                      <div className="insight-thumbnail" onClick={() => setSelectedImage(insight.filename)}>
                        <img 
                          src={`${config.CCR_API_URL}/images/${insight.filename}`}
                          alt={insight.filename}
                          className="thumbnail-image"
                          onError={(e) => {
                            e.target.style.display = 'none';
                            e.target.nextSibling.style.display = 'block';
                          }}
                        />
                        <div className="chart-placeholder" style={{display: 'none'}}>
                          📊
                        </div>
                        <span className="image-filename">{insight.filename}</span>
                      </div>
                      <div className="insight-content">
                        <h4>
                          {isEditing ? (
                            <input
                              type="text"
                              value={editableResults?.graph_insights?.[index]?.title || insight.title}
                              onChange={(e) => handleInsightChange(index, 'title', e.target.value)}
                              className="edit-input"
                            />
                          ) : (
                            (editableResults?.graph_insights?.[index]?.title || insight.title)
                          )}
                        </h4>
                        <div className="insight-section">
                          <strong>Trend:</strong>
                          {isEditing ? (
                            <textarea
                              value={editableResults?.graph_insights?.[index]?.trend || insight.trend}
                              onChange={(e) => handleInsightChange(index, 'trend', e.target.value)}
                              className="edit-textarea"
                              rows={3}
                            />
                          ) : (
                            <p>{editableResults?.graph_insights?.[index]?.trend || insight.trend}</p>
                          )}
                        </div>
                        <div className="insight-section">
                          <strong>Recommendation:</strong>
                          {isEditing ? (
                            <textarea
                              value={editableResults?.graph_insights?.[index]?.recommendation || insight.recommendation}
                              onChange={(e) => handleInsightChange(index, 'recommendation', e.target.value)}
                              className="edit-textarea"
                              rows={3}
                            />
                          ) : (
                            <p>{editableResults?.graph_insights?.[index]?.recommendation || insight.recommendation}</p>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
                
                {/* Image Popup Modal */}
                {selectedImage && (
                  <div className="image-modal" onClick={() => setSelectedImage(null)}>
                    <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                      <button className="close-button" onClick={() => setSelectedImage(null)}>
                        ✕
                      </button>
                      <img 
                        src={`${config.CCR_API_URL}/images/${selectedImage}`}
                        alt={selectedImage}
                        className="modal-image"
                      />
                      <div className="modal-filename">{selectedImage}</div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
};

export default CCRDeckAssistantPage;
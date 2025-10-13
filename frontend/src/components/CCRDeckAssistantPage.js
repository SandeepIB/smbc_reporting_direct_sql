import React, { useState, useEffect } from 'react';
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
  const [isEditMode, setIsEditMode] = useState(false);
  const [editedResults, setEditedResults] = useState(null);
  const [zoomedImage, setZoomedImage] = useState(null);

  // Fix scrolling issue
  useEffect(() => {
    // Enable scrolling on mount
    document.body.style.overflow = 'auto';
    document.body.style.height = 'auto';
    document.documentElement.style.overflow = 'auto';
    document.documentElement.style.height = 'auto';
    
    // Cleanup on unmount
    return () => {
      document.body.style.overflow = '';
      document.body.style.height = '';
      document.documentElement.style.overflow = '';
      document.documentElement.style.height = '';
    };
  }, []);

  const handleReset = () => {
    setFiles([]);
    setAnalysisResults(null);
    setUploadStatus('');
    setCropConfig({ rows: 2, cols: 3, enabled: false });
    const fileInput = document.getElementById('ccr-file-input');
    if (fileInput) fileInput.value = '';
  };

  const handleFileSelect = (e) => {
    const selectedFiles = Array.from(e.target.files);
    setFiles(selectedFiles);
    setUploadStatus(`${selectedFiles.length} files selected`);
  };

  const handleAnalyze = async () => {
    console.log('🔍 CCR Analysis Started');
    
    try {
      console.log('Files selected:', files.length);
      console.log('API URL:', config.API_URL);
      console.log('Crop config:', cropConfig);
      
      if (files.length === 0) {
        console.error('❌ No files selected');
        setUploadStatus('❌ Please select images first');
        return;
      }

      const controller = new AbortController();
      setAbortController(controller);
      setIsAnalyzing(true);
      setUploadStatus('Uploading images...');

    try {
      const formData = new FormData();
      files.forEach((file, index) => {
        console.log(`📁 Adding file ${index + 1}:`, file.name, file.type, file.size);
        formData.append('files', file);
      });

      console.log('📤 Uploading to:', `${config.API_URL}/upload-images`);
      
      const uploadResponse = await fetch(`${config.API_URL}/upload-images`, {
        method: 'POST',
        body: formData,
        signal: controller.signal
      });
      
      console.log('📤 Upload response status:', uploadResponse.status);
      
      if (!uploadResponse.ok) {
        const errorText = await uploadResponse.text();
        console.error('❌ Upload failed:', errorText);
        throw new Error(`Upload failed: ${uploadResponse.status} - ${errorText}`);
      }

      const uploadResult = await uploadResponse.json();
      console.log('✅ Upload successful:', uploadResult);

      setUploadStatus('Configuring analysis settings...');
      console.log('⚙️ Configuring cropping:', cropConfig);

      const configResponse = await fetch(`${config.API_URL}/configure-cropping`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(cropConfig),
        signal: controller.signal
      });

      console.log('⚙️ Config response status:', configResponse.status);
      
      if (!configResponse.ok) {
        const errorText = await configResponse.text();
        console.error('❌ Configuration failed:', errorText);
        throw new Error(`Configuration failed: ${configResponse.status} - ${errorText}`);
      }

      const configResult = await configResponse.json();
      console.log('✅ Configuration successful:', configResult);

      setUploadStatus('Analyzing images with AI...');
      console.log('🤖 Starting AI analysis...');

      const analyzeResponse = await fetch(`${config.API_URL}/analyze`, {
        method: 'POST',
        signal: controller.signal
      });

      console.log('🤖 Analysis response status:', analyzeResponse.status);
      
      if (!analyzeResponse.ok) {
        const errorText = await analyzeResponse.text();
        console.error('❌ Analysis failed:', errorText);
        throw new Error(`Analysis failed: ${analyzeResponse.status} - ${errorText}`);
      }

      const results = await analyzeResponse.json();
      console.log('✅ Analysis results:', results);
      
      setAnalysisResults(results);
      setUploadStatus('Analysis complete!');
      console.log('🎉 CCR Analysis Complete!');
      
      // Force a re-render check
      setTimeout(() => {
        console.log('🔍 Checking state after timeout - analysisResults:', analysisResults);
      }, 100);
    } catch (error) {
      console.error('💥 CCR Analysis Error:', error);
      console.error('Error name:', error.name);
      console.error('Error message:', error.message);
      console.error('Error stack:', error.stack);
      

      if (error.name === 'AbortError') {
        console.log('🛑 Analysis cancelled by user');
        setUploadStatus('❌ Analysis cancelled');
      } else {
        console.error('❌ Analysis failed with error:', error.message);
        setUploadStatus(`❌ Analysis failed: ${error.message || 'Network error - please check connection'}`);
      }
    } finally {
      console.log('🔄 Cleaning up analysis state');
      setIsAnalyzing(false);
      setAbortController(null);
    }
  } catch (outerError) {
    console.error('💥 Outer function error:', outerError);
    alert('Function error: ' + outerError.message);
    setIsAnalyzing(false);
  }
  };

  const handleCancelAnalysis = () => {
    if (abortController) {
      abortController.abort();
    }
  };

  const handleDownload = async () => {
    try {
      const response = await fetch(`${config.API_URL}/download-report`);
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

  const handleEditAll = () => {
    setIsEditMode(true);
    setEditedResults(JSON.parse(JSON.stringify(analysisResults))); // Deep copy
  };

  const handleSaveAll = () => {
    setAnalysisResults(editedResults);
    setIsEditMode(false);
    setEditedResults(null);
  };

  const handleCancelEdit = () => {
    setIsEditMode(false);
    setEditedResults(null);
  };

  const handleUpdateExecutiveTrend = (value) => {
    setEditedResults(prev => ({
      ...prev,
      executive_summary: {
        ...prev.executive_summary,
        trend: value
      }
    }));
  };

  const handleUpdateExecutiveRecommendation = (value) => {
    setEditedResults(prev => ({
      ...prev,
      executive_summary: {
        ...prev.executive_summary,
        recommendation: value
      }
    }));
  };

  const handleUpdateInsightTrend = (index, value) => {
    setEditedResults(prev => {
      const newResults = { ...prev };
      newResults.graph_insights[index] = {
        ...newResults.graph_insights[index],
        trend: value
      };
      return newResults;
    });
  };

  const handleUpdateInsightRecommendation = (index, value) => {
    setEditedResults(prev => {
      const newResults = { ...prev };
      newResults.graph_insights[index] = {
        ...newResults.graph_insights[index],
        recommendation: value
      };
      return newResults;
    });
  };

  return (
    <div className="ccr-page" style={{overflow: 'visible', height: 'auto', minHeight: '100vh'}}>
      <CommonHeader title="CCR Deck Assistant" />
      
      <main className="ccr-page-content">
        <div className="ccr-workflow">
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
                    <button onClick={handleReset} className="reset-button">
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

          {analysisResults && (
            <div className="results-panel">
              <div className="results-header">
                <h2>📊 Analysis Results</h2>
                <div className="results-actions">
                  {!isEditMode ? (
                    <>
                      <button onClick={handleEditAll} className="edit-all-button">
                        ✏️ Edit All
                      </button>
                      <button onClick={handleReset} className="reset-button">
                        🔄 New Analysis
                      </button>
                      <button onClick={handleDownload} className="download-button">
                        📥 Download Report
                      </button>
                    </>
                  ) : (
                    <>
                      <button onClick={handleSaveAll} className="save-all-button">
                        ✓ Save All Changes
                      </button>
                      <button onClick={handleCancelEdit} className="cancel-edit-button">
                        ✗ Cancel
                      </button>
                    </>
                  )}
                </div>
              </div>
              
              <div className="results-grid">
                <div className="result-card executive">
                  <h3>Executive Summary</h3>
                  {!isEditMode ? (
                    <>
                      <div className="summary-item">
                        <strong>Trend:</strong> {analysisResults.executive_summary?.trend}
                      </div>
                      <div className="summary-item">
                        <strong>Recommendation:</strong> {analysisResults.executive_summary?.recommendation}
                      </div>
                    </>
                  ) : (
                    <div className="edit-executive-form">
                      <div className="edit-field">
                        <strong>Trend:</strong>
                        <textarea
                          value={editedResults?.executive_summary?.trend || ''}
                          onChange={(e) => handleUpdateExecutiveTrend(e.target.value)}
                          className="edit-textarea"
                          rows="3"
                        />
                      </div>
                      <div className="edit-field">
                        <strong>Recommendation:</strong>
                        <textarea
                          value={editedResults?.executive_summary?.recommendation || ''}
                          onChange={(e) => handleUpdateExecutiveRecommendation(e.target.value)}
                          className="edit-textarea"
                          rows="3"
                        />
                      </div>
                    </div>
                  )}
                </div>

                {(isEditMode ? editedResults?.graph_insights : analysisResults.graph_insights)?.map((insight, index) => (
                  <div key={index} className="result-card insight-with-image">
                    <div className="insight-layout">
                      <div className="insight-thumbnail">
                        <img 
                          src={`${config.API_URL}${insight.image_url}`}
                          alt={insight.filename}
                          className="chart-thumbnail"
                          onClick={() => setZoomedImage(`${config.API_URL}${insight.image_url}`)}
                          onError={(e) => {
                            e.target.style.display = 'none';
                            e.target.nextSibling.style.display = 'block';
                          }}
                        />
                        <div className="chart-placeholder" style={{display: 'none'}}>
                          📊
                        </div>
                      </div>
                      <div className="insight-content">
                        <h4>{insight.title}</h4>
                        
                        {!isEditMode ? (
                          <>
                            <div className="insight-section">
                              <strong>Trend:</strong>
                              <p>{insight.trend}</p>
                            </div>
                            <div className="insight-section">
                              <strong>Recommendation:</strong>
                              <p>{insight.recommendation}</p>
                            </div>
                          </>
                        ) : (
                          <div className="edit-insight-form">
                            <div className="edit-field">
                              <strong>Trend:</strong>
                              <textarea
                                value={insight.trend}
                                onChange={(e) => handleUpdateInsightTrend(index, e.target.value)}
                                className="edit-textarea"
                                rows="2"
                              />
                            </div>
                            <div className="edit-field">
                              <strong>Recommendation:</strong>
                              <textarea
                                value={insight.recommendation}
                                onChange={(e) => handleUpdateInsightRecommendation(index, e.target.value)}
                                className="edit-textarea"
                                rows="2"
                              />
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
          
          {/* Image Zoom Modal */}
          {zoomedImage && (
            <div className="image-zoom-modal" onClick={() => setZoomedImage(null)}>
              <div className="zoom-modal-content" onClick={(e) => e.stopPropagation()}>
                <button className="close-zoom" onClick={() => setZoomedImage(null)}>
                  ✕
                </button>
                <img src={zoomedImage} alt="Zoomed chart" className="zoomed-image" />
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
};

export default CCRDeckAssistantPage;
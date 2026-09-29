import React, { useState, useRef } from 'react';
import { UploadCloud, FileText, CheckCircle2, Sparkles, ArrowRight, BookOpen, Layers, RefreshCw } from 'lucide-react';

export default function MaterialsTab({
  material,
  onUploadPdf,
  onLoadSample,
  onNavigateToTab,
  isLoading
}) {
  const [dragOver, setDragOver] = useState(false);
  const fileInputRef = useRef(null);

  const handleFileChange = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      if (!file.name.toLowerCase().endsWith('.pdf')) {
        alert('Only PDF files are supported. Please select a valid .pdf file.');
        return;
      }
      onUploadPdf(file);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setDragOver(true);
  };

  const handleDragLeave = () => {
    setDragOver(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files?.[0];
    if (file) {
      if (!file.name.toLowerCase().endsWith('.pdf')) {
        alert('Only PDF files are supported. Please select a valid .pdf file.');
        return;
      }
      onUploadPdf(file);
    }
  };

  const hasMaterial = material && material.filename && material.text;

  return (
    <div className="card" id="materials-section">
      <div className="card-header">
        <h2 className="card-title">
          <BookOpen className="text-primary" size={24} color="#818cf8" />
          <span>Upload Study Material</span>
        </h2>
        <p className="card-description">
          Upload any lecture notes, syllabus, or textbook PDF to extract core concepts and generate an adaptive study roadmap.
        </p>
      </div>

      {/* Large Dropzone */}
      <div
        className={`dropzone ${dragOver ? 'drag-active' : ''}`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
      >
        <input
          type="file"
          ref={fileInputRef}
          onChange={handleFileChange}
          accept="application/pdf"
          style={{ display: 'none' }}
          id="pdf-upload-input"
        />

        <div className="dropzone-icon">
          <UploadCloud size={32} />
        </div>

        <h3 className="dropzone-title">Drop your PDF here</h3>
        <p className="dropzone-subtitle">or click to browse from your device (PDF only)</p>

        <div className="dropzone-actions" onClick={(e) => e.stopPropagation()}>
          <button
            type="button"
            id="upload-pdf-btn"
            className="btn btn-primary"
            onClick={() => fileInputRef.current?.click()}
            disabled={isLoading}
          >
            {isLoading ? (
              <>
                <span className="spinner"></span>
                <span>Processing PDF...</span>
              </>
            ) : (
              <>
                <UploadCloud size={16} />
                <span>Upload PDF</span>
              </>
            )}
          </button>

          <button
            type="button"
            id="load-sample-btn"
            className="btn btn-secondary"
            onClick={onLoadSample}
            disabled={isLoading}
            title="Load built-in 5-page Computer Networks PDF instantly"
          >
            <Sparkles size={16} color="#fbbf24" />
            <span>Load Sample PDF (Computer Networks)</span>
          </button>
        </div>
      </div>

      {/* Uploaded Material Preview */}
      {hasMaterial && (
        <div style={{ marginTop: '32px' }}>
          {/* File Meta Header Bar */}
          <div className="material-info-bar">
            <div className="material-meta">
              <div className="doc-icon-badge">PDF</div>
              <div>
                <div className="material-title">{material.filename}</div>
                <div className="material-stats">
                  <span className="stat-pill">
                    <strong>{material.pages}</strong> {material.pages === 1 ? 'page' : 'pages'}
                  </span>
                  <span>&bull;</span>
                  <span className="stat-pill">
                    <strong>{material.word_count || material.text.split(' ').length}</strong> words
                  </span>
                </div>
              </div>
            </div>

            <button
              className="btn btn-secondary btn-sm"
              onClick={() => fileInputRef.current?.click()}
              title="Replace current document"
            >
              <RefreshCw size={14} />
              <span>Change PDF</span>
            </button>
          </div>

          {/* Extracted Text Preview */}
          <div style={{ marginBottom: '24px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
              <span style={{ fontSize: '13px', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.6px' }}>
                Extracted text preview
              </span>
              <span style={{ fontSize: '12px', color: 'var(--text-dim)' }}>
                pypdf extraction
              </span>
            </div>
            <div className="text-preview-box" id="extracted-text-preview">
              {material.text_preview || material.text.slice(0, 800) + '...'}
            </div>
          </div>

          {/* Detected Topics */}
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
              <Layers size={18} color="#818cf8" />
              <h3 style={{ fontFamily: 'var(--font-heading)', fontSize: '18px', fontWeight: 700, color: '#fff' }}>
                Detected Topics
              </h3>
              <span style={{ fontSize: '12px', background: 'rgba(99, 102, 241, 0.2)', color: '#a5b4fc', padding: '2px 8px', borderRadius: '12px', fontWeight: 600 }}>
                {material.topics?.length || 0} identified
              </span>
            </div>

            <div className="topics-grid" id="detected-topics-list">
              {material.topics && material.topics.length > 0 ? (
                material.topics.map((topic, idx) => (
                  <div key={idx} className="topic-tag">
                    <CheckCircle2 size={14} color="#10b981" />
                    <span>{topic}</span>
                  </div>
                ))
              ) : (
                <div style={{ color: 'var(--text-muted)', fontSize: '14px' }}>
                  No topics identified yet.
                </div>
              )}
            </div>

            {/* Quick Action Navigation */}
            <div style={{ marginTop: '28px', display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
              <button
                id="goto-study-plan-btn"
                className="btn btn-primary"
                onClick={() => onNavigateToTab('study-plan')}
              >
                <span>Generate Study Plan</span>
                <ArrowRight size={16} />
              </button>

              <button
                id="goto-quiz-btn"
                className="btn btn-secondary"
                onClick={() => onNavigateToTab('quiz')}
              >
                <span>Take a Practice Quiz</span>
                <ArrowRight size={16} />
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

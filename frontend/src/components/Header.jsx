import React from 'react';
import { BookOpen, Sparkles, Cpu, FileText } from 'lucide-react';

export default function Header({ systemStatus, currentMaterial }) {
  const isOllama = systemStatus?.ollama_available;
  const modelName = systemStatus?.ollama_model;
  const fileName = currentMaterial?.filename;
  const pageCount = currentMaterial?.pages;

  return (
    <header className="app-header">
      <div className="header-top">
        <div className="brand-section">
          <div className="brand-logo">
            <BookOpen size={24} />
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center' }}>
              <h1 className="brand-title">StudyFlow AI</h1>
              <span className="brand-badge">Hackathon Edition</span>
            </div>
            <p className="brand-subtitle">AI-Powered Personalized Study Assistant</p>
          </div>
        </div>

        <div className="header-badges">
          {/* AI Engine Status */}
          <div className="status-pill" title={isOllama ? `Connected to local Ollama (${modelName})` : "Using instant heuristic neural engine"}>
            <span className={`status-dot ${isOllama ? '' : 'warning'}`}></span>
            <Cpu size={14} />
            <span>
              {isOllama ? `Ollama: ${modelName}` : "Smart Fallback Engine (Offline)"}
            </span>
          </div>

          {/* Loaded Document Pill */}
          {fileName && (
            <div className="status-pill" style={{ borderColor: 'rgba(99, 102, 241, 0.4)' }}>
              <FileText size={14} color="#818cf8" />
              <span style={{ color: '#e0e7ff', fontWeight: 600 }}>
                {fileName} ({pageCount} {pageCount === 1 ? 'page' : 'pages'})
              </span>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}

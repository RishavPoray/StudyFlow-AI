import React, { useState, useEffect } from 'react';
import { HelpCircle, CheckCircle, XCircle, Sparkles, RefreshCw, ArrowRight, BookOpen, AlertTriangle, Check, Award } from 'lucide-react';
import confetti from 'canvas-confetti';

export default function QuizTab({
  material,
  quizQuestions,
  lastQuizResult,
  onGenerateQuiz,
  onSubmitQuiz,
  onAddRevisionTask,
  onNavigateToTab,
  isLoading
}) {
  const topics = material?.topics || ["OSI Model", "TCP/IP", "Network Devices", "Network Topologies", "Protocols"];
  const [selectedTopic, setSelectedTopic] = useState("All Topics");
  const [numQuestions, setNumQuestions] = useState(5);
  const [userAnswers, setUserAnswers] = useState({});
  const [hasUpdatedPlan, setHasUpdatedPlan] = useState(false);
  const [revisionAddedMessage, setRevisionAddedMessage] = useState("");

  // Update selected topic if topics change
  useEffect(() => {
    if (topics.length > 0 && selectedTopic === "All Topics") {
      // Keep "All Topics" as option, but valid
    }
  }, [topics]);

  // Trigger celebratory confetti on high score
  useEffect(() => {
    if (lastQuizResult && lastQuizResult.percentage >= 80) {
      try {
        confetti({
          particleCount: 80,
          spread: 70,
          origin: { y: 0.6 }
        });
      } catch (e) {
        // Safe fallback if canvas not available
      }
    }
  }, [lastQuizResult]);

  const handleStartQuiz = (e) => {
    e.preventDefault();
    setUserAnswers({});
    setHasUpdatedPlan(false);
    setRevisionAddedMessage("");
    onGenerateQuiz(selectedTopic, parseInt(numQuestions) || 5);
  };

  const handleSelectOption = (questionId, optionLetter) => {
    setUserAnswers((prev) => ({
      ...prev,
      [questionId]: optionLetter
    }));
  };

  const handleSubmitQuiz = (e) => {
    e.preventDefault();
    if (quizQuestions.length === 0) return;

    // Check if any unanswered
    const answeredCount = Object.keys(userAnswers).length;
    if (answeredCount < quizQuestions.length) {
      const confirmSubmit = window.confirm(
        `You have answered ${answeredCount} of ${quizQuestions.length} questions. Submit anyway?`
      );
      if (!confirmSubmit) return;
    }

    onSubmitQuiz(userAnswers);
  };

  const handleUpdateStudyPlan = async () => {
    if (!lastQuizResult) return;
    const weakTopics = lastQuizResult.weak_topics;
    const targetTopic = weakTopics && weakTopics.length > 0 ? weakTopics[0] : (material?.topics?.[0] || "Targeted Concept");

    const res = await onAddRevisionTask(targetTopic, "30 minutes");
    if (res?.success) {
      setHasUpdatedPlan(true);
      setRevisionAddedMessage(res.message || `Added ${targetTopic} Revision to your Study Plan!`);
    }
  };

  const hasQuestions = quizQuestions && quizQuestions.length > 0;
  const showResults = Boolean(lastQuizResult);

  return (
    <div className="card" id="quiz-section">
      <div className="card-header">
        <h2 className="card-title">
          <HelpCircle className="text-primary" size={24} color="#818cf8" />
          <span>Interactive Knowledge Quiz</span>
        </h2>
        <p className="card-description">
          Generate multiple-choice questions from your uploaded study material to evaluate mastery and diagnose weak topics.
        </p>
      </div>

      {/* QUIZ CONFIGURATION FORM (Always available or when resetting) */}
      {(!hasQuestions || showResults) && (
        <form onSubmit={handleStartQuiz} style={{ marginBottom: '28px' }}>
          <div className="form-row">
            <div className="form-group">
              <label className="form-label" htmlFor="quiz-topic-select">
                Select topic:
              </label>
              <select
                id="quiz-topic-select"
                className="form-select"
                value={selectedTopic}
                onChange={(e) => setSelectedTopic(e.target.value)}
              >
                <option value="All Topics">All Topics (Comprehensive Mix)</option>
                {topics.map((t, i) => (
                  <option key={i} value={t}>
                    {t}
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label className="form-label" htmlFor="quiz-num-questions">
                Number of questions:
              </label>
              <select
                id="quiz-num-questions"
                className="form-select"
                value={numQuestions}
                onChange={(e) => setNumQuestions(e.target.value)}
              >
                <option value={3}>3 Questions (Quick Check)</option>
                <option value={5}>5 Questions (Standard)</option>
                <option value={8}>8 Questions (In-depth)</option>
                <option value={10}>10 Questions (Mastery)</option>
              </select>
            </div>
          </div>

          <button
            type="submit"
            id="generate-quiz-btn"
            className="btn btn-primary"
            disabled={isLoading}
            style={{ width: '100%' }}
          >
            {isLoading ? (
              <>
                <span className="spinner"></span>
                <span>Generating Quiz Questions...</span>
              </>
            ) : (
              <>
                <Sparkles size={16} />
                <span>Generate Quiz</span>
              </>
            )}
          </button>
        </form>
      )}

      {/* ACTIVE QUIZ VIEW */}
      {hasQuestions && !showResults && (
        <form onSubmit={handleSubmitQuiz} id="active-quiz-form">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '18px', flexWrap: 'wrap', gap: '8px' }}>
            <span style={{ fontSize: '14px', fontWeight: 600, color: 'var(--text-muted)' }}>
              Topic: <strong style={{ color: '#fff' }}>{selectedTopic}</strong>
            </span>
            <span style={{ fontSize: '13px', background: 'rgba(99, 102, 241, 0.2)', color: '#818cf8', padding: '3px 10px', borderRadius: '12px', fontWeight: 600 }}>
              {Object.keys(userAnswers).length} of {quizQuestions.length} answered
            </span>
          </div>

          <div className="questions-container">
            {quizQuestions.map((q, idx) => {
              const questionNum = idx + 1;
              const selectedOption = userAnswers[q.id];

              return (
                <div key={q.id} className="question-card" id={`question-card-${q.id}`}>
                  <div className="question-header">
                    <span style={{ fontSize: '13px', fontWeight: 700, color: 'var(--primary-light)', textTransform: 'uppercase', letterSpacing: '0.6px' }}>
                      Question {questionNum}
                    </span>
                    <span className="question-topic-pill">{q.topic || selectedTopic}</span>
                  </div>

                  <p className="question-prompt">{q.question}</p>

                  <div className="options-list">
                    {q.options.map((optText, optIdx) => {
                      const letter = String.fromCharCode(65 + optIdx); // 'A', 'B', 'C', 'D'
                      const isSelected = selectedOption === letter;

                      return (
                        <button
                          key={optIdx}
                          type="button"
                          id={`option-${q.id}-${letter}`}
                          className={`option-btn ${isSelected ? 'selected' : ''}`}
                          onClick={() => handleSelectOption(q.id, letter)}
                        >
                          <span className="option-letter">{letter}</span>
                          <span style={{ flex: 1 }}>{optText}</span>
                          {isSelected && <Check size={16} color="#818cf8" />}
                        </button>
                      );
                    })}
                  </div>
                </div>
              );
            })}
          </div>

          <button
            type="submit"
            id="submit-quiz-btn"
            className="btn btn-success"
            disabled={isLoading}
            style={{ width: '100%', marginTop: '8px', padding: '14px' }}
          >
            {isLoading ? (
              <>
                <span className="spinner"></span>
                <span>Evaluating Your Responses...</span>
              </>
            ) : (
              <>
                <CheckCircle size={18} />
                <span>Submit Quiz</span>
              </>
            )}
          </button>
        </form>
      )}

      {/* QUIZ RESULTS VIEW */}
      {showResults && lastQuizResult && (
        <div id="quiz-results-container">
          <div className="results-hero">
            <h3 style={{ fontSize: '14px', textTransform: 'uppercase', letterSpacing: '1px', color: 'var(--text-muted)', marginBottom: '8px', fontWeight: 700 }}>
              Your Result
            </h3>
            <div className="score-display">
              <span className="score-number" id="result-score-text">
                {lastQuizResult.score} / {lastQuizResult.total}
              </span>
              <span
                id="result-percentage-badge"
                className={`score-percentage ${
                  lastQuizResult.percentage >= 80 ? 'high' : lastQuizResult.percentage >= 60 ? 'mid' : 'low'
                }`}
              >
                {lastQuizResult.percentage}%
              </span>
            </div>
          </div>

          {/* Topics Breakdown Grid */}
          <div className="results-grid">
            {/* Strong Topics */}
            <div className="result-card" id="strong-topics-card">
              <div className="result-card-header strong-header">
                <CheckCircle size={18} />
                <span>Strong Topics</span>
              </div>
              <div className="topics-pill-list">
                {lastQuizResult.strong_topics && lastQuizResult.strong_topics.length > 0 ? (
                  lastQuizResult.strong_topics.map((st, i) => (
                    <span key={i} className="strong-pill">
                      ✔ {st}
                    </span>
                  ))
                ) : (
                  <span style={{ fontSize: '13px', color: 'var(--text-muted)' }}>
                    Keep practicing to establish high proficiency.
                  </span>
                )}
              </div>
            </div>

            {/* Needs Practice */}
            <div className="result-card" id="weak-topics-card">
              <div className="result-card-header weak-header">
                <AlertTriangle size={18} />
                <span>Needs Practice</span>
              </div>
              <div className="topics-pill-list">
                {lastQuizResult.weak_topics && lastQuizResult.weak_topics.length > 0 ? (
                  lastQuizResult.weak_topics.map((wt, i) => (
                    <span key={i} className="weak-pill">
                      ⚠ {wt}
                    </span>
                  ))
                ) : (
                  <span style={{ fontSize: '13px', color: '#34d399' }}>
                    No weak areas detected! Great conceptual mastery.
                  </span>
                )}
              </div>
            </div>
          </div>

          {/* AI Recommendation Card */}
          <div className="ai-recommendation-card" id="ai-recommendation-card">
            <div className="ai-recommendation-header">
              <Sparkles size={20} color="#fbbf24" />
              <span>AI Recommendation</span>
            </div>

            <p className="ai-recommendation-text" id="ai-recommendation-text">
              "{lastQuizResult.recommendation}"
            </p>

            {/* Update Study Plan Action */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', flexWrap: 'wrap' }}>
              <button
                type="button"
                id="update-study-plan-btn"
                className="btn btn-primary"
                onClick={handleUpdateStudyPlan}
                disabled={hasUpdatedPlan || isLoading}
              >
                <Sparkles size={16} />
                <span>{hasUpdatedPlan ? "Study Plan Updated!" : "Update Study Plan"}</span>
              </button>

              {hasUpdatedPlan && (
                <button
                  type="button"
                  id="view-updated-plan-btn"
                  className="btn btn-secondary"
                  onClick={() => onNavigateToTab('study-plan')}
                >
                  <span>View Updated Study Plan</span>
                  <ArrowRight size={16} />
                </button>
              )}
            </div>

            {revisionAddedMessage && (
              <div style={{
                padding: '10px 14px',
                background: 'rgba(16, 185, 129, 0.15)',
                border: '1px solid rgba(16, 185, 129, 0.3)',
                borderRadius: 'var(--radius-sm)',
                color: '#34d399',
                fontSize: '13px',
                display: 'flex',
                alignItems: 'center',
                gap: '8px'
              }}>
                <CheckCircle size={16} />
                <span>{revisionAddedMessage}</span>
              </div>
            )}
          </div>

          {/* Detailed Question Review */}
          <details style={{ background: 'rgba(17, 24, 39, 0.5)', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)', padding: '16px', marginBottom: '24px' }}>
            <summary style={{ cursor: 'pointer', fontWeight: 600, color: 'var(--text-main)', fontSize: '14px' }}>
              Review Detailed Answers & Explanations ({lastQuizResult.breakdown?.length || 0} questions)
            </summary>
            <div style={{ marginTop: '16px', display: 'flex', flexDirection: 'column', gap: '14px' }}>
              {lastQuizResult.breakdown?.map((item, idx) => (
                <div
                  key={idx}
                  style={{
                    padding: '12px 16px',
                    borderRadius: 'var(--radius-sm)',
                    background: item.is_correct ? 'rgba(16, 185, 129, 0.08)' : 'rgba(239, 68, 68, 0.08)',
                    border: `1px solid ${item.is_correct ? 'rgba(16, 185, 129, 0.25)' : 'rgba(239, 68, 68, 0.25)'}`
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '6px' }}>
                    <span style={{ fontSize: '13px', fontWeight: 600, color: '#fff' }}>
                      Q{idx + 1}: {item.question}
                    </span>
                    <span style={{
                      fontSize: '11px',
                      fontWeight: 700,
                      padding: '2px 8px',
                      borderRadius: '12px',
                      background: item.is_correct ? 'var(--success-bg)' : 'var(--danger-bg)',
                      color: item.is_correct ? '#34d399' : '#f87171'
                    }}>
                      {item.is_correct ? 'Correct' : 'Incorrect'}
                    </span>
                  </div>
                  <div style={{ fontSize: '13px', color: 'var(--text-muted)' }}>
                    Your answer: <strong style={{ color: item.is_correct ? '#34d399' : '#f87171' }}>Option {item.user_answer}</strong>
                    {!item.is_correct && (
                      <span style={{ marginLeft: '12px' }}>
                        Correct answer: <strong style={{ color: '#34d399' }}>Option {item.correct_answer}</strong>
                      </span>
                    )}
                  </div>
                  {item.explanation && (
                    <div style={{ fontSize: '12px', color: 'var(--text-dim)', marginTop: '4px', fontStyle: 'italic' }}>
                      💡 {item.explanation}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </details>

          {/* Quiz Actions */}
          <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
            <button
              type="button"
              id="retake-quiz-btn"
              className="btn btn-secondary"
              onClick={handleStartQuiz}
            >
              <RefreshCw size={16} />
              <span>Retake Quiz</span>
            </button>
            <button
              type="button"
              className="btn btn-secondary"
              onClick={() => onNavigateToTab('study-plan')}
            >
              <span>View Study Plan</span>
              <ArrowRight size={16} />
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

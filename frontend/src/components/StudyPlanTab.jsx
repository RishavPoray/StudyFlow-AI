import React, { useState } from 'react';
import { Calendar, Clock, CheckSquare, Sparkles, Award, ArrowRight, PlusCircle, AlertCircle } from 'lucide-react';

export default function StudyPlanTab({
  studyPlan,
  studyPlanMeta,
  material,
  onGeneratePlan,
  onToggleTask,
  onNavigateToTab,
  isLoading
}) {
  // Calculate default exam date (7 days from today)
  const getDefaultExamDate = () => {
    const d = new Date();
    d.setDate(d.getDate() + 7);
    return d.toISOString().split('T')[0];
  };

  const [examDate, setExamDate] = useState(studyPlanMeta?.exam_date || getDefaultExamDate());
  const [hoursPerDay, setHoursPerDay] = useState(studyPlanMeta?.hours_per_day || 1.5);

  const handleSubmit = (e) => {
    e.preventDefault();
    onGeneratePlan(examDate, parseFloat(hoursPerDay) || 1.5);
  };

  const totalTasks = studyPlan.length;
  const completedTasks = studyPlan.filter((t) => t.completed).length;
  const progressPercent = totalTasks > 0 ? Math.round((completedTasks / totalTasks) * 100) : 0;

  // Compute plan duration text (e.g. "Your 7-Day Study Plan")
  const maxDay = totalTasks > 0 ? Math.max(...studyPlan.map((t) => t.day || 1)) : 7;
  const planTitle = `Your ${maxDay}-Day Study Plan`;

  const hasMaterial = material && material.filename;

  return (
    <div className="card" id="study-plan-section">
      <div className="card-header">
        <h2 className="card-title">
          <Calendar className="text-primary" size={24} color="#818cf8" />
          <span>Create Your Study Plan</span>
        </h2>
        <p className="card-description">
          Define your target exam timeline and daily commitment to generate a structured, day-by-day learning schedule.
        </p>
      </div>

      {/* Warning banner if material not loaded */}
      {!hasMaterial && (
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '12px',
          padding: '12px 16px',
          background: 'rgba(245, 158, 11, 0.1)',
          border: '1px solid rgba(245, 158, 11, 0.3)',
          borderRadius: 'var(--radius-md)',
          marginBottom: '20px',
          fontSize: '13px',
          color: '#fbbf24'
        }}>
          <AlertCircle size={18} />
          <span>
            No study material uploaded yet. Generating a plan will use standard core networking topics.
          </span>
          <button
            type="button"
            className="btn btn-secondary btn-sm"
            onClick={() => onNavigateToTab('materials')}
            style={{ marginLeft: 'auto' }}
          >
            Upload PDF First
          </button>
        </div>
      )}

      {/* Input Form */}
      <form onSubmit={handleSubmit} style={{ marginBottom: '32px' }}>
        <div className="form-row">
          <div className="form-group">
            <label className="form-label" htmlFor="exam-date-input">
              Exam date:
            </label>
            <input
              type="date"
              id="exam-date-input"
              className="form-input"
              value={examDate}
              min={new Date().toISOString().split('T')[0]}
              onChange={(e) => setExamDate(e.target.value)}
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="study-hours-input">
              Available study hours per day:
            </label>
            <div style={{ display: 'flex', gap: '8px' }}>
              <input
                type="number"
                id="study-hours-input"
                className="form-input"
                value={hoursPerDay}
                min="0.5"
                max="12"
                step="0.5"
                onChange={(e) => setHoursPerDay(e.target.value)}
                required
              />
              {/* Quick Preset Buttons */}
              <button
                type="button"
                className="btn btn-secondary btn-sm"
                onClick={() => setHoursPerDay(1)}
              >
                1h
              </button>
              <button
                type="button"
                className="btn btn-secondary btn-sm"
                onClick={() => setHoursPerDay(1.5)}
              >
                1.5h
              </button>
              <button
                type="button"
                className="btn btn-secondary btn-sm"
                onClick={() => setHoursPerDay(2)}
              >
                2h
              </button>
            </div>
          </div>
        </div>

        <button
          type="submit"
          id="generate-plan-btn"
          className="btn btn-primary"
          disabled={isLoading}
          style={{ width: '100%' }}
        >
          {isLoading ? (
            <>
              <span className="spinner"></span>
              <span>Synthesizing Personalized Schedule...</span>
            </>
          ) : (
            <>
              <Sparkles size={16} />
              <span>Generate Study Plan</span>
            </>
          )}
        </button>
      </form>

      {/* Generated Study Plan Display */}
      {studyPlan && studyPlan.length > 0 && (
        <div id="generated-plan-container">
          <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            flexWrap: 'wrap',
            gap: '12px',
            borderTop: '1px solid var(--border-subtle)',
            paddingTop: '24px'
          }}>
            <div>
              <h3 style={{ fontFamily: 'var(--font-heading)', fontSize: '20px', fontWeight: 700, color: '#fff' }}>
                {planTitle}
              </h3>
              <p style={{ fontSize: '13px', color: 'var(--text-muted)' }}>
                {completedTasks} of {totalTasks} tasks completed ({progressPercent}%)
              </p>
            </div>

            {progressPercent === 100 && (
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#34d399', fontSize: '14px', fontWeight: 700 }}>
                <Award size={18} />
                <span>All Tasks Completed! Ready for Exam!</span>
              </div>
            )}
          </div>

          {/* Progress Bar */}
          <div className="plan-progress-bar-container">
            <div
              className="plan-progress-fill"
              style={{ width: `${progressPercent}%` }}
            ></div>
          </div>

          {/* Day-by-Day Task List */}
          <div className="plan-timeline" id="plan-tasks-list">
            {studyPlan.map((task) => {
              const isRevision = task.type === 'revision' || task.is_ai_recommended;
              const isQuiz = task.type === 'quiz';

              return (
                <div
                  key={task.id}
                  className={`task-item ${task.completed ? 'completed' : ''} ${isRevision ? 'is-revision' : ''} ${isQuiz ? 'is-quiz' : ''}`}
                >
                  <input
                    type="checkbox"
                    id={`checkbox-${task.id}`}
                    className="custom-checkbox"
                    checked={task.completed || false}
                    onChange={(e) => onToggleTask(task.id, e.target.checked)}
                    aria-label={`Mark Day ${task.day}: ${task.topic} as completed`}
                  />

                  <div className="task-content">
                    <div className="task-header-row">
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <span className="task-day-tag">Day {task.day}</span>
                        {task.is_ai_recommended && (
                          <span className="task-tag-ai">
                            ⚡ AI Targeted Revision
                          </span>
                        )}
                      </div>

                      <span className="task-duration-badge">
                        <Clock size={12} style={{ display: 'inline', marginRight: '4px', verticalAlign: '-1px' }} />
                        {task.duration}
                      </span>
                    </div>

                    <div className="task-topic-title">
                      {task.topic}
                    </div>

                    {task.description && (
                      <p className="task-desc">
                        {task.description}
                      </p>
                    )}
                  </div>
                </div>
              );
            })}
          </div>

          {/* Post-Plan Call to Action */}
          <div style={{ marginTop: '28px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '12px' }}>
            <span style={{ fontSize: '13px', color: 'var(--text-muted)' }}>
              Tip: Test your recall right now with an adaptive quiz.
            </span>
            <button
              id="plan-to-quiz-btn"
              className="btn btn-secondary"
              onClick={() => onNavigateToTab('quiz')}
            >
              <span>Test Knowledge with Quiz</span>
              <ArrowRight size={16} />
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

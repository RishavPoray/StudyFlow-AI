import React from 'react';
import { FileText, Calendar, HelpCircle } from 'lucide-react';

export default function TabsNav({ activeTab, setActiveTab, topicsCount, planCount, completedCount, quizScore }) {
  return (
    <nav className="tabs-nav" aria-label="Main Navigation">
      <button
        id="tab-materials"
        className={`tab-btn ${activeTab === 'materials' ? 'active' : ''}`}
        onClick={() => setActiveTab('materials')}
      >
        <FileText size={18} />
        <span>📄 Materials</span>
        {topicsCount > 0 && <span className="tab-counter">{topicsCount} topics</span>}
      </button>

      <button
        id="tab-study-plan"
        className={`tab-btn ${activeTab === 'study-plan' ? 'active' : ''}`}
        onClick={() => setActiveTab('study-plan')}
      >
        <Calendar size={18} />
        <span>📅 Study Plan</span>
        {planCount > 0 && (
          <span className="tab-counter">
            {completedCount}/{planCount} done
          </span>
        )}
      </button>

      <button
        id="tab-quiz"
        className={`tab-btn ${activeTab === 'quiz' ? 'active' : ''}`}
        onClick={() => setActiveTab('quiz')}
      >
        <HelpCircle size={18} />
        <span>📝 Quiz</span>
        {quizScore !== null && <span className="tab-counter">{quizScore}%</span>}
      </button>
    </nav>
  );
}

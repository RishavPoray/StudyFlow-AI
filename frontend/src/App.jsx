import { useMemo, useRef, useState } from 'react'

const LETTERS = ['A', 'B', 'C', 'D']
const API = '/api'

const STEPS = [
  { id: 'upload', label: 'Upload PDF', short: 'Upload' },
  { id: 'topics', label: 'Topics', short: 'Topics' },
  { id: 'plan', label: 'Study Plan', short: 'Plan' },
  { id: 'quiz', label: 'Quiz', short: 'Quiz' },
  { id: 'results', label: 'Results', short: 'Results' },
]

const styles = `
:root {
  --sf-bg: #0b1020;
  --sf-surface: rgba(18, 25, 45, .88);
  --sf-surface2: rgba(27, 36, 61, .72);
  --sf-border: rgba(148, 163, 184, .16);
  --sf-text: #f8fafc;
  --sf-muted: #94a3b8;
  --sf-accent: #7c6cff;
  --sf-accent2: #a78bfa;
  --sf-success: #34d399;
  --sf-danger: #fb7185;
  --sf-warn: #fbbf24;
}
* { box-sizing: border-box; }
.app {
  min-height: 100vh;
  color: var(--sf-text);
  max-width: 1040px;
  margin: 0 auto;
  padding: 28px 20px 56px;
}
.sf-header {
  display:flex; align-items:center; justify-content:space-between; gap:20px;
  padding: 20px 22px; margin-bottom:18px;
  border:1px solid var(--sf-border); border-radius:20px;
  background:linear-gradient(135deg,rgba(124,108,255,.13),rgba(167,139,250,.04));
  backdrop-filter: blur(14px);
}
.sf-brand { display:flex; align-items:center; gap:12px; }
.sf-logo {
  width:44px; height:44px; display:grid; place-items:center;
  border-radius:14px; background:rgba(124,108,255,.16);
  border:1px solid rgba(167,139,250,.25); color:var(--sf-accent2);
  font-size:22px;
}
.sf-title { font-size:1.35rem; font-weight:800; letter-spacing:-.02em; }
.sf-subtitle { color:var(--sf-muted); font-size:.82rem; margin-top:3px; }
.sf-pill {
  padding:7px 11px; border-radius:999px; font-size:.75rem; color:#c4b5fd;
  background:rgba(124,108,255,.11); border:1px solid rgba(167,139,250,.2);
}
.sf-steps {
  display:grid; grid-template-columns:repeat(5,1fr); gap:8px;
  padding:8px; margin-bottom:18px; border:1px solid var(--sf-border);
  border-radius:16px; background:rgba(15,23,42,.7);
}
.sf-step {
  border:0; background:transparent; color:var(--sf-muted); border-radius:11px;
  padding:10px 7px; cursor:pointer; transition:.2s; font:inherit;
}
.sf-step:hover:not(:disabled) { background:rgba(255,255,255,.04); color:var(--sf-text); }
.sf-step.active { color:#fff; background:rgba(124,108,255,.17); }
.sf-step.done { color:#c4b5fd; }
.sf-step:disabled { cursor:not-allowed; opacity:.5; }
.sf-step-num {
  width:26px; height:26px; border-radius:50%; display:inline-grid; place-items:center;
  margin-right:7px; font-size:.74rem; font-weight:800;
  background:rgba(148,163,184,.1); border:1px solid var(--sf-border);
}
.sf-step.active .sf-step-num { background:var(--sf-accent); color:white; border-color:transparent; }
.sf-step.done .sf-step-num { background:rgba(52,211,153,.13); color:var(--sf-success); }
.sf-progress { height:3px; background:rgba(148,163,184,.1); border-radius:99px; margin:-8px 5px 18px; overflow:hidden; }
.sf-progress > div { height:100%; background:linear-gradient(90deg,var(--sf-accent),var(--sf-accent2)); transition:.3s; }
.sf-card {
  background:var(--sf-surface); border:1px solid var(--sf-border); border-radius:20px;
  padding:24px; margin-bottom:16px; box-shadow:0 18px 55px rgba(0,0,0,.12);
}
.sf-card-title { display:flex; align-items:center; gap:9px; font-size:1.02rem; font-weight:750; margin-bottom:18px; }
.sf-card-title .icon { color:var(--sf-accent2); }
.sf-muted { color:var(--sf-muted); }
.sf-upload {
  min-height:300px; display:grid; place-items:center; text-align:center;
  border:1.5px dashed rgba(167,139,250,.35); border-radius:18px;
  background:radial-gradient(circle at center,rgba(124,108,255,.09),transparent 60%);
  cursor:pointer; transition:.2s;
}
.sf-upload:hover,.sf-upload.drag { border-color:var(--sf-accent2); background:rgba(124,108,255,.12); transform:translateY(-1px); }
.sf-upload-icon { font-size:34px; margin-bottom:12px; }
.sf-upload-title { font-size:1.05rem; font-weight:700; }
.sf-upload-sub { color:var(--sf-muted); font-size:.82rem; margin-top:6px; }
.sf-meta { display:flex; gap:8px; flex-wrap:wrap; margin-bottom:13px; }
.sf-meta-item,.sf-badge {
  display:inline-flex; align-items:center; gap:6px; padding:7px 10px; border-radius:9px;
  background:var(--sf-surface2); border:1px solid var(--sf-border); color:#cbd5e1; font-size:.78rem;
}
.sf-badge.accent { color:#ddd6fe; background:rgba(124,108,255,.11); border-color:rgba(167,139,250,.18); }
.sf-badge.success { color:#a7f3d0; background:rgba(52,211,153,.08); }
.sf-badge.warn { color:#fde68a; background:rgba(251,191,36,.08); }
.sf-preview {
  max-height:250px; overflow:auto; white-space:pre-wrap; line-height:1.65;
  padding:15px; border-radius:12px; background:rgba(2,6,23,.42);
  border:1px solid var(--sf-border); color:#cbd5e1; font-size:.82rem;
}
.sf-topics { display:grid; grid-template-columns:repeat(auto-fill,minmax(190px,1fr)); gap:9px; }
.sf-topic {
  display:flex; justify-content:space-between; gap:8px; align-items:center;
  padding:11px 12px; border-radius:11px; background:var(--sf-surface2);
  border:1px solid var(--sf-border); font-size:.82rem;
}
.sf-score { min-width:25px; text-align:center; border-radius:7px; padding:3px 5px; font-size:.7rem; color:#c4b5fd; background:rgba(124,108,255,.14); }
.sf-form-grid { display:grid; grid-template-columns:1fr 1fr; gap:14px; }
.sf-field label { display:block; color:#cbd5e1; font-size:.8rem; font-weight:650; margin-bottom:7px; }
.sf-field input {
  width:100%; border:1px solid var(--sf-border); border-radius:10px; padding:11px 12px;
  color:var(--sf-text); background:rgba(2,6,23,.4); outline:none; font:inherit;
}
.sf-field input:focus { border-color:rgba(167,139,250,.6); box-shadow:0 0 0 3px rgba(124,108,255,.1); }
.sf-actions { display:flex; align-items:center; justify-content:flex-end; gap:10px; flex-wrap:wrap; }
.sf-btn {
  border:0; border-radius:10px; padding:11px 16px; cursor:pointer; font:inherit;
  font-weight:700; transition:.18s; display:inline-flex; align-items:center; gap:8px;
}
.sf-btn:hover:not(:disabled) { transform:translateY(-1px); }
.sf-btn:disabled { opacity:.5; cursor:not-allowed; transform:none; }
.sf-btn-primary { color:white; background:linear-gradient(135deg,#6d5dfc,#8b5cf6); box-shadow:0 8px 25px rgba(124,108,255,.2); }
.sf-btn-ghost { color:#cbd5e1; background:rgba(148,163,184,.07); border:1px solid var(--sf-border); }
.sf-alert { padding:11px 13px; border-radius:10px; margin-top:13px; font-size:.83rem; }
.sf-error { color:#fecdd3; background:rgba(251,113,133,.08); border:1px solid rgba(251,113,133,.18); }
.sf-info { color:#c4b5fd; background:rgba(124,108,255,.08); border:1px solid rgba(124,108,255,.16); }
.sf-divider { height:1px; background:var(--sf-border); margin:20px 0; }
.sf-plan { display:grid; gap:9px; max-height:480px; overflow:auto; padding-right:3px; }
.sf-day {
  display:flex; gap:14px; padding:13px; border-radius:12px; background:var(--sf-surface2);
  border:1px solid var(--sf-border);
}
.sf-day-num { width:42px; height:42px; flex:0 0 42px; display:grid; place-items:center; border-radius:11px; color:#ddd6fe; background:rgba(124,108,255,.13); font-size:.75rem; font-weight:800; }
.sf-day-date { font-size:.74rem; color:var(--sf-muted); margin-bottom:4px; }
.sf-day-task { font-size:.86rem; line-height:1.45; }
.sf-day-hours { color:#a7f3d0; font-size:.72rem; margin-top:5px; }
.sf-question { padding:18px 0; border-top:1px solid var(--sf-border); }
.sf-question:first-of-type { border-top:0; }
.sf-q-top { display:flex; justify-content:space-between; gap:10px; color:var(--sf-muted); font-size:.73rem; margin-bottom:9px; }
.sf-q-text { font-size:1rem; font-weight:650; line-height:1.5; margin-bottom:13px; }
.sf-options { display:grid; gap:8px; }
.sf-option {
  width:100%; display:flex; align-items:center; gap:10px; text-align:left;
  border:1px solid var(--sf-border); background:rgba(2,6,23,.25); color:#dbe4f0;
  border-radius:11px; padding:11px 12px; cursor:pointer; font:inherit; transition:.16s;
}
.sf-option:hover:not(:disabled) { border-color:rgba(167,139,250,.4); background:rgba(124,108,255,.07); }
.sf-option.selected { border-color:rgba(167,139,250,.55); background:rgba(124,108,255,.12); }
.sf-option.correct { border-color:rgba(52,211,153,.45); background:rgba(52,211,153,.08); color:#d1fae5; }
.sf-option.wrong { border-color:rgba(251,113,133,.45); background:rgba(251,113,133,.08); color:#fecdd3; }
.sf-letter {
  width:27px; height:27px; flex:0 0 27px; display:grid; place-items:center; border-radius:8px;
  background:rgba(148,163,184,.09); font-size:.74rem; font-weight:800;
}
.sf-score-box { text-align:center; padding:24px; border-radius:16px; background:radial-gradient(circle at center,rgba(124,108,255,.12),transparent 70%); }
.sf-score-num { font-size:3rem; line-height:1; font-weight:850; letter-spacing:-.05em; }
.sf-score-good { color:#6ee7b7; } .sf-score-ok { color:#fcd34d; } .sf-score-poor { color:#fb7185; }
.sf-breakdown { display:grid; gap:7px; }
.sf-break-row { display:flex; gap:9px; padding:10px; border-radius:9px; background:var(--sf-surface2); font-size:.8rem; }
.sf-footer { text-align:center; color:#64748b; font-size:.72rem; padding-top:8px; }
.sf-spinner {
  width:16px; height:16px; border:2px solid rgba(255,255,255,.25); border-top-color:#fff;
  border-radius:50%; animation:sfspin .7s linear infinite; display:inline-block;
}
@keyframes sfspin { to { transform:rotate(360deg); } }
@media(max-width:700px) {
  .app { padding:14px 12px 40px; }
  .sf-header { padding:16px; }
  .sf-pill { display:none; }
  .sf-steps { gap:3px; }
  .sf-step { font-size:.7rem; padding:8px 3px; }
  .sf-step-num { display:block; margin:0 auto 4px; }
  .sf-form-grid { grid-template-columns:1fr; }
  .sf-card { padding:17px; border-radius:16px; }
  .sf-upload { min-height:250px; }
}
`

async function apiPost(path, body, isFormData = false) {
  const res = await fetch(API + path, {
    method: 'POST',
    body: isFormData ? body : JSON.stringify(body),
    headers: isFormData ? {} : { 'Content-Type': 'application/json' },
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(err.detail || 'Request failed')
  }
  return res.json()
}

function Spinner() {
  return <span className="sf-spinner" />
}

function UploadStep({ onDone }) {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [drag, setDrag] = useState(false)
  const inputRef = useRef(null)

  async function handleFile(file) {
    if (!file) return
    if (!file.name.toLowerCase().endsWith('.pdf')) {
      setError('Please select a PDF file.')
      return
    }
    setError(null)
    setLoading(true)
    try {
      const fd = new FormData()
      fd.append('file', file)
      onDone(await apiPost('/upload', fd, true))
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <section className="sf-card">
      <div className="sf-card-title"><span className="icon">📄</span> Upload your study material</div>
      <div
        className={`sf-upload${drag ? ' drag' : ''}`}
        onClick={() => !loading && inputRef.current?.click()}
        onDragOver={e => { e.preventDefault(); setDrag(true) }}
        onDragLeave={() => setDrag(false)}
        onDrop={e => { e.preventDefault(); setDrag(false); handleFile(e.dataTransfer.files[0]) }}
      >
        <input ref={inputRef} type="file" accept=".pdf,application/pdf" hidden disabled={loading}
          onChange={e => handleFile(e.target.files[0])} />
        <div>
          <div className="sf-upload-icon">{loading ? <Spinner /> : '↑'}</div>
          <div className="sf-upload-title">{loading ? 'Extracting your PDF…' : 'Drop your PDF here'}</div>
          <div className="sf-upload-sub">{loading ? 'Reading pages and detecting topics' : 'or click to browse · PDF files only'}</div>
        </div>
      </div>
      {error && <div className="sf-alert sf-error">⚠ {error}</div>}
    </section>
  )
}

function TopicsStep({ data, onNext }) {
  const [full, setFull] = useState(false)
  const preview = full ? data.full_text : data.full_text.slice(0, 1000) + (data.full_text.length > 1000 ? '…' : '')

  return (
    <>
      <section className="sf-card">
        <div className="sf-card-title"><span className="icon">📄</span> Extracted Content</div>
        <div className="sf-meta">
          <span className="sf-meta-item">📄 <strong>{data.filename}</strong></span>
          <span className="sf-meta-item">Pages <strong>{data.total_pages}</strong></span>
          <span className="sf-meta-item">Words <strong>{data.word_count.toLocaleString()}</strong></span>
        </div>
        <div className="sf-preview">{preview}</div>
        <button className="sf-btn sf-btn-ghost" style={{ marginTop: 10 }} onClick={() => setFull(v => !v)}>
          {full ? 'Show less' : 'Show full text'}
        </button>
      </section>

      <section className="sf-card">
        <div className="sf-card-title"><span className="icon">✦</span> Detected Study Topics</div>
        {!data.detected_topics?.length ? (
          <div className="sf-alert sf-info">No clear topics were detected. You can still create a general study plan.</div>
        ) : (
          <div className="sf-topics">
            {data.detected_topics.map(t => (
              <div className="sf-topic" key={t.topic} title={`Keywords: ${(t.keywords_found || []).join(', ')}`}>
                <span>{t.topic}</span><span className="sf-score">{t.score}</span>
              </div>
            ))}
          </div>
        )}
        <div className="sf-actions" style={{ marginTop: 18 }}>
          <button className="sf-btn sf-btn-primary" onClick={onNext}>Generate Study Plan →</button>
        </div>
      </section>
    </>
  )
}

function PlanStep({ topics, onDone, onNext }) {
  const defaultDate = useMemo(() => {
    const d = new Date()
    d.setDate(d.getDate() + 7)
    return d.toISOString().split('T')[0]
  }, [])
  const [examDate, setExamDate] = useState(defaultDate)
  const [hours, setHours] = useState('2')
  const [plan, setPlan] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const topicNames = topics.length ? topics.map(t => t.topic) : ['General Review']

  async function generate() {
    setError(null)
    const h = Number(hours)
    if (!examDate) return setError('Please select an exam date.')
    if (!h || h < 0.5 || h > 12) return setError('Daily study time must be between 0.5 and 12 hours.')
    setLoading(true)
    try {
      const data = await apiPost('/study-plan', { topics: topicNames, exam_date: examDate, daily_hours: h })
      setPlan(data)
      onDone(data)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <section className="sf-card">
      <div className="sf-card-title"><span className="icon">◷</span> Build your study plan</div>
      <div className="sf-form-grid">
        <div className="sf-field">
          <label>Exam date</label>
          <input type="date" value={examDate} min={new Date().toISOString().split('T')[0]} onChange={e => setExamDate(e.target.value)} />
        </div>
        <div className="sf-field">
          <label>Hours available per day</label>
          <input type="number" value={hours} min="0.5" max="12" step="0.5" onChange={e => setHours(e.target.value)} />
        </div>
      </div>

      <div style={{ marginTop: 18 }}>
        <div className="sf-muted" style={{ fontSize: '.78rem', marginBottom: 8 }}>Topics in this plan</div>
        <div className="sf-meta">{topicNames.map(t => <span className="sf-badge accent" key={t}>{t}</span>)}</div>
      </div>

      {error && <div className="sf-alert sf-error">⚠ {error}</div>}

      <div className="sf-actions" style={{ marginTop: 16 }}>
        <button className="sf-btn sf-btn-primary" onClick={generate} disabled={loading}>
          {loading ? <><Spinner /> Generating plan…</> : 'Generate Plan'}
        </button>
      </div>

      {plan && (
        <>
          <div className="sf-divider" />
          <div className="sf-meta">
            <span className="sf-badge accent">📅 {plan.days_left} days</span>
            <span className="sf-badge accent">⏱ {plan.total_study_hours}h total</span>
            <span className="sf-badge accent">~{plan.hours_per_topic}h/topic</span>
          </div>
          <div className="sf-plan">
            {plan.plan.map(d => (
              <div className="sf-day" key={d.day}>
                <div className="sf-day-num">D{d.day}</div>
                <div style={{ minWidth: 0 }}>
                  <div className="sf-day-date">
                    {new Date(d.date + 'T00:00:00').toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' })}
                  </div>
                  <div className="sf-day-task">{(d.tasks || []).join(' · ')}</div>
                  <div className="sf-day-hours">{d.hours}h study</div>
                </div>
              </div>
            ))}
          </div>
          <div className="sf-actions" style={{ marginTop: 18 }}>
            <button className="sf-btn sf-btn-primary" onClick={onNext}>Continue to Quiz →</button>
          </div>
        </>
      )}
    </section>
  )
}

function QuizStep({ text, onDone }) {
  const [questions, setQuestions] = useState(null)
  const [answers, setAnswers] = useState({})
  const [submitted, setSubmitted] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [numQ, setNumQ] = useState(5)

  async function loadQuiz() {
    setError(null)
    setLoading(true)
    setAnswers({})
    setSubmitted(false)
    try {
      const n = Math.max(3, Math.min(15, Number(numQ) || 5))
      setNumQ(n)
      const data = await apiPost('/quiz', { text, num_questions: n })
      if (!data.questions?.length) throw new Error('No quiz questions were generated. Please try again.')
      setQuestions(data.questions)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  function submit() {
    if (!questions) return
    const results = questions.map(q => ({
      ...q,
      chosen: answers[q.id] ?? null,
      correct: answers[q.id] === q.answer,
    }))
    setSubmitted(true)
    onDone(results)
  }

  return (
    <section className="sf-card">
      <div className="sf-card-title"><span className="icon">🧠</span> Practice Quiz</div>

      {!questions && (
        <>
          <p className="sf-muted" style={{ marginTop: -7, fontSize: '.84rem' }}>
            Test your understanding with conceptual questions from your uploaded material.
          </p>
          <div className="sf-form-grid" style={{ maxWidth: 520, marginTop: 18 }}>
            <div className="sf-field">
              <label>Number of questions</label>
              <input type="number" value={numQ} min="3" max="15" onChange={e => setNumQ(e.target.value)} />
            </div>
            <div className="sf-actions" style={{ justifyContent: 'flex-start', alignItems: 'end' }}>
              <button className="sf-btn sf-btn-primary" onClick={loadQuiz} disabled={loading}>
                {loading ? <><Spinner /> Generating quiz…</> : 'Generate Quiz'}
              </button>
            </div>
          </div>
        </>
      )}

      {error && <div className="sf-alert sf-error">⚠ {error}</div>}

      {questions && (
        <>
          <div className="sf-meta">
            <span className="sf-badge accent">{questions.length} questions</span>
            <span className="sf-badge">Choose one answer for each</span>
          </div>

          {questions.map((q, qi) => {
            const chosen = answers[q.id]
            return (
              <div className="sf-question" key={q.id}>
                <div className="sf-q-top">
                  <span>Question {qi + 1} of {questions.length}</span>
                  <span>{chosen ? 'Answered' : 'Not answered'}</span>
                </div>
                <div className="sf-q-text">{q.question}</div>
                <div className="sf-options">
                  {(q.options || []).map((opt, oi) => {
                    let cls = 'sf-option'
                    if (submitted) {
                      if (opt === q.answer) cls += ' correct'
                      else if (opt === chosen) cls += ' wrong'
                    } else if (opt === chosen) cls += ' selected'
                    return (
                      <button className={cls} key={oi} disabled={submitted} onClick={() => !submitted && setAnswers(a => ({ ...a, [q.id]: opt }))}>
                        <span className="sf-letter">{LETTERS[oi]}</span>
                        <span>{opt}</span>
                        {submitted && opt === q.answer && <span style={{ marginLeft: 'auto' }}>✓</span>}
                      </button>
                    )
                  })}
                </div>
              </div>
            )
          })}

          <div className="sf-actions" style={{ marginTop: 12 }}>
            {!submitted ? (
              <button className="sf-btn sf-btn-primary" onClick={submit} disabled={questions.some(q => !answers[q.id])}>
                Submit Quiz
              </button>
            ) : (
              <button className="sf-btn sf-btn-ghost" onClick={() => { setQuestions(null); setSubmitted(false); setAnswers({}); }}>
                ↻ Try Another Quiz
              </button>
            )}
          </div>
          {!submitted && questions.some(q => !answers[q.id]) && (
            <div className="sf-muted" style={{ textAlign: 'right', fontSize: '.74rem', marginTop: 8 }}>Answer all questions to submit.</div>
          )}
        </>
      )}
    </section>
  )
}

function ResultsStep({ results, detectedTopics, onReset }) {
  if (!results) return <section className="sf-card"><div className="sf-muted">Complete the quiz to see your results.</div></section>

  const total = results.length
  const correct = results.filter(r => r.correct).length
  const pct = Math.round((correct / total) * 100)
  const scoreClass = pct >= 80 ? 'sf-score-good' : pct >= 50 ? 'sf-score-ok' : 'sf-score-poor'
  const message = pct >= 80 ? 'Excellent work!' : pct >= 50 ? 'Good start — keep practising.' : 'Keep practising and revisit the topics.'

  const wrongCount = total - correct
  const weakTopics = detectedTopics.slice(0, Math.min(detectedTopics.length, Math.max(1, Math.ceil(wrongCount / 2))))

  return (
    <section className="sf-card">
      <div className="sf-card-title"><span className="icon">📊</span> Quiz Results</div>
      <div className="sf-score-box">
        <div className={`sf-score-num ${scoreClass}`}>{pct}%</div>
        <div style={{ fontWeight: 750, marginTop: 10 }}>{message}</div>
        <div className="sf-muted" style={{ fontSize: '.8rem', marginTop: 5 }}>{correct} of {total} answers correct</div>
      </div>

      <div className="sf-divider" />
      <div style={{ fontWeight: 700, marginBottom: 10 }}>Question Breakdown</div>
      <div className="sf-breakdown">
        {results.map((r, i) => (
          <div className="sf-break-row" key={i}>
            <span>{r.correct ? '✅' : '❌'}</span>
            <div style={{ minWidth: 0 }}>
              <div style={{ color: '#cbd5e1' }}>Q{i + 1}: {r.question}</div>
              {!r.correct && (
                <div style={{ marginTop: 5, color: '#94a3b8' }}>
                  Your answer: <span style={{ color: '#fb7185' }}>{r.chosen || 'Not answered'}</span>
                  {' · '}Correct: <span style={{ color: '#6ee7b7' }}>{r.answer}</span>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      {wrongCount > 0 && weakTopics.length > 0 && (
        <>
          <div className="sf-divider" />
          <div style={{ fontWeight: 700, marginBottom: 9 }}>Topics to revisit</div>
          <div className="sf-meta">
            {weakTopics.map(t => <span className="sf-badge warn" key={t.topic}>{t.topic}</span>)}
          </div>
        </>
      )}

      <div className="sf-actions" style={{ marginTop: 18 }}>
        <button className="sf-btn sf-btn-ghost" onClick={onReset}>↻ Start Over</button>
      </div>
    </section>
  )
}

export default function App() {
  const [step, setStep] = useState(0)
  const [pdfData, setPdfData] = useState(null)
  const [planData, setPlanData] = useState(null)
  const [results, setResults] = useState(null)

  const doneSteps = new Set()
  if (pdfData) { doneSteps.add(0); doneSteps.add(1) }
  if (planData) doneSteps.add(2)
  if (results) { doneSteps.add(3); doneSteps.add(4) }

  function reset() {
    setStep(0); setPdfData(null); setPlanData(null); setResults(null)
  }

  return (
    <>
      <style>{styles}</style>
      <main className="app">
        <header className="sf-header">
          <div className="sf-brand">
            <div className="sf-logo">✦</div>
            <div>
              <div className="sf-title">StudyFlow AI</div>
              <div className="sf-subtitle">Turn your study material into a focused learning flow</div>
            </div>
          </div>
          <div className="sf-pill">AI Study Assistant</div>
        </header>

        <nav className="sf-steps">
          {STEPS.map((s, i) => {
            const available = i === 0 || doneSteps.has(i)
            return (
              <button
                key={s.id}
                className={`sf-step${step === i ? ' active' : ''}${doneSteps.has(i) && step !== i ? ' done' : ''}`}
                disabled={!available}
                onClick={() => available && setStep(i)}
              >
                <span className="sf-step-num">{doneSteps.has(i) && step !== i ? '✓' : i + 1}</span>
                <span>{s.short}</span>
              </button>
            )
          })}
        </nav>
        <div className="sf-progress"><div style={{ width: `${(step / (STEPS.length - 1)) * 100}%` }} /></div>

        {step === 0 && <UploadStep onDone={data => { setPdfData(data); setStep(1) }} />}
        {step === 1 && pdfData && <TopicsStep data={pdfData} onNext={() => setStep(2)} />}
        {step === 2 && <PlanStep topics={pdfData?.detected_topics || []} onDone={setPlanData} onNext={() => setStep(3)} />}
        {step === 3 && pdfData && <QuizStep text={pdfData.full_text} onDone={res => { setResults(res); setStep(4) }} />}
        {step === 4 && <ResultsStep results={results} detectedTopics={pdfData?.detected_topics || []} onReset={reset} />}

        <div className="sf-footer">StudyFlow AI · Upload → Extract → Plan → Quiz → Improve</div>
      </main>
    </>
  )
}

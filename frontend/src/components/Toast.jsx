import React from 'react';
import { CheckCircle, Info, AlertCircle, X } from 'lucide-react';

export default function Toast({ toasts, onDismiss }) {
  if (!toasts || toasts.length === 0) return null;

  return (
    <div className="toast-container" aria-live="polite">
      {toasts.map((toast) => (
        <div key={toast.id} className={`toast ${toast.type || 'info'}`}>
          {toast.type === 'success' && <CheckCircle size={18} color="#10b981" />}
          {toast.type === 'warning' && <AlertCircle size={18} color="#f59e0b" />}
          {toast.type === 'info' && <Info size={18} color="#818cf8" />}

          <span>{toast.message}</span>

          <button
            onClick={() => onDismiss(toast.id)}
            style={{
              background: 'transparent',
              border: 'none',
              color: 'var(--text-dim)',
              cursor: 'pointer',
              marginLeft: '8px',
              display: 'flex',
              alignItems: 'center'
            }}
            aria-label="Dismiss notification"
          >
            <X size={14} />
          </button>
        </div>
      ))}
    </div>
  );
}

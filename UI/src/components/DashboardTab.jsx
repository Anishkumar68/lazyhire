import React, { useState, useEffect } from 'react';
import { api } from '../api';
import { 
  Briefcase, 
  CheckCircle, 
  Clock, 
  Send, 
  Cpu, 
  DollarSign, 
  Play, 
  RefreshCw, 
  FileSpreadsheet, 
  AlertTriangle 
} from 'lucide-react';

export default function DashboardTab({ onNavigate }) {
  const [stats, setStats] = useState(null);
  const [tokens, setTokens] = useState([]);
  const [health, setHealth] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [healthRes, statsRes, tokenRes] = await Promise.allSettled([
        api.getHealth(),
        api.getDashboardStats(),
        api.getTokenTelemetry(),
      ]);

      if (healthRes.status === 'fulfilled') setHealth(healthRes.value);
      if (statsRes.status === 'fulfilled' && statsRes.value) setStats(statsRes.value.data || statsRes.value);
      if (tokenRes.status === 'fulfilled' && tokenRes.value) setTokens(tokenRes.value.data || []);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
        <div>
          <h2 style={{ fontSize: '1.5rem', fontWeight: 700 }}>LazyHire Control Center</h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.88rem' }}>
            Unified automation workspace for intelligent intake, tailoring, and live stealth application.
          </p>
        </div>
        <div style={{ display: 'flex', gap: '0.75rem' }}>
          <button className="btn btn-outline" onClick={loadData}>
            <RefreshCw size={15} className={loading ? 'animate-spin' : ''} /> Refresh
          </button>
          <a href={api.getExportExcelUrl()} target="_blank" rel="noreferrer" className="btn btn-outline">
            <FileSpreadsheet size={15} /> Export Excel
          </a>
        </div>
      </div>

      {error && (
        <div style={{ padding: '1rem', background: 'rgba(244, 63, 94, 0.1)', border: '1px solid var(--accent-rose)', borderRadius: 'var(--radius-sm)', marginBottom: '1.5rem', color: 'var(--accent-rose)', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <AlertTriangle size={18} /> Backend Notice: {error}
        </div>
      )}

      {/* Stats Grid */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-info">
            <span>Discovered Jobs</span>
            <h3>{stats?.total_jobs_discovered ?? 0}</h3>
          </div>
          <div className="stat-icon" style={{ background: 'rgba(59, 130, 246, 0.15)', color: 'var(--accent-blue)' }}>
            <Briefcase size={22} />
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-info">
            <span>Semantic Matched</span>
            <h3>{stats?.total_matched_jobs ?? 0}</h3>
          </div>
          <div className="stat-icon" style={{ background: 'rgba(99, 102, 241, 0.15)', color: 'var(--accent-indigo)' }}>
            <CheckCircle size={22} />
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-info">
            <span>HITL Review Queue</span>
            <h3>{stats?.total_pending_review ?? 0}</h3>
          </div>
          <div className="stat-icon" style={{ background: 'rgba(245, 158, 11, 0.15)', color: 'var(--accent-amber)' }}>
            <Clock size={22} />
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-info">
            <span>Applications Submitted</span>
            <h3>{stats?.total_applied ?? 0}</h3>
          </div>
          <div className="stat-icon" style={{ background: 'rgba(16, 185, 129, 0.15)', color: 'var(--accent-emerald)' }}>
            <Send size={22} />
          </div>
        </div>
      </div>

      {/* Quick Launch Cards */}
      <div className="grid-2">
        <div className="card">
          <div className="card-header">
            <span className="card-title"><Play size={18} color="var(--accent-indigo)" /> Quick Operations</span>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            <button className="btn btn-outline" style={{ justifyContent: 'space-between' }} onClick={() => onNavigate('jobs')}>
              <span>🔍 Discover New Postings</span>
              <span style={{ color: 'var(--text-muted)', fontSize: '0.75rem' }}>Scrape LinkedIn & ATS</span>
            </button>
            <button className="btn btn-outline" style={{ justifyContent: 'space-between' }} onClick={() => onNavigate('review')}>
              <span>📋 Inspect Review Queue</span>
              <span style={{ color: 'var(--text-muted)', fontSize: '0.75rem' }}>Approve / Reject Tailored Materials</span>
            </button>
            <button className="btn btn-primary" style={{ justifyContent: 'space-between' }} onClick={() => onNavigate('execution')}>
              <span>🚀 Launch Stealth Runner</span>
              <span style={{ fontSize: '0.75rem' }}>Live Browser Automation</span>
            </button>
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <span className="card-title"><Cpu size={18} color="var(--accent-purple)" /> LLM & Cost Telemetry</span>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1rem', padding: '0.75rem', background: 'var(--bg-primary)', borderRadius: 'var(--radius-sm)' }}>
            <div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Estimated Spend</div>
              <div style={{ fontSize: '1.25rem', fontWeight: 700, color: 'var(--accent-emerald)' }}>
                ${stats?.total_estimated_cost_usd?.toFixed(3) || '0.000'}
              </div>
            </div>
            <div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Total Tokens Used</div>
              <div style={{ fontSize: '1.25rem', fontWeight: 700, color: 'var(--text-primary)' }}>
                {stats?.total_tokens_used?.toLocaleString() || '0'}
              </div>
            </div>
          </div>
          <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
            Multi-LLM layer active with prompt caching, token budgets, and automatic rate limiting.
          </p>
        </div>
      </div>
    </div>
  );
}

import React, { useState, useEffect } from 'react';
import { api } from '../api';
import { 
  Cpu, 
  Layers, 
  Trash2, 
  FileSpreadsheet, 
  FileText, 
  RefreshCw, 
  CheckCircle, 
  AlertTriangle 
} from 'lucide-react';

export default function SettingsTab() {
  const [providerName, setProviderName] = useState('openai');
  const [testPrompt, setTestPrompt] = useState('Hello, verify API connection');
  const [testResult, setTestResult] = useState(null);
  const [testing, setTesting] = useState(false);
  const [message, setMessage] = useState(null);

  const handleTestProvider = async (e) => {
    e.preventDefault();
    setTesting(true);
    setTestResult(null);
    setMessage(null);
    try {
      const res = await api.testProvider(providerName, testPrompt);
      setTestResult(res.data || res);
      setMessage({ type: 'success', text: `LLM Provider ${providerName.toUpperCase()} responded successfully.` });
    } catch (err) {
      setMessage({ type: 'error', text: err.message });
    } finally {
      setTesting(false);
    }
  };

  const handleCleanup = async () => {
    setMessage(null);
    try {
      await api.cleanupTasks();
      setMessage({ type: 'success', text: 'Maintenance task executed: stale screenshots and temporary PDFs purged.' });
    } catch (err) {
      setMessage({ type: 'error', text: err.message });
    }
  };

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <h2 style={{ fontSize: '1.5rem', fontWeight: 700 }}>System Configuration &amp; Providers</h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.88rem' }}>
            Multi-LLM layer connectivity, background Celery queue monitoring, and reporting exports.
          </p>
        </div>
      </div>

      {message && (
        <div
          style={{
            padding: '0.85rem 1.25rem',
            borderRadius: 'var(--radius-sm)',
            marginBottom: '1.25rem',
            background: message.type === 'success' ? 'rgba(16, 185, 129, 0.15)' : 'rgba(244, 63, 94, 0.15)',
            border: `1px solid ${message.type === 'success' ? 'var(--accent-emerald)' : 'var(--accent-rose)'}`,
            color: message.type === 'success' ? 'var(--accent-emerald)' : 'var(--accent-rose)',
            fontSize: '0.88rem',
          }}
        >
          {message.text}
        </div>
      )}

      <div className="grid-2">
        {/* LLM Provider Tester */}
        <div className="card">
          <div className="card-header">
            <span className="card-title"><Cpu size={18} color="var(--accent-indigo)" /> Multi-LLM Provider Engine</span>
          </div>

          <form onSubmit={handleTestProvider}>
            <div className="form-group">
              <label>Select Active Provider Adapter</label>
              <select className="form-select" value={providerName} onChange={(e) => setProviderName(e.target.value)}>
                <option value="openai">OpenAI (GPT-4o, o3-mini)</option>
                <option value="anthropic">Anthropic Claude (3.5 Sonnet)</option>
                <option value="gemini">Google Gemini (Flash, Pro)</option>
                <option value="deepseek">DeepSeek (V3, R1)</option>
                <option value="ollama">Ollama Local (Llama 3, Qwen, DeepSeek-R1)</option>
                <option value="openrouter">OpenRouter (Unified Gateway)</option>
              </select>
            </div>

            <div className="form-group">
              <label>Prompt Verification Test</label>
              <input
                type="text"
                className="form-input"
                value={testPrompt}
                onChange={(e) => setTestPrompt(e.target.value)}
              />
            </div>

            <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '1rem' }}>
              <button type="submit" className="btn btn-primary" disabled={testing}>
                <RefreshCw size={14} className={testing ? 'animate-spin' : ''} /> {testing ? 'Testing...' : 'Test Connection'}
              </button>
            </div>
          </form>

          {testResult && (
            <div style={{ marginTop: '1rem', padding: '0.85rem', background: 'var(--bg-primary)', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-color)', fontSize: '0.82rem' }}>
              <div style={{ color: 'var(--accent-emerald)', fontWeight: 600, marginBottom: '4px' }}>✓ Connection Verified</div>
              <div style={{ color: 'var(--text-secondary)' }}>{testResult.sample_response || 'Model operational.'}</div>
            </div>
          )}
        </div>

        {/* Celery Queues & Maintenance */}
        <div className="card">
          <div className="card-header">
            <span className="card-title"><Layers size={18} color="var(--accent-emerald)" /> Worker Queues &amp; DLQ</span>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.6rem', marginBottom: '1.25rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '0.6rem 0.85rem', background: 'var(--bg-primary)', borderRadius: 'var(--radius-sm)', fontSize: '0.82rem' }}>
              <span><code>search</code> queue (Scraper crawlers)</span>
              <span className="badge badge-approved">Active</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '0.6rem 0.85rem', background: 'var(--bg-primary)', borderRadius: 'var(--radius-sm)', fontSize: '0.82rem' }}>
              <span><code>materials</code> queue (Resume IR &amp; Tectonic)</span>
              <span className="badge badge-approved">Active</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '0.6rem 0.85rem', background: 'var(--bg-primary)', borderRadius: 'var(--radius-sm)', fontSize: '0.82rem' }}>
              <span><code>application</code> queue (Browser runners)</span>
              <span className="badge badge-approved">Active</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '0.6rem 0.85rem', background: 'var(--bg-primary)', borderRadius: 'var(--radius-sm)', fontSize: '0.82rem' }}>
              <span><code>maintenance</code> &amp; DLQ (Quarantine)</span>
              <span className="badge badge-pending">0 Stuck Tasks</span>
            </div>
          </div>

          <button className="btn btn-outline btn-sm" style={{ width: '100%', justifyContent: 'center' }} onClick={handleCleanup}>
            <Trash2 size={14} /> Run Temporary File &amp; Screenshot Cleanup
          </button>
        </div>
      </div>

      {/* Export Reports Card */}
      <div className="card">
        <div className="card-header">
          <span className="card-title"><FileSpreadsheet size={18} color="var(--accent-purple)" /> Spreadsheet &amp; Telemetry Exports</span>
        </div>
        <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '1.25rem' }}>
          Directly export complete application outcomes, timestamps, skipped listings, and interview logs into formatted workbooks (from Auto_job_applier_linkedIn's spreadsheet feature).
        </p>
        <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
          <a href={api.getExportExcelUrl()} target="_blank" rel="noreferrer" className="btn btn-outline">
            <FileSpreadsheet size={16} /> Export to Excel (.xlsx)
          </a>
          <a href={api.getExportCsvUrl()} target="_blank" rel="noreferrer" className="btn btn-outline">
            <FileText size={16} /> Export to CSV (.csv)
          </a>
        </div>
      </div>
    </div>
  );
}

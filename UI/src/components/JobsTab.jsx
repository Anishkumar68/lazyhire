import React, { useState, useEffect } from 'react';
import { api } from '../api';
import { 
  Search, 
  Plus, 
  ExternalLink, 
  Sparkles, 
  Filter, 
  DownloadCloud, 
  CheckCircle2, 
  Clock, 
  AlertCircle 
} from 'lucide-react';

export default function JobsTab() {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [platform, setPlatform] = useState('');
  const [easyApplyOnly, setEasyApplyOnly] = useState(false);
  const [matchStatus, setMatchStatus] = useState('');
  const [message, setMessage] = useState(null);

  // Scrape / Discover modal state
  const [showScrapeModal, setShowScrapeModal] = useState(false);
  const [scrapeKeywords, setScrapeKeywords] = useState('Software Engineer, Full Stack');
  const [scrapeLocation, setScrapeLocation] = useState('United States');
  const [scrapePlatform, setScrapePlatform] = useState('linkedin');
  const [scrapeLoading, setScrapeLoading] = useState(false);

  // Ingest URL state
  const [ingestUrl, setIngestUrl] = useState('');
  const [ingestLoading, setIngestLoading] = useState(false);

  const fetchJobs = async () => {
    setLoading(true);
    try {
      const params = {};
      if (platform) params.platform = platform;
      if (easyApplyOnly) params.is_easy_apply_only = true;
      if (matchStatus) params.match_status = matchStatus;

      const res = await api.getJobs(params);
      setJobs(res.data || []);
    } catch (err) {
      console.error('Failed to load jobs:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchJobs();
  }, [platform, easyApplyOnly, matchStatus]);

  const handleScrape = async (e) => {
    e.preventDefault();
    setScrapeLoading(true);
    setMessage(null);
    try {
      const keywordsArray = scrapeKeywords.split(',').map((s) => s.trim()).filter(Boolean);
      await api.scrapeJobs({
        platform: scrapePlatform,
        keywords: keywordsArray,
        location: scrapeLocation,
        easy_apply_only: true,
      });
      setMessage({ type: 'success', text: 'Job scraper task enqueued successfully.' });
      setShowScrapeModal(false);
      fetchJobs();
    } catch (err) {
      setMessage({ type: 'error', text: err.message });
    } finally {
      setScrapeLoading(false);
    }
  };

  const handleIngest = async (e) => {
    e.preventDefault();
    if (!ingestUrl.trim()) return;
    setIngestLoading(true);
    setMessage(null);
    try {
      await api.ingestJob(ingestUrl);
      setMessage({ type: 'success', text: 'Job URL normalized and ingested.' });
      setIngestUrl('');
      fetchJobs();
    } catch (err) {
      setMessage({ type: 'error', text: err.message });
    } finally {
      setIngestLoading(false);
    }
  };

  const handleScoreAll = async () => {
    setMessage(null);
    try {
      await api.matchJobs();
      setMessage({ type: 'success', text: 'Semantic matching triggered for pending jobs.' });
      fetchJobs();
    } catch (err) {
      setMessage({ type: 'error', text: err.message });
    }
  };

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <h2 style={{ fontSize: '1.5rem', fontWeight: 700 }}>Job Discovery & Intake</h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.88rem' }}>
            Index, deduplicate, and rank jobs from LinkedIn and top ATS platforms (Greenhouse, Lever, Ashby, Workday).
          </p>
        </div>
        <div style={{ display: 'flex', gap: '0.75rem' }}>
          <button className="btn btn-outline" onClick={handleScoreAll}>
            <Sparkles size={16} color="var(--accent-indigo)" /> Run Fit Matcher
          </button>
          <button className="btn btn-primary" onClick={() => setShowScrapeModal(true)}>
            <DownloadCloud size={16} /> Scrape New Jobs
          </button>
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

      {/* URL Quick Ingest Bar */}
      <div className="card" style={{ padding: '1rem 1.25rem' }}>
        <form onSubmit={handleIngest} style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
          <input
            type="url"
            className="form-input"
            placeholder="Paste direct job URL (Greenhouse, Lever, Ashby, LinkedIn Easy Apply)..."
            value={ingestUrl}
            onChange={(e) => setIngestUrl(e.target.value)}
            style={{ flex: 1 }}
          />
          <button type="submit" className="btn btn-primary" disabled={ingestLoading || !ingestUrl.trim()}>
            {ingestLoading ? 'Ingesting...' : 'Ingest Posting'}
          </button>
        </form>
      </div>

      {/* Filters Bar */}
      <div className="card" style={{ padding: '0.85rem 1.25rem', display: 'flex', gap: '1rem', flexWrap: 'wrap', alignItems: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
          <Filter size={15} /> Filters:
        </div>
        <select className="form-select" style={{ width: 'auto' }} value={platform} onChange={(e) => setPlatform(e.target.value)}>
          <option value="">All Platforms</option>
          <option value="linkedin">LinkedIn</option>
          <option value="greenhouse">Greenhouse</option>
          <option value="lever">Lever</option>
          <option value="ashby">Ashby</option>
          <option value="workday">Workday</option>
        </select>

        <select className="form-select" style={{ width: 'auto' }} value={matchStatus} onChange={(e) => setMatchStatus(e.target.value)}>
          <option value="">All Match Statuses</option>
          <option value="matched">Matched (Fit Score &gt; 0.5)</option>
          <option value="pending">Pending Scoring</option>
          <option value="rejected">Hard Filter Excluded</option>
        </select>

        <label style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.85rem', cursor: 'pointer' }}>
          <input
            type="checkbox"
            checked={easyApplyOnly}
            onChange={(e) => setEasyApplyOnly(e.target.checked)}
          />
          Easy Apply / Direct Submit only
        </label>
      </div>

      {/* Jobs Table */}
      <div className="card" style={{ padding: 0 }}>
        <div className="table-responsive">
          <table className="data-table">
            <thead>
              <tr>
                <th>Job Title & Company</th>
                <th>Platform</th>
                <th>Location</th>
                <th>Fit Score</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr>
                  <td colSpan="6" style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-muted)' }}>
                    Loading job listings...
                  </td>
                </tr>
              ) : jobs.length === 0 ? (
                <tr>
                  <td colSpan="6" style={{ textAlign: 'center', padding: '2.5rem', color: 'var(--text-muted)' }}>
                    No job postings found matching criteria. Use "Scrape New Jobs" or ingest a URL.
                  </td>
                </tr>
              ) : (
                jobs.map((job) => (
                  <tr key={job.id}>
                    <td>
                      <div style={{ fontWeight: 600 }}>{job.title}</div>
                      <div style={{ color: 'var(--text-secondary)', fontSize: '0.8rem' }}>{job.company}</div>
                    </td>
                    <td>
                      <span className="badge" style={{ background: 'var(--bg-tertiary)' }}>
                        {job.platform}
                      </span>
                    </td>
                    <td>{job.location || 'Remote / Unspecified'}</td>
                    <td>
                      {job.fit_score != null ? (
                        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                          <div style={{
                            width: '40px',
                            height: '6px',
                            background: 'var(--bg-tertiary)',
                            borderRadius: '3px',
                            overflow: 'hidden',
                          }}>
                            <div style={{
                              width: `${Math.round(job.fit_score * 100)}%`,
                              height: '100%',
                              background: job.fit_score > 0.7 ? 'var(--accent-emerald)' : job.fit_score > 0.4 ? 'var(--accent-amber)' : 'var(--accent-rose)'
                            }} />
                          </div>
                          <span style={{ fontSize: '0.8rem', fontWeight: 600 }}>{Math.round(job.fit_score * 100)}%</span>
                        </div>
                      ) : (
                        <span style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>Unscored</span>
                      )}
                    </td>
                    <td>
                      <span className={`badge badge-${job.match_status || 'pending'}`}>
                        {job.match_status || 'pending'}
                      </span>
                    </td>
                    <td>
                      <a href={job.url} target="_blank" rel="noreferrer" className="btn btn-outline btn-sm" title="View Source Job">
                        <ExternalLink size={13} /> View
                      </a>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Scrape Modal */}
      {showScrapeModal && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'rgba(0, 0, 0, 0.7)',
          backdropFilter: 'blur(4px)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 100,
        }}>
          <div className="card" style={{ width: '480px', maxWidth: '90%', margin: 0 }}>
            <div className="card-header">
              <span className="card-title">🔍 Trigger Job Discovery Scraper</span>
              <button className="btn btn-outline btn-sm" onClick={() => setShowScrapeModal(false)}>✕</button>
            </div>
            <form onSubmit={handleScrape}>
              <div className="form-group">
                <label>Platform</label>
                <select className="form-select" value={scrapePlatform} onChange={(e) => setScrapePlatform(e.target.value)}>
                  <option value="linkedin">LinkedIn (with Easy Apply toggle)</option>
                  <option value="greenhouse">Greenhouse Boards</option>
                  <option value="lever">Lever Job Listings</option>
                  <option value="ashby">Ashby HQ</option>
                </select>
              </div>
              <div className="form-group">
                <label>Target Keywords (comma-separated)</label>
                <input
                  type="text"
                  className="form-input"
                  value={scrapeKeywords}
                  onChange={(e) => setScrapeKeywords(e.target.value)}
                  placeholder="e.g. Python Developer, FastAPI, Backend"
                  required
                />
              </div>
              <div className="form-group">
                <label>Location</label>
                <input
                  type="text"
                  className="form-input"
                  value={scrapeLocation}
                  onChange={(e) => setScrapeLocation(e.target.value)}
                  placeholder="e.g. Remote, San Francisco, New York"
                />
              </div>
              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem', marginTop: '1.5rem' }}>
                <button type="button" className="btn btn-outline" onClick={() => setShowScrapeModal(false)}>
                  Cancel
                </button>
                <button type="submit" className="btn btn-primary" disabled={scrapeLoading}>
                  {scrapeLoading ? 'Launching...' : 'Start Scrape Task'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

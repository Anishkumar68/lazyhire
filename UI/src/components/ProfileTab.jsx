import React, { useState, useEffect } from 'react';
import { api } from '../api';
import { 
  User, 
  BookOpen, 
  HelpCircle, 
  Plus, 
  Save, 
  Upload, 
  CheckCircle, 
  AlertCircle 
} from 'lucide-react';

export default function ProfileTab() {
  const [profile, setProfile] = useState({
    first_name: '',
    last_name: '',
    email: '',
    phone: '',
    location: '',
    summary: '',
    skills: [],
    total_work_experience: 5,
    work_authorization: 'Yes',
    requires_sponsorship: 'No',
    desired_salary: '140,000',
    notice_period: '14 days',
    keywords: [],
  });
  const [stories, setStories] = useState([]);
  const [qaEntries, setQaEntries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState(null);

  // New Story Form state
  const [showStoryModal, setShowStoryModal] = useState(false);
  const [storyTitle, setStoryTitle] = useState('');
  const [storySituation, setStorySituation] = useState('');
  const [storyTask, setStoryTask] = useState('');
  const [storyAction, setStoryAction] = useState('');
  const [storyResult, setStoryResult] = useState('');

  // New QA Entry Form state
  const [showQAModal, setShowQAModal] = useState(false);
  const [qaKey, setQaKey] = useState('');
  const [qaQuestion, setQaQuestion] = useState('');
  const [qaAnswer, setQaAnswer] = useState('');

  const loadProfileData = async () => {
    setLoading(true);
    try {
      const activeRes = await api.getActiveProfile();
      if (activeRes && activeRes.data) {
        setProfile(activeRes.data);
      }
      const qaRes = await api.getQABank();
      if (qaRes && qaRes.data) {
        setQaEntries(qaRes.data);
      }
    } catch (err) {
      console.warn('Using default profile form state:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadProfileData();
  }, []);

  const handleSaveProfile = async (e) => {
    e.preventDefault();
    setSaving(true);
    setMessage(null);
    try {
      if (profile.id) {
        await api.updateProfile(profile.id, profile);
      } else {
        const res = await api.createProfile(profile);
        if (res && res.data) setProfile(res.data);
      }
      setMessage({ type: 'success', text: 'Candidate Profile & Memory Cache refreshed successfully.' });
    } catch (err) {
      setMessage({ type: 'error', text: err.message });
    } finally {
      setSaving(false);
    }
  };

  const handleAddStory = async (e) => {
    e.preventDefault();
    try {
      const candidateId = profile.id || 1;
      await api.createStory(candidateId, {
        title: storyTitle,
        situation: storySituation,
        task: storyTask,
        action: storyAction,
        result: storyResult,
      });
      setStories((prev) => [
        ...prev,
        {
          id: Date.now(),
          title: storyTitle,
          situation: storySituation,
          result: storyResult,
        },
      ]);
      setShowStoryModal(false);
      setStoryTitle('');
      setStorySituation('');
      setStoryTask('');
      setStoryAction('');
      setStoryResult('');
      setMessage({ type: 'success', text: 'Story added to candidate memory bank.' });
    } catch (err) {
      setMessage({ type: 'error', text: err.message });
    }
  };

  const handleAddQA = async (e) => {
    e.preventDefault();
    try {
      await api.addQAEntry({
        question_key: qaKey,
        question_text: qaQuestion,
        answer_text: qaAnswer,
      });
      setQaEntries((prev) => [
        ...prev,
        { id: Date.now(), question_key: qaKey, question_text: qaQuestion, answer_text: qaAnswer },
      ]);
      setShowQAModal(false);
      setQaKey('');
      setQaQuestion('');
      setQaAnswer('');
      setMessage({ type: 'success', text: 'QA Entry saved to Redis & Memory Bank.' });
    } catch (err) {
      setMessage({ type: 'error', text: err.message });
    }
  };

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <h2 style={{ fontSize: '1.5rem', fontWeight: 700 }}>Applicant Memory Bank & Profile</h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.88rem' }}>
            Structured ground facts, story banks, and QA pairs used by the IR Tailoring Engine and Dynamic QA Solver.
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

      {/* Main Profile Form */}
      <div className="card">
        <div className="card-header">
          <span className="card-title"><User size={18} color="var(--accent-indigo)" /> Core Applicant Information</span>
        </div>
        <form onSubmit={handleSaveProfile}>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '1rem' }}>
            <div className="form-group">
              <label>First Name</label>
              <input
                type="text"
                className="form-input"
                value={profile.first_name || ''}
                onChange={(e) => setProfile({ ...profile, first_name: e.target.value })}
                required
              />
            </div>
            <div className="form-group">
              <label>Last Name</label>
              <input
                type="text"
                className="form-input"
                value={profile.last_name || ''}
                onChange={(e) => setProfile({ ...profile, last_name: e.target.value })}
                required
              />
            </div>
            <div className="form-group">
              <label>Email Address</label>
              <input
                type="email"
                className="form-input"
                value={profile.email || ''}
                onChange={(e) => setProfile({ ...profile, email: e.target.value })}
                required
              />
            </div>
            <div className="form-group">
              <label>Phone Number</label>
              <input
                type="text"
                className="form-input"
                value={profile.phone || ''}
                onChange={(e) => setProfile({ ...profile, phone: e.target.value })}
              />
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '1rem' }}>
            <div className="form-group">
              <label>Location (City, State / Country)</label>
              <input
                type="text"
                className="form-input"
                value={profile.location || ''}
                onChange={(e) => setProfile({ ...profile, location: e.target.value })}
              />
            </div>
            <div className="form-group">
              <label>Desired Annual Salary ($)</label>
              <input
                type="text"
                className="form-input"
                value={profile.desired_salary || ''}
                onChange={(e) => setProfile({ ...profile, desired_salary: e.target.value })}
              />
            </div>
            <div className="form-group">
              <label>Notice Period</label>
              <input
                type="text"
                className="form-input"
                value={profile.notice_period || ''}
                onChange={(e) => setProfile({ ...profile, notice_period: e.target.value })}
              />
            </div>
            <div className="form-group">
              <label>Requires Visa Sponsorship?</label>
              <select
                className="form-select"
                value={profile.requires_sponsorship || 'No'}
                onChange={(e) => setProfile({ ...profile, requires_sponsorship: e.target.value })}
              >
                <option value="No">No</option>
                <option value="Yes">Yes</option>
              </select>
            </div>
          </div>

          <div className="form-group">
            <label>Professional Summary &amp; Experience Highlights</label>
            <textarea
              className="form-textarea"
              rows="3"
              value={profile.summary || ''}
              onChange={(e) => setProfile({ ...profile, summary: e.target.value })}
              placeholder="Overview used to ground LLM-generated tailored cover letters..."
            />
          </div>

          <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '1rem' }}>
            <button type="submit" className="btn btn-primary" disabled={saving}>
              <Save size={15} /> {saving ? 'Saving...' : 'Save & Refresh Cache'}
            </button>
          </div>
        </form>
      </div>

      {/* Story Bank & QA Bank Grid */}
      <div className="grid-2">
        {/* Story Bank Card */}
        <div className="card">
          <div className="card-header">
            <span className="card-title"><BookOpen size={18} color="var(--accent-purple)" /> Story Bank (STAR Facts)</span>
            <button className="btn btn-outline btn-sm" onClick={() => setShowStoryModal(true)}>
              <Plus size={13} /> Add Story
            </button>
          </div>
          <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '1rem' }}>
            Verified candidate accomplishments used by the IR Tailoring Engine to prevent fact-drift or hallucination.
          </p>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.6rem' }}>
            {stories.length === 0 ? (
              <div style={{ padding: '1rem', background: 'var(--bg-primary)', borderRadius: 'var(--radius-sm)', color: 'var(--text-muted)', fontSize: '0.85rem' }}>
                No stories added yet. Click "+ Add Story" to record real career projects.
              </div>
            ) : (
              stories.map((s) => (
                <div key={s.id} style={{ padding: '0.75rem', background: 'var(--bg-primary)', borderRadius: 'var(--radius-sm)' }}>
                  <div style={{ fontWeight: 600, fontSize: '0.88rem' }}>{s.title}</div>
                  <div style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', marginTop: '4px' }}>
                    {s.situation || s.result}
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Dynamic QA Bank Card */}
        <div className="card">
          <div className="card-header">
            <span className="card-title"><HelpCircle size={18} color="var(--accent-amber)" /> Dynamic QA Bank</span>
            <button className="btn btn-outline btn-sm" onClick={() => setShowQAModal(true)}>
              <Plus size={13} /> Add QA
            </button>
          </div>
          <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '1rem' }}>
            Pre-configured answers for common application questions (Tier 2 in the dynamic QA solver).
          </p>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.6rem' }}>
            {qaEntries.length === 0 ? (
              <div style={{ padding: '1rem', background: 'var(--bg-primary)', borderRadius: 'var(--radius-sm)', color: 'var(--text-muted)', fontSize: '0.85rem' }}>
                No custom QA entries yet. Common answers (salary, notice period) are loaded from Profile.
              </div>
            ) : (
              qaEntries.map((qa) => (
                <div key={qa.id} style={{ padding: '0.75rem', background: 'var(--bg-primary)', borderRadius: 'var(--radius-sm)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div>
                    <div style={{ fontWeight: 600, fontSize: '0.85rem' }}>{qa.question_key || qa.question_text}</div>
                    <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>{qa.question_text}</div>
                  </div>
                  <div style={{ fontWeight: 600, color: 'var(--accent-emerald)', fontSize: '0.88rem' }}>
                    {qa.answer_text}
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>

      {/* Add Story Modal */}
      {showStoryModal && (
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
          <div className="card" style={{ width: '500px', maxWidth: '90%', margin: 0 }}>
            <div className="card-header">
              <span className="card-title">Add Story to Memory Bank</span>
              <button className="btn btn-outline btn-sm" onClick={() => setShowStoryModal(false)}>✕</button>
            </div>
            <form onSubmit={handleAddStory}>
              <div className="form-group">
                <label>Story Title / Project Name</label>
                <input
                  type="text"
                  className="form-input"
                  value={storyTitle}
                  onChange={(e) => setStoryTitle(e.target.value)}
                  placeholder="e.g. Scaled PostgreSQL & Redis architecture"
                  required
                />
              </div>
              <div className="form-group">
                <label>Situation &amp; Task</label>
                <textarea
                  className="form-textarea"
                  rows="2"
                  value={storySituation}
                  onChange={(e) => setStorySituation(e.target.value)}
                  placeholder="What was the challenge or background context?"
                />
              </div>
              <div className="form-group">
                <label>Action &amp; Result (Quantifiable outcome)</label>
                <textarea
                  className="form-textarea"
                  rows="2"
                  value={storyResult}
                  onChange={(e) => setStoryResult(e.target.value)}
                  placeholder="What specific actions were taken and measurable results achieved?"
                />
              </div>
              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem', marginTop: '1rem' }}>
                <button type="button" className="btn btn-outline" onClick={() => setShowStoryModal(false)}>Cancel</button>
                <button type="submit" className="btn btn-primary">Save Story</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Add QA Modal */}
      {showQAModal && (
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
              <span className="card-title">Add Custom QA Entry</span>
              <button className="btn btn-outline btn-sm" onClick={() => setShowQAModal(false)}>✕</button>
            </div>
            <form onSubmit={handleAddQA}>
              <div className="form-group">
                <label>Question Key / Topic</label>
                <input
                  type="text"
                  className="form-input"
                  value={qaKey}
                  onChange={(e) => setQaKey(e.target.value)}
                  placeholder="e.g. leadership_experience, relocation"
                  required
                />
              </div>
              <div className="form-group">
                <label>Question Text (as asked by employer)</label>
                <input
                  type="text"
                  className="form-input"
                  value={qaQuestion}
                  onChange={(e) => setQaQuestion(e.target.value)}
                  placeholder="e.g. Are you willing to relocate to San Francisco?"
                  required
                />
              </div>
              <div className="form-group">
                <label>Candidate Answer</label>
                <input
                  type="text"
                  className="form-input"
                  value={qaAnswer}
                  onChange={(e) => setQaAnswer(e.target.value)}
                  placeholder="e.g. Yes, willing to relocate for full-time role"
                  required
                />
              </div>
              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem', marginTop: '1rem' }}>
                <button type="button" className="btn btn-outline" onClick={() => setShowQAModal(false)}>Cancel</button>
                <button type="submit" className="btn btn-primary">Save QA</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

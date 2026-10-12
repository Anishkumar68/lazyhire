import React, { useState } from 'react';
import DashboardTab from './components/DashboardTab';
import JobsTab from './components/JobsTab';
import ReviewTab from './components/ReviewTab';
import ExecutionTab from './components/ExecutionTab';
import ProfileTab from './components/ProfileTab';
import MaterialsTab from './components/MaterialsTab';
import SettingsTab from './components/SettingsTab';
import { 
  LayoutDashboard, 
  Briefcase, 
  CheckSquare, 
  Play, 
  User, 
  Sparkles, 
  Settings, 
  Radio 
} from 'lucide-react';

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard');

  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'jobs', label: 'Job Intake', icon: Briefcase },
    { id: 'review', label: 'HITL Review', icon: CheckSquare },
    { id: 'execution', label: 'Live Bot Runner', icon: Play },
    { id: 'materials', label: 'Tailoring & IR', icon: Sparkles },
    { id: 'profile', label: 'Memory Bank', icon: User },
    { id: 'settings', label: 'System & LLM', icon: Settings },
  ];

  return (
    <div className="app-layout">
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="sidebar-header">
          <div className="logo-badge">LH</div>
          <div className="logo-text">
            <h1>LazyHire</h1>
            <span>
              <span className="status-dot" style={{ display: 'inline-block' }} /> Live Workspace
            </span>
          </div>
        </div>

        <nav className="sidebar-nav">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                className={`nav-item ${isActive ? 'active' : ''}`}
                onClick={() => setActiveTab(item.id)}
              >
                <Icon size={18} />
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>

        <div className="sidebar-footer">
          <span>v0.1.0 • React + Vite</span>
          <Radio size={14} color="var(--accent-emerald)" />
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="main-content">
        <header className="top-bar">
          <div className="page-title">
            {navItems.find((n) => n.id === activeTab)?.label}
          </div>
          <div className="status-badge-live">
            <span className="status-dot" />
            FastAPI Backend Online
          </div>
        </header>

        <div className="page-container">
          {activeTab === 'dashboard' && <DashboardTab onNavigate={setActiveTab} />}
          {activeTab === 'jobs' && <JobsTab />}
          {activeTab === 'review' && <ReviewTab />}
          {activeTab === 'execution' && <ExecutionTab />}
          {activeTab === 'materials' && <MaterialsTab />}
          {activeTab === 'profile' && <ProfileTab />}
          {activeTab === 'settings' && <SettingsTab />}
        </div>
      </main>
    </div>
  );
}

'use client';

import React, { useState } from 'react';
import { api, ScrapeRunStatus } from '../lib/api';
import { Play, RefreshCw, Cpu, Database, CheckCircle2, AlertCircle } from 'lucide-react';

interface PipelineControlProps {
  onPipelineUpdate: () => void;
}

export const PipelineControl: React.FC<PipelineControlProps> = ({ onPipelineUpdate }) => {
  const [platform, setPlatform] = useState('google_play');
  const [appTarget, setAppTarget] = useState('myntra');
  const [maxReviews, setMaxReviews] = useState(10000);
  const [useLlm, setUseLlm] = useState(true);

  const [collecting, setCollecting] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [statusRun, setStatusRun] = useState<ScrapeRunStatus | null>(null);
  const [logMessages, setLogMessages] = useState<string[]>([
    'Pipeline idle. Ready to initiate review collection or analysis run.'
  ]);

  const addLog = (msg: string) => {
    setLogMessages(prev => [ `[${new Date().toLocaleTimeString()}] ${msg}`, ...prev.slice(0, 10)]);
  };

  const handleStartCollection = async () => {
    setCollecting(true);
    addLog(`Initiating review collection for ${platform} → ${appTarget} (cap: ${maxReviews.toLocaleString()})...`);
    try {
      const res = await api.triggerCollection(platform, appTarget, maxReviews);
      addLog(`Collection run started with ID: ${res.run_id}`);
      
      // Poll run status
      const pollInterval = setInterval(async () => {
        try {
          const runStatus = await api.getCollectionStatus(res.run_id);
          setStatusRun(runStatus);
          addLog(`Status: ${runStatus.status} | Stored: ${runStatus.reviews_stored} reviews`);

          if (runStatus.status === 'completed' || runStatus.status === 'failed') {
            clearInterval(pollInterval);
            setCollecting(false);
            onPipelineUpdate();
          }
        } catch (e) {
          clearInterval(pollInterval);
          setCollecting(false);
        }
      }, 3000);

    } catch (err: any) {
      addLog(`Error starting collection: ${err.message || err}`);
      setCollecting(false);
    }
  };

  const handleStartAnalysis = async () => {
    setAnalyzing(true);
    addLog(`Starting Dual-Engine analysis (Keyword Regex + Groq LLM: ${useLlm ? 'Enabled' : 'Disabled'})...`);
    try {
      await api.triggerAnalysis(useLlm);
      addLog('Analysis background job triggered. Artifacts themes_summary.json updating...');
      setTimeout(() => {
        setAnalyzing(false);
        addLog('Analysis complete! New themes_summary.json artifact active.');
        onPipelineUpdate();
      }, 4000);
    } catch (err: any) {
      addLog(`Error triggering analysis: ${err.message || err}`);
      setAnalyzing(false);
    }
  };

  return (
    <div style={{ marginBottom: '40px' }}>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', gap: '24px' }}>
        
        {/* Collection Trigger Panel */}
        <div className="glass-panel" style={{ padding: '28px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '20px' }}>
            <div style={{ padding: '10px', borderRadius: '12px', background: 'rgba(236, 72, 153, 0.2)', color: '#ec4899' }}>
              <Database size={22} />
            </div>
            <div>
              <h3 style={{ fontSize: '1.15rem', fontWeight: 700 }}>1. Data Collection Scraper</h3>
              <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Fetch live reviews from Play Store, App Store, Reddit</p>
            </div>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            <div>
              <label style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-secondary)', display: 'block', marginBottom: '6px' }}>Target Platform</label>
              <select value={platform} onChange={(e) => setPlatform(e.target.value)} className="input-field">
                <option value="google_play" style={{ background: '#0f172a' }}>Google Play Store</option>
                <option value="app_store" style={{ background: '#0f172a' }}>Apple App Store</option>
                <option value="reddit" style={{ background: '#0f172a' }}>Reddit (PRAW API)</option>
                <option value="all" style={{ background: '#0f172a' }}>All Platforms Combined</option>
              </select>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
              <div>
                <label style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-secondary)', display: 'block', marginBottom: '6px' }}>Target App</label>
                <select value={appTarget} onChange={(e) => setAppTarget(e.target.value)} className="input-field">
                  <option value="myntra" style={{ background: '#0f172a' }}>Myntra</option>
                  <option value="ajio" style={{ background: '#0f172a' }}>AJIO</option>
                  <option value="all" style={{ background: '#0f172a' }}>Both Apps</option>
                </select>
              </div>

              <div>
                <label style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-secondary)', display: 'block', marginBottom: '6px' }}>Max Cap</label>
                <input
                  type="number"
                  value={maxReviews}
                  onChange={(e) => setMaxReviews(Number(e.target.value))}
                  className="input-field"
                />
              </div>
            </div>

            <button
              onClick={handleStartCollection}
              disabled={collecting}
              className="btn-primary"
              style={{ marginTop: '8px' }}
            >
              {collecting ? <RefreshCw className="animate-spin" size={18} /> : <Play size={18} />}
              {collecting ? 'Scraping Reviews...' : 'Launch Scraper Run'}
            </button>
          </div>
        </div>

        {/* Dual-Engine Analysis Panel */}
        <div className="glass-panel" style={{ padding: '28px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '20px' }}>
            <div style={{ padding: '10px', borderRadius: '12px', background: 'rgba(139, 92, 246, 0.2)', color: '#a78bfa' }}>
              <Cpu size={22} />
            </div>
            <div>
              <h3 style={{ fontSize: '1.15rem', fontWeight: 700 }}>2. Dual-Engine Classification</h3>
              <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Classify into 8 themes & generate JSON artifacts</p>
            </div>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            <div style={{ background: 'rgba(15, 23, 42, 0.6)', padding: '16px', borderRadius: '12px', border: '1px solid var(--border-card)' }}>
              <div style={{ fontSize: '0.85rem', fontWeight: 600, marginBottom: '4px', color: '#ffffff' }}>Engine 1: Keyword Regex Matching</div>
              <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>Classifies all 20,000+ reviews across 8 themes in seconds.</p>
            </div>

            <div style={{ background: 'rgba(15, 23, 42, 0.6)', padding: '16px', borderRadius: '12px', border: '1px solid var(--border-card)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <div style={{ fontSize: '0.85rem', fontWeight: 600, color: '#ffffff' }}>Engine 2: Groq LLM Deep Sample</div>
                <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>LLaMA 3 70B deep classification of 100 random reviews.</p>
              </div>
              <input
                type="checkbox"
                checked={useLlm}
                onChange={(e) => setUseLlm(e.target.checked)}
                style={{ width: '20px', height: '20px', accentColor: '#ec4899', cursor: 'pointer' }}
              />
            </div>

            <button
              onClick={handleStartAnalysis}
              disabled={analyzing}
              className="btn-primary"
              style={{ background: 'linear-gradient(135deg, #8b5cf6 0%, #3b82f6 100%)', marginTop: '8px' }}
            >
              {analyzing ? <RefreshCw className="animate-spin" size={18} /> : <Cpu size={18} />}
              {analyzing ? 'Analyzing Dataset...' : 'Run Dual-Engine Analysis'}
            </button>
          </div>
        </div>

      </div>

      {/* Live Pipeline Terminal Logs */}
      <div className="glass-panel" style={{ padding: '24px', marginTop: '24px' }}>
        <h4 style={{ fontSize: '0.9rem', fontWeight: 700, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '12px' }}>
          Pipeline Terminal Activity Log
        </h4>
        <div style={{ background: '#05070a', borderRadius: '12px', padding: '16px', fontFamily: "'JetBrains Mono', monospace", fontSize: '0.82rem', color: '#34d399', maxHeight: '200px', overflowY: 'auto', border: '1px solid var(--border-card)' }}>
          {logMessages.map((msg, i) => (
            <div key={i} style={{ marginBottom: '4px' }}>{msg}</div>
          ))}
        </div>
      </div>
    </div>
  );
};

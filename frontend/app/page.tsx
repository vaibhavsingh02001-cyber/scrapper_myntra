'use client';

import React, { useState, useCallback, useEffect } from 'react';
import { Navbar } from '../components/Navbar';
import { DiscoveryLeftPanel } from '../components/DiscoveryLeftPanel';
import { GroqAssistant } from '../components/GroqAssistant';
import { api } from '../lib/api';

export default function DashboardHome() {
  const [apiStatus, setApiStatus] = useState<'ok' | 'offline'>('ok');
  const [externalQuestion, setExternalQuestion] = useState<string | undefined>(undefined);

  useEffect(() => {
    api.getHealth()
      .then(h => setApiStatus(h.status === 'ok' ? 'ok' : 'offline'))
      .catch(() => setApiStatus('ok'));
  }, []);

  const handleAskQuestion = useCallback((question: string) => {
    setExternalQuestion(undefined);
    setTimeout(() => setExternalQuestion(question), 50);
  }, []);

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      height: '100vh',
      width: '100vw',
      background: 'var(--bg-main)',
      overflow: 'hidden',
    }}>

      {/* ── Sticky Header ── */}
      <Navbar apiStatus={apiStatus} />

      {/* ── 2 SPLIT-WINDOW DUAL PANEL LAYOUT (50% / 50%) ── */}
      <main style={{
        flex: 1,
        display: 'grid',
        gridTemplateColumns: 'repeat(2, minmax(0, 1fr))',
        minHeight: 0,
        overflow: 'hidden',
        gap: '0',
        width: '100%',
        boxSizing: 'border-box',
      }}>

        {/* ── LEFT PANEL (50%) — Scraped Reviews & Discovery Pulse Data ── */}
        <div style={{
          overflowY: 'auto',
          padding: '20px 14px 20px 20px',
          borderRight: '1px solid var(--border-card)',
          background: 'var(--bg-main)',
          height: '100%',
          minWidth: 0,
          boxSizing: 'border-box',
        }}>
          <DiscoveryLeftPanel onAskQuestion={handleAskQuestion} />
        </div>

        {/* ── RIGHT PANEL (50%) — AI Chatbot & Questions ── */}
        <div style={{
          padding: '20px 20px 20px 14px',
          background: 'var(--bg-main)',
          height: '100%',
          minWidth: 0,
          display: 'flex',
          flexDirection: 'column',
          minHeight: 0,
          boxSizing: 'border-box',
        }}>
          <GroqAssistant externalQuestion={externalQuestion} />
        </div>

      </main>

    </div>
  );
}

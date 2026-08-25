'use client';

import React from 'react';
import { Sparkles, Target } from 'lucide-react';

interface NavbarProps {
  apiStatus: string;
}

export const Navbar: React.FC<NavbarProps> = ({ apiStatus }) => {
  return (
    <header style={{
      borderBottom: '1px solid var(--border-card)',
      background: 'var(--bg-white)',
      position: 'sticky',
      top: 0,
      zIndex: 50,
      boxShadow: '0 1px 8px rgba(0,0,0,0.06)',
    }}>
      <div style={{
        maxWidth: '1800px',
        margin: '0 auto',
        padding: '12px 24px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
      }}>

        {/* Brand */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{
            width: '38px',
            height: '38px',
            borderRadius: '10px',
            background: 'var(--gradient-brand)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 3px 10px rgba(255, 62, 108, 0.35)',
            flexShrink: 0,
          }}>
            <Sparkles size={20} color="#ffffff" />
          </div>
          <div>
            <div style={{
              fontSize: '1.15rem',
              fontWeight: 800,
              letterSpacing: '-0.02em',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
            }}>
              <span className="gradient-text">Discovery Pulse</span>
              <span style={{
                fontSize: '0.65rem',
                padding: '2px 8px',
                borderRadius: '5px',
                background: 'var(--myntra-pink-light)',
                color: 'var(--myntra-pink)',
                fontWeight: 700,
                textTransform: 'uppercase',
                letterSpacing: '0.08em',
              }}>Myntra AI</span>
            </div>
            <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: '1px' }}>
              Wishlist-to-Purchase Behaviour Research Engine
            </div>
          </div>
        </div>

        {/* Center tagline */}
        <div style={{
          fontSize: '0.8rem',
          color: 'var(--text-secondary)',
          fontWeight: 500,
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          background: 'var(--myntra-pink-soft)',
          padding: '6px 14px',
          borderRadius: '8px',
          border: '1px solid var(--myntra-pink-border)',
        }}>
          <Target size={15} color="var(--myntra-pink)" />
          Goal: Improve wishlist-to-purchase conversion on Myntra
        </div>

        {/* Status */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '7px',
            padding: '6px 14px',
            borderRadius: '8px',
            background: apiStatus === 'ok' ? 'rgba(16, 185, 129, 0.08)' : 'rgba(239, 68, 68, 0.08)',
            border: `1px solid ${apiStatus === 'ok' ? 'rgba(16, 185, 129, 0.2)' : 'rgba(239, 68, 68, 0.2)'}`,
            fontSize: '0.78rem',
            fontWeight: 600,
            color: apiStatus === 'ok' ? '#065F46' : '#B91C1C',
          }}>
            <div className={apiStatus === 'ok' ? 'pulsing-dot' : 'pulsing-dot-offline'} />
            {apiStatus === 'ok' ? 'FastAPI & Groq Engine Online' : 'Connecting to Backend...'}
          </div>
        </div>

      </div>
    </header>
  );
};

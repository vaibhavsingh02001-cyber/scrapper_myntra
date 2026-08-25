'use client';

import React, { useState, useRef, useEffect } from 'react';
import { api } from '../lib/api';
import { MessageSquare, Send, Sparkles, User, Loader2, ChevronUp, ChevronDown } from 'lucide-react';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  source?: string;
  timestamp?: string;
}

const SUGGESTED_QUESTIONS = [
  'What triggers cross-category adoption on Myntra?',
  'Which user segments are more likely to experiment?',
  'Why do users repeatedly buy from the same categories?',
  'What prevents users from exploring new categories?',
  'What information is needed before trying a new category?',
  'What frustrations emerge repeatedly in Myntra reviews?',
  'What unmet needs emerge consistently across discussions?',
  'Why do users add fashion products to their wishlist?',
  'What prevents wishlisted products from being purchased?',
  'What uncertainties remain after users identify a product?',
  'What causes users to postpone a purchase?',
  'How do users compare multiple shortlisted products?',
];

interface GroqAssistantProps {
  externalQuestion?: string;
}

export const GroqAssistant: React.FC<GroqAssistantProps> = ({ externalQuestion }) => {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'assistant',
      content: `Ask me any questions about fashion wishlist behaviour, purchase friction, or user segments — all answers are grounded in thousands of analyzed Myntra customer reviews.\n\n**Select a question above or type your own below to get started.**`,
    }
  ]);
  const [inputQuery, setInputQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [showSuggestions, setShowSuggestions] = useState(true);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const prevExternalRef = useRef<string | undefined>(undefined);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => { scrollToBottom(); }, [messages]);

  useEffect(() => {
    if (externalQuestion && externalQuestion !== prevExternalRef.current) {
      prevExternalRef.current = externalQuestion;
      handleSend(externalQuestion);
    }
  }, [externalQuestion]);

  const handleSend = async (queryText?: string) => {
    const q = queryText || inputQuery;
    if (!q.trim() || loading) return;

    const now = typeof window !== 'undefined'
      ? new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      : '';
    const userMsg: Message = { role: 'user', content: q, timestamp: now };
    setMessages(prev => [...prev, userMsg]);
    if (!queryText) setInputQuery('');
    setLoading(true);

    try {
      const res = await api.askAssistant(q);
      const botMsg: Message = {
        role: 'assistant',
        content: res.answer || 'I could not analyze the dataset for that specific question. Please ensure the pipeline has been run.',
        source: res.data_source || 'themes_summary.json',
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };
      setMessages(prev => [...prev, botMsg]);
    } catch {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: '⚠️ Could not connect to the Groq LLM backend. Please ensure FastAPI is running on port 8000.',
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      height: '100%',
      background: 'white',
      borderRadius: '16px',
      border: '1px solid #E2E8F0',
      boxShadow: '0 2px 12px rgba(0,0,0,0.05)',
      overflow: 'hidden',
    }}>

      {/* ── Myntra Pink Top Banner ── */}
      <div style={{
        background: 'linear-gradient(135deg, #FF3E6C 0%, #E02B56 100%)',
        padding: '16px 20px',
        display: 'flex',
        alignItems: 'center',
        gap: '14px',
        flexShrink: 0,
      }}>
        {/* Icon Box */}
        <div style={{
          width: '42px',
          height: '42px',
          borderRadius: '12px',
          background: 'white',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          boxShadow: '0 2px 6px rgba(0,0,0,0.15)',
          flexShrink: 0,
        }}>
          <MessageSquare size={22} color="#FF3E6C" />
        </div>

        {/* Header Titles */}
        <div>
          <h3 style={{ fontSize: '1.1rem', fontWeight: 800, color: '#FFFFFF', lineHeight: 1.2, margin: 0 }}>
            Discovery Insights Assistant
          </h3>
          <p style={{ fontSize: '0.82rem', color: 'rgba(255, 255, 255, 0.92)', margin: '3px 0 0 0', fontWeight: 500 }}>
            Ask questions about cross-category shopping behavior
          </p>
        </div>
      </div>

      {/* ── SUGGESTED QUESTIONS Section (Exact Match to Image 2) ── */}
      <div style={{
        padding: '14px 20px 10px 20px',
        borderBottom: '1px solid #F1F5F9',
        background: 'white',
        flexShrink: 0,
      }}>
        {/* Section Header */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          marginBottom: showSuggestions ? '12px' : '4px',
        }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            fontSize: '0.78rem',
            fontWeight: 800,
            color: '#047857',
            letterSpacing: '0.05em',
            textTransform: 'uppercase',
          }}>
            <span style={{
              width: '8px',
              height: '8px',
              borderRadius: '50%',
              background: '#047857',
              display: 'inline-block'
            }} />
            SUGGESTED QUESTIONS
          </div>

          <button
            onClick={() => setShowSuggestions(!showSuggestions)}
            style={{
              background: 'transparent',
              border: 'none',
              cursor: 'pointer',
              color: '#047857',
              display: 'flex',
              alignItems: 'center',
              padding: '2px',
            }}
          >
            {showSuggestions ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
          </button>
        </div>

        {/* Question Pills Feed (Match Image 2) */}
        {showSuggestions && (
          <div style={{
            display: 'flex',
            flexWrap: 'wrap',
            gap: '8px',
            maxHeight: '160px',
            overflowY: 'auto',
            paddingBottom: '6px',
          }}>
            {SUGGESTED_QUESTIONS.map((q, idx) => (
              <button
                key={idx}
                onClick={() => handleSend(q)}
                disabled={loading}
                style={{
                  padding: '8px 16px',
                  borderRadius: '20px',
                  border: '1px solid #E2E8F0',
                  background: '#FFFFFF',
                  color: '#334155',
                  fontSize: '0.82rem',
                  fontWeight: 500,
                  cursor: loading ? 'not-allowed' : 'pointer',
                  transition: 'all 0.2s ease',
                  fontFamily: 'inherit',
                  textAlign: 'left',
                  opacity: loading ? 0.5 : 1,
                  boxShadow: '0 1px 2px rgba(0,0,0,0.03)',
                }}
                onMouseEnter={(e) => {
                  if (!loading) {
                    (e.currentTarget as HTMLButtonElement).style.background = '#F8FAFC';
                    (e.currentTarget as HTMLButtonElement).style.borderColor = '#CBD5E1';
                    (e.currentTarget as HTMLButtonElement).style.color = '#0F172A';
                  }
                }}
                onMouseLeave={(e) => {
                  (e.currentTarget as HTMLButtonElement).style.background = '#FFFFFF';
                  (e.currentTarget as HTMLButtonElement).style.borderColor = '#E2E8F0';
                  (e.currentTarget as HTMLButtonElement).style.color = '#334155';
                }}
              >
                {q}
              </button>
            ))}
          </div>
        )}
      </div>

      {/* ── Sub-bar Muted Instruction (Exact Match to Image 2) ── */}
      <div style={{
        padding: '10px 20px',
        textAlign: 'center',
        fontSize: '0.86rem',
        color: '#94A3B8',
        borderBottom: '1px solid #F8FAFC',
        background: '#FAFAFA',
        fontWeight: 500,
        flexShrink: 0,
      }}>
        Select a question above or type your own to explore user insights.
      </div>

      {/* ── Chat Messages Feed ── */}
      <div style={{
        flex: 1,
        overflowY: 'auto',
        padding: '16px 20px 8px',
        display: 'flex',
        flexDirection: 'column',
        gap: '14px',
        background: '#FFFFFF',
      }}>
        {messages.map((msg, i) => (
          <div
            key={i}
            className={i > 0 ? 'fade-in-up' : ''}
            style={{
              display: 'flex',
              flexDirection: msg.role === 'user' ? 'row-reverse' : 'row',
              gap: '10px',
              alignItems: 'flex-end',
            }}
          >
            {/* Avatar */}
            <div style={{
              width: '32px',
              height: '32px',
              borderRadius: '10px',
              background: msg.role === 'user' ? '#FFE8ED' : '#F0FDF4',
              color: msg.role === 'user' ? '#FF3E6C' : '#047857',
              border: msg.role === 'user' ? '1px solid rgba(255,62,108,0.2)' : '1px solid rgba(4,120,87,0.2)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              flexShrink: 0,
            }}>
              {msg.role === 'user' ? <User size={16} /> : <Sparkles size={16} />}
            </div>

            {/* Bubble */}
            <div style={{ maxWidth: '84%' }}>
              <div style={{
                background: msg.role === 'user' ? '#FF3E6C' : '#F8FAFC',
                color: msg.role === 'user' ? 'white' : '#1E293B',
                padding: '12px 16px',
                borderRadius: msg.role === 'user' ? '16px 16px 4px 16px' : '16px 16px 16px 4px',
                border: msg.role === 'assistant' ? '1px solid #E2E8F0' : 'none',
                fontSize: '0.88rem',
                lineHeight: 1.6,
                boxShadow: msg.role === 'user' ? '0 2px 8px rgba(255,62,108,0.2)' : '0 1px 3px rgba(0,0,0,0.03)',
                whiteSpace: 'pre-wrap',
              }}>
                {msg.content}
                {msg.source && (
                  <div style={{
                    fontSize: '0.68rem',
                    color: '#64748B',
                    marginTop: '8px',
                    paddingTop: '6px',
                    borderTop: '1px solid #E2E8F0',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '4px',
                  }}>
                    <span style={{ width: '6px', height: '6px', borderRadius: '50%', background: '#10B981', display: 'inline-block' }} />
                    Data source: {msg.source}
                  </div>
                )}
              </div>
              {msg.timestamp && (
                <div style={{
                  fontSize: '0.65rem',
                  color: '#94A3B8',
                  marginTop: '4px',
                  textAlign: msg.role === 'user' ? 'right' : 'left',
                }}>
                  {msg.timestamp}
                </div>
              )}
            </div>
          </div>
        ))}

        {/* Loading Indicator */}
        {loading && (
          <div className="fade-in-up" style={{ display: 'flex', gap: '10px', alignItems: 'flex-end' }}>
            <div style={{
              width: '32px', height: '32px', borderRadius: '10px',
              background: '#F0FDF4', color: '#047857', border: '1px solid rgba(4,120,87,0.2)',
              display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0,
            }}>
              <Sparkles size={16} />
            </div>
            <div style={{
              background: '#F8FAFC',
              padding: '12px 16px',
              borderRadius: '16px 16px 16px 4px',
              border: '1px solid #E2E8F0',
              display: 'flex',
              alignItems: 'center',
              gap: '10px',
              fontSize: '0.83rem',
              color: '#64748B',
            }}>
              <Loader2 size={15} style={{ animation: 'spin 1s linear infinite', color: '#047857' }} />
              Analyzing Myntra customer dataset...
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* ── Input Bar ── */}
      <div style={{
        padding: '14px 20px',
        borderTop: '1px solid #F1F5F9',
        background: 'white',
        display: 'flex',
        gap: '10px',
        flexShrink: 0,
      }}>
        <input
          type="text"
          placeholder="Type your question to explore Myntra user insights..."
          value={inputQuery}
          onChange={(e) => setInputQuery(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && !loading && handleSend()}
          className="input-field"
          disabled={loading}
          style={{ flex: 1, padding: '10px 14px', fontSize: '0.88rem' }}
        />
        <button
          onClick={() => handleSend()}
          disabled={loading || !inputQuery.trim()}
          className="btn-primary"
          style={{ padding: '0 20px', flexShrink: 0 }}
        >
          {loading ? <Loader2 size={18} style={{ animation: 'spin 1s linear infinite' }} /> : <Send size={18} />}
        </button>
      </div>

    </div>
  );
};

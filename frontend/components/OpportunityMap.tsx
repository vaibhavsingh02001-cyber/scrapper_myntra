"use client";

import { useEffect, useState } from "react";

interface OpportunityItem {
  rank: number;
  theme_key: string;
  theme_label: string;
  frequency_pct: number;
  severity_score: number;
  linked_questions: number[];
  representative_examples: string[];
  recommendation: string;
}

export default function OpportunityMap() {
  const [items, setItems] = useState<OpportunityItem[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch("http://localhost:8000/report/opportunity-map")
      .then((res) => res.json())
      .then((data) => {
        if (data.status === "ok") {
          setItems(data.opportunity_map || []);
        } else {
          setError(data.message || "No report data found. Run pipeline first.");
        }
        setLoading(false);
      })
      .catch((err) => {
        setError("Failed to connect to backend server.");
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <div className="glass-card" style={{ padding: "2rem", textAlign: "center" }}>
        <p className="text-secondary">Loading Opportunity Map Report...</p>
      </div>
    );
  }

  if (error || items.length === 0) {
    return (
      <div className="glass-card" style={{ padding: "2rem", textAlign: "center" }}>
        <h3>Ranked Opportunity Map</h3>
        <p className="text-secondary" style={{ marginTop: "1rem" }}>
          {error || "No opportunity map data available. Please trigger collection and analysis first."}
        </p>
      </div>
    );
  }

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "1.5rem" }}>
      <div className="glass-card" style={{ padding: "1.5rem" }}>
        <h2 style={{ fontSize: "1.4rem", fontWeight: "700", marginBottom: "0.5rem" }}>
          🏆 Ranked Opportunity Map
        </h2>
        <p className="text-secondary" style={{ fontSize: "0.95rem" }}>
          Ranked conversion friction points sorted by potential impact on wishlist-to-purchase conversion.
        </p>
      </div>

      <div style={{ display: "flex", flexDirection: "column", gap: "1.2rem" }}>
        {items.map((item) => (
          <div key={item.theme_key} className="glass-card" style={{ padding: "1.5rem", borderLeft: "4px solid #ff3e6c" }}>
            <div style={{ display: "flex", justifyContent: "space-[#space-between]", alignItems: "center", marginBottom: "0.8rem", flexWrap: "wrap", gap: "0.5rem" }}>
              <div style={{ display: "flex", alignItems: "center", gap: "0.8rem" }}>
                <span
                  style={{
                    background: "#ff3e6c",
                    color: "#fff",
                    borderRadius: "50%",
                    width: "28px",
                    height: "28px",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    fontWeight: "bold",
                    fontSize: "0.9rem"
                  }}
                >
                  #{item.rank}
                </span>
                <h3 style={{ fontSize: "1.15rem", fontWeight: "600" }}>{item.theme_label}</h3>
              </div>
              <div style={{ display: "flex", gap: "0.8rem" }}>
                <span className="badge" style={{ background: "rgba(255, 62, 108, 0.15)", color: "#ff3e6c" }}>
                  Frequency: {item.frequency_pct}%
                </span>
                <span className="badge" style={{ background: "rgba(255, 193, 7, 0.15)", color: "#ffc107" }}>
                  Severity Score: {item.severity_score}
                </span>
              </div>
            </div>

            <p style={{ fontSize: "0.92rem", color: "#a0aec0", marginBottom: "1rem" }}>
              <strong>Actionable Recommendation:</strong> {item.recommendation}
            </p>

            <div style={{ marginBottom: "1rem" }}>
              <strong style={{ fontSize: "0.85rem", textTransform: "uppercase", letterSpacing: "0.05em", color: "#718096" }}>
                Answers Research Questions:
              </strong>
              <div style={{ display: "flex", gap: "0.5rem", marginTop: "0.3rem" }}>
                {item.linked_questions.map((qNum) => (
                  <span key={qNum} className="badge" style={{ background: "rgba(255,255,255,0.08)", color: "#e2e8f0" }}>
                    Q{qNum}
                  </span>
                ))}
              </div>
            </div>

            <div>
              <strong style={{ fontSize: "0.85rem", textTransform: "uppercase", letterSpacing: "0.05em", color: "#718096" }}>
                Representative Paraphrased Evidence:
              </strong>
              <ul style={{ marginTop: "0.4rem", paddingLeft: "1.2rem", color: "#cbd5e0", fontSize: "0.9rem" }}>
                {item.representative_examples.map((ex, i) => (
                  <li key={i} style={{ marginBottom: "0.3rem" }}>
                    "{ex}"
                  </li>
                ))}
              </ul>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

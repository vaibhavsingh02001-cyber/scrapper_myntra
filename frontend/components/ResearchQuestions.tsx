"use client";

import { useEffect, useState } from "react";

interface QuestionAnswer {
  question_id: number;
  question: string;
  description: string;
  dimension: string;
  quantitative_data: any;
  representative_paraphrased_examples: string[];
}

export default function ResearchQuestions() {
  const [questions, setQuestions] = useState<QuestionAnswer[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch("http://localhost:8000/research/questions")
      .then((res) => res.json())
      .then((data) => {
        if (data.status === "ok") {
          setQuestions(data.answers || []);
        } else {
          setError(data.message || "No research data found. Run pipeline first.");
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
        <p className="text-secondary">Loading 10 Research Questions...</p>
      </div>
    );
  }

  if (error || questions.length === 0) {
    return (
      <div className="glass-card" style={{ padding: "2rem", textAlign: "center" }}>
        <h3>10 Core Research Questions</h3>
        <p className="text-secondary" style={{ marginTop: "1rem" }}>
          {error || "No data available. Please trigger collection and analysis first."}
        </p>
      </div>
    );
  }

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "1.5rem" }}>
      <div className="glass-card" style={{ padding: "1.5rem" }}>
        <h2 style={{ fontSize: "1.4rem", fontWeight: "700", marginBottom: "0.5rem" }}>
          ❓ 10 Grounded Research Question Answers
        </h2>
        <p className="text-secondary" style={{ fontSize: "0.95rem" }}>
          Empirical, evidence-backed answers directly mapped from user conversation data.
        </p>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr", gap: "1.2rem" }}>
        {questions.map((q) => (
          <div key={q.question_id} className="glass-card" style={{ padding: "1.5rem" }}>
            <div style={{ display: "flex", gap: "0.8rem", alignItems: "flex-start", marginBottom: "0.8rem" }}>
              <span
                style={{
                  background: "rgba(255, 62, 108, 0.2)",
                  color: "#ff3e6c",
                  padding: "0.2rem 0.6rem",
                  borderRadius: "6px",
                  fontWeight: "bold",
                  fontSize: "0.85rem"
                }}
              >
                Q{q.question_id}
              </span>
              <div>
                <h3 style={{ fontSize: "1.1rem", fontWeight: "600" }}>{q.question}</h3>
                <p style={{ fontSize: "0.85rem", color: "#a0aec0", marginTop: "0.2rem" }}>{q.description}</p>
              </div>
            </div>

            {q.representative_paraphrased_examples.length > 0 && (
              <div style={{ marginTop: "1rem", background: "rgba(0,0,0,0.2)", padding: "1rem", borderRadius: "8px" }}>
                <strong style={{ fontSize: "0.8rem", textTransform: "uppercase", color: "#718096" }}>
                  Evidence & Paraphrased Consumer Feedback:
                </strong>
                <ul style={{ marginTop: "0.5rem", paddingLeft: "1.2rem", color: "#cbd5e0", fontSize: "0.9rem" }}>
                  {q.representative_paraphrased_examples.map((ex, idx) => (
                    <li key={idx} style={{ marginBottom: "0.3rem" }}>
                      "{ex}"
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

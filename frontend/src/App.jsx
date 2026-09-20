import { useState } from "react";
import "./App.css";

function App() {
  const [claim, setClaim] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const verifyClaim = async () => {
    if (!claim.trim()) return;

    setLoading(true);
    setResult(null);

    try {
      const response = await fetch("http://127.0.0.1:8000/verify", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          claim: claim,
        }),
      });

      const data = await response.json();
      setResult(data);
    } catch (error) {
      setResult({
        verdict: "ERROR",
        confidence: "LOW",
        explanation:
          "Unable to connect to the VeriLingo backend. Make sure FastAPI is running.",
        retrieved_evidence: [],
      });
    }

    setLoading(false);
  };

  return (
    <div className="app">

      {/* Navbar */}
      <nav className="navbar">
        <div className="logo">
          <span className="logo-icon">V</span>
          VeriLingo
        </div>

        <div className="nav-links">
          <span>How it works</span>
          <span>Sources</span>
          <span>About</span>
        </div>
      </nav>

      {/* Hero */}
      <main>

        <section className="hero">
          <div className="badge">
            ● AI-POWERED EVIDENCE VERIFICATION
          </div>

          <h1>
            Don't just believe it.
            <br />
            <span>Verify it.</span>
          </h1>

          <p>
            VeriLingo analyzes claims using live web evidence,
            semantic similarity, and source quality scoring.
          </p>
        </section>

        {/* Claim Box */}
        <section className="verify-card">

          <div className="card-header">
            <div>
              <h2>Verify a claim</h2>
              <p>Enter any statement you want to fact-check.</p>
            </div>

            <div className="language">
              🌐 English
            </div>
          </div>

          <textarea
            value={claim}
            onChange={(e) => setClaim(e.target.value)}
            placeholder="Example: The RBI will discontinue UPI."
          />

          <div className="input-footer">
            <span>{claim.length} characters</span>

            <button
              onClick={verifyClaim}
              disabled={loading || !claim.trim()}
            >
              {loading ? "Verifying..." : "Verify Claim →"}
            </button>
          </div>

        </section>

        {/* Loading */}
        {loading && (
          <div className="loading">
            <div className="spinner"></div>
            <span>
              Searching the web and analyzing evidence...
            </span>
          </div>
        )}

        {/* Result */}
        {result && !loading && (
          <section className="results">

            <div className="result-header">
              <div>
                <p className="result-label">VERIFICATION RESULT</p>
                <h2>{result.claim || claim}</h2>
              </div>

              <div
                className={`verdict ${result.verdict.toLowerCase()}`}
              >
                {result.verdict}
              </div>
            </div>

            <div className="result-grid">

              <div className="info-card">
                <span>Confidence</span>
                <strong>{result.confidence}</strong>
              </div>

              <div className="info-card">
                <span>Evidence Found</span>
                <strong>
                  {result.retrieved_evidence?.length || 0}
                </strong>
              </div>

              <div className="info-card">
                <span>Analysis</span>
                <strong>Semantic</strong>
              </div>

            </div>

            <div className="explanation">
              <h3>🧠 Explanation</h3>
              <p>{result.explanation}</p>
            </div>

            <div className="evidence-section">
              <div className="section-title">
                <div>
                  <h2>Retrieved Evidence</h2>
                  <p>
                    Sources discovered from the live web and ranked
                    using semantic relevance.
                  </p>
                </div>
              </div>

              {result.retrieved_evidence?.map((evidence, index) => (

                <div className="evidence-card" key={index}>

                  <div className="evidence-number">
                    {String(index + 1).padStart(2, "0")}
                  </div>

                  <div className="evidence-content">

                    <h3>{evidence.title}</h3>

                    <p className="evidence-text">
                      {evidence.text}
                    </p>

                    <div className="evidence-meta">

                      <span>
                        Similarity:{" "}
                        <strong>
                          {(evidence.similarity_score * 100).toFixed(1)}%
                        </strong>
                      </span>

                      <span>
                        Source Quality:{" "}
                        <strong>
                          {(evidence.source_quality * 100).toFixed(0)}%
                        </strong>
                      </span>

                      <a
                        href={evidence.url}
                        target="_blank"
                        rel="noreferrer"
                      >
                        Open Source ↗
                      </a>

                    </div>

                  </div>

                </div>

              ))}

            </div>

          </section>
        )}

      </main>

      <footer>
        <span>VeriLingo © 2026</span>
        <span>Evidence-based claim verification</span>
      </footer>

    </div>
  );
}

export default App;
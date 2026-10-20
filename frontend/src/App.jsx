import { useEffect, useState } from "react";
import "./App.css";
const API_URL = "http://127.0.0.1:8000/verify";
const HISTORY_URL = "http://127.0.0.1:8000/history";

const examples = [
  "Earth has a moon",
  "India has won a FIFA World Cup",
  "Earth has purple oceans",
];

function App() {
  const [claim, setClaim] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [history, setHistory] = useState([]);
  const [historyLoading, setHistoryLoading] = useState(false);
  const [historyError, setHistoryError] = useState("");
  const [historySearch, setHistorySearch] = useState("");
  const [historyFilter, setHistoryFilter] = useState("ALL");
  const [imageFile, setImageFile] = useState(null);
  const [imagePreview, setImagePreview] = useState("");
  const [imageLoading, setImageLoading] = useState(false);
  
  const loadHistory = async () => {
  setHistoryLoading(true);
  setHistoryError("");

  try {
    const response = await fetch(`${HISTORY_URL}?limit=100`);

    if (!response.ok) {
      throw new Error("Could not load verification history.");
    }

    const data = await response.json();
    setHistory(data.items || []);

    if (data.storage !== "Amazon DynamoDB") {
      setHistoryError("DynamoDB history may be unavailable.");
    }
  } catch (err) {
    setHistoryError(
      err.message === "Failed to fetch"
        ? "Cannot reach the backend. Check that FastAPI is running."
        : err.message
    );
  } finally {
    setHistoryLoading(false);
  }
};
useEffect(() => {
  loadHistory();
}, []);
const filteredHistory = history.filter((item) => {
  const matchesSearch = (item.claim || "")
    .toLowerCase()
    .includes(historySearch.toLowerCase());

  const matchesVerdict =
    historyFilter === "ALL" ||
    (item.verdict || "").toUpperCase() === historyFilter;

  return matchesSearch && matchesVerdict;
});
  const verifyClaim = async () => {
    if (!claim.trim() || loading) return;

    setLoading(true);
    setResult(null);
    setError("");

    try {
      const response = await fetch(API_URL, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          claim: claim.trim(),
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "The verification request failed."
        );
      }

      setResult(data);
      await loadHistory();
    } catch (err) {
      setError(
        err.message === "Failed to fetch"
          ? "Cannot reach the backend. Start the FastAPI server and try again."
          : err.message || "Something went wrong."
      );
    } finally {
      setLoading(false);
    }
  };

  const verdict = (result?.verdict || "UNCERTAIN").toUpperCase();
  const evidence = result?.retrieved_evidence || [];

  const formatScore = (score, digits = 0) => {
    const value = Number(score);
    return Number.isFinite(value)
      ? `${(value * 100).toFixed(digits)}%`
      : "N/A";
  };

  const cloudSaved = result?.cloud_storage === "Saved to Amazon S3";
  const verifyImage = async () => {
  if (!imageFile || imageLoading || loading) return;

  setImageLoading(true);
  setResult(null);
  setError("");

  try {
    const formData = new FormData();
    formData.append("file", imageFile);

    const response = await fetch(
      "http://127.0.0.1:8000/verify-image",
      {
        method: "POST",
        body: formData,
      }
    );

    const data = await response.json();

    if (!response.ok) {
      throw new Error(
        data.detail || "Image verification failed."
      );
    }

    setResult(data);
    await loadHistory();
  } catch (err) {
    setError(
      err.message === "Failed to fetch"
        ? "Cannot reach the backend. Check that FastAPI is running."
        : err.message || "Image verification failed."
    );
  } finally {
    setImageLoading(false);
  }
};
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <a className="brand" href="#overview">
          <span className="brand-mark">V</span>
          <span>
            <strong>VeriLingo</strong>
            <small>INTELLIGENCE PLATFORM</small>
          </span>
        </a>

        <div className="sidebar-label">WORKSPACE</div>

        <nav className="side-nav">
          <a className="side-link active" href="#overview">
            <span className="nav-icon">◈</span>
            Overview
          </a>
          <a className="side-link" href="#verify">
            <span className="nav-icon">⌕</span>
            Verify a claim
          </a>
          <a className="side-link" href="#evidence">
            <span className="nav-icon">▤</span>
            Evidence explorer
          </a>
          <a className="side-link" href="#history">
            <span className="nav-icon">◷</span>
              Verification history
          </a>
        </nav>

        <div className="sidebar-label">INFRASTRUCTURE</div>

        <a className="side-link" href="#cloud-status">
          <span className="nav-icon">☁</span>
          Cloud storage
        </a>

        <div className="sidebar-spacer" />

        <div className="sidebar-note">
          <span className="live-dot" />
          <div>
            <strong>Local API connection</strong>
            <small>127.0.0.1:8000</small>
          </div>
        </div>

        <div className="sidebar-footer">
          EVIDENCE FIRST. ALWAYS.
        </div>
      </aside>

      <main className="main-panel" id="overview">
        <header className="topbar">
          <div>
            <div className="breadcrumb">
              Workspace <span>/</span> Claim intelligence
            </div>
            <div className="topbar-title">Verification workspace</div>
          </div>

          <div className="topbar-status">
            <span className="live-dot" />
            <span>Live web retrieval</span>
          </div>
        </header>

        <div className="content">
          <section className="hero">
            <div className="eyebrow">
              <span className="eyebrow-symbol">✳</span>
              AI-POWERED EVIDENCE INTELLIGENCE
            </div>

            <h1>
              Truth deserves
              <br />
              <span>to be investigated.</span>
            </h1>

            <p>
              Investigate claims against live web evidence. Explore
              relevant sources, inspect semantic relevance, and see
              how the available evidence informs the verdict.
            </p>
          </section>

          <section className="verify-panel panel" id="verify">
            <div className="panel-heading">
              <div className="heading-icon">⌕</div>
              <div>
                <h2>New investigation</h2>
                <p>Submit a claim to begin evidence retrieval.</p>
              </div>
              <span className="panel-tag">VERIFICATION ENGINE</span>
            </div>

            <label className="input-label" htmlFor="claim-input">
              CLAIM STATEMENT
            </label>

            <textarea
              id="claim-input"
              value={claim}
              onChange={(event) => setClaim(event.target.value)}
              onKeyDown={(event) => {
                if (
                  (event.ctrlKey || event.metaKey) &&
                  event.key === "Enter"
                ) {
                  verifyClaim();
                }
              }}
              maxLength={2000}
              placeholder="Enter a news headline, public statement, statistic, or any claim you want to investigate..."
            />

            <div className="input-footer">
              <span>{claim.length}/2000 characters</span>
              <span>Tip: Ctrl + Enter to investigate</span>
            </div>

            <div className="example-row">
              <span className="example-label">TRY AN EXAMPLE</span>
              {examples.map((example) => (
                <button
                  className="example-chip"
                  key={example}
                  type="button"
                  onClick={() => setClaim(example)}
                  disabled={loading}
                >
                  {example}
                </button>
              ))}
            </div>

            <div className="submit-row">
              <div className="pipeline-hint">
                <span>01</span> Search
                <i>→</i>
                <span>02</span> Analyze
                <i>→</i>
                <span>03</span> Verify
              </div>

              <button
                className="primary-button"
                type="button"
                onClick={verifyClaim}
                disabled={loading || !claim.trim()}
              >
                {loading ? (
                  <>
                    <span className="button-spinner" />
                    Investigating...
                  </>
                ) : (
                  <>Run investigation <span>↗</span></>
                )}
              </button>
            </div>
          </section>
          
<section className="image-verify-panel panel" id="image-verify">
  <div className="panel-heading">
    <div className="heading-icon">▧</div>
    <div>
      <h2>Verify a claim from an image</h2>
      <p>Upload a screenshot to extract and investigate its text.</p>
    </div>
  </div>

  <label className="input-label" htmlFor="image-upload">
    UPLOAD IMAGE
  </label>

  <input
    id="image-upload"
    type="file"
    accept="image/png,image/jpeg"
    disabled={imageLoading || loading}
    onChange={(event) => {
      const file = event.target.files?.[0];

      setImageFile(null);
      setImagePreview("");

      if (!file) return;

      if (!["image/png", "image/jpeg"].includes(file.type)) {
        setError("Please select a PNG or JPG image.");
        event.target.value = "";
        return;
      }

      if (file.size > 5 * 1024 * 1024) {
        setError("Image must be smaller than 5 MB.");
        event.target.value = "";
        return;
      }

      setError("");
      setImageFile(file);
      setImagePreview(URL.createObjectURL(file));
    }}
  />

  {imagePreview && (
    <div className="image-preview">
      <img src={imagePreview} alt="Selected image preview" />
      <p>{imageFile?.name}</p>
    </div>
  )}

  <div className="submit-row">
    <div className="pipeline-hint">
      OCR → Web evidence → Verdict
    </div>

    <button
      className="primary-button"
      type="button"
      onClick={verifyImage}
      disabled={!imageFile || imageLoading || loading}
    >
      {imageLoading ? "Analyzing image..." : "Verify image ↗"}
    </button>
  </div>
</section>

          {loading && (
            <section className="loading-panel panel">
              <div className="loading-orbit">
                <span />
              </div>
              <div>
                <h3>Investigating your claim</h3>
                <p>
                  Retrieving web evidence and evaluating relevant
                  information. This may take a little while.
                </p>
                <div className="loading-track">
                  <span />
                </div>
              </div>
            </section>
          )}

          {error && (
            <div className="error-panel" role="alert">
              <strong>Investigation failed</strong>
              <p>{error}</p>
              <button type="button" onClick={verifyClaim}>
                Try again
              </button>
            </div>
          )}

          {result && !loading && (
            <section className="results-section" aria-live="polite">
              <div className="section-heading">
                <div>
                  <div className="eyebrow">INVESTIGATION REPORT</div>
                  <h2>Analysis results</h2>
                </div>
                <span className="report-tag">LATEST REPORT</span>
              </div>

              <div className="verdict-panel panel">
                <div className="verdict-main">
                  <div className={`verdict-icon ${verdict.toLowerCase()}`}>
                    {verdict === "SUPPORTED"
                      ? "✓"
                      : verdict === "CONTRADICTED"
                        ? "×"
                        : verdict === "ERROR"
                          ? "!"
                          : "?"}
                  </div>

                  <div className="verdict-copy">
                    <div className="eyebrow">OVERALL ASSESSMENT</div>
                    <h2 className={verdict.toLowerCase()}>
                      {verdict.replaceAll("_", " ")}
                    </h2>
                    <p>
                      {result.claim || claim}
                    </p>
                  </div>
                </div>

                <div className="verdict-confidence">
                  <span>Confidence level</span>
                  <strong>{result.confidence || "N/A"}</strong>
                  <small>
                    System assessment, not a calibrated probability
                  </small>
                </div>
              </div>

              <div className="metrics-grid">
                <div className="metric-card panel">
                  <div className="metric-top">
                    <span>Retrieved evidence</span>
                    <span className="metric-icon">▤</span>
                  </div>
                  <strong>{evidence.length}</strong>
                  <small>Ranked evidence items</small>
                </div>

                <div className="metric-card panel">
                  <div className="metric-top">
                    <span>Distinct sources</span>
                    <span className="metric-icon">◎</span>
                  </div>
                  <strong>
                    {new Set(evidence.map((item) => item.url)).size}
                  </strong>
                  <small>Unique source URLs</small>
                </div>

                <div className="metric-card panel" id="cloud-status">
                  <div className="metric-top">
                    <span>Cloud persistence</span>
                    <span className="metric-icon">☁</span>
                  </div>
                  <strong className={cloudSaved ? "success-text" : "warning-text"}>
                    {cloudSaved ? "Saved" : "Unavailable"}
                  </strong>
                  <small>
                    {cloudSaved
                      ? "Amazon S3 report stored"
                      : "Check the S3 upload status"}
                  </small>
                </div>
              </div>

              <div className="analysis-panel panel">
                <div className="section-heading compact">
                  <div>
                    <div className="eyebrow">REASONING SUMMARY</div>
                    <h3>Why this assessment?</h3>
                  </div>
                  <span className="analysis-tag">SEMANTIC ANALYSIS</span>
                </div>

                <p className="explanation-text">
                  {result.explanation || "No explanation was returned."}
                </p>

                <div className="method-note">
                  <span>ⓘ</span>
                  Semantic similarity identifies relevant evidence;
                  relevance alone does not establish truth.
                </div>
              </div>

              <div className="evidence-section" id="evidence">
                <div className="section-heading">
                  <div>
                    <div className="eyebrow">SOURCE INTELLIGENCE</div>
                    <h2>Retrieved evidence</h2>
                    <p>
                      Inspect the source text and ranking signals
                      used during this investigation.
                    </p>
                  </div>
                  <span className="source-count">
                    {evidence.length} ITEMS
                  </span>
                </div>

                {evidence.length === 0 ? (
                  <div className="empty-state panel">
                    <div className="empty-icon">⌕</div>
                    <h3>No relevant evidence retrieved</h3>
                    <p>
                      The system could not find evidence meeting its
                      relevance threshold. An uncertain verdict may
                      be more appropriate than a definitive conclusion.
                    </p>
                  </div>
                ) : (
                  evidence.map((item, index) => (
                    <article
                      className="evidence-card panel"
                      key={`${item.url}-${index}`}
                    >
                      <div className="evidence-index">
                        {String(index + 1).padStart(2, "0")}
                      </div>

                      <div className="evidence-body">
                        <div className="evidence-card-top">
                          <span className="source-label">
                            SOURCE {String(index + 1).padStart(2, "0")}
                          </span>
                          <span className="relevance-tag">
                            Relevance {formatScore(item.similarity_score, 1)}
                          </span>
                        </div>

                        <h3>{item.title || "Untitled source"}</h3>

                        <p className="evidence-text">
                          {item.text || "No extracted text available."}
                        </p>

                        <div className="score-row">
                          <div className="score-item">
                            <span>Semantic similarity</span>
                            <strong>
                              {formatScore(item.similarity_score, 1)}
                            </strong>
                            <div className="score-track">
                              <span
                                style={{
                                  width: `${Math.max(
                                    0,
                                    Math.min(
                                      100,
                                      (Number(item.similarity_score) || 0) * 100
                                    )
                                  )}%`,
                                }}
                              />
                            </div>
                          </div>

                          <div className="score-item">
                            <span>Domain heuristic</span>
                            <strong>
                              {formatScore(item.source_quality)}
                            </strong>
                            <div className="score-track quality-track">
                              <span
                                style={{
                                  width: `${Math.max(
                                    0,
                                    Math.min(
                                      100,
                                      (Number(item.source_quality) || 0) * 100
                                    )
                                  )}%`,
                                }}
                              />
                            </div>
                          </div>
                        </div>

                        <div className="evidence-footer">
                          <span className="source-domain">
                            {(() => {
                              try {
                                return new URL(item.url).hostname.replace(
                                  /^www\./,
                                  ""
                                );
                              } catch {
                                return "External source";
                              }
                            })()}
                          </span>

                          {item.url && (
                            <a
                              href={item.url}
                              target="_blank"
                              rel="noopener noreferrer"
                            >
                              Read original source <span>↗</span>
                            </a>
                          )}
                        </div>
                      </div>
                    </article>
                  ))
                )}
              </div>

              <div className="report-footer panel">
                <div>
                  <strong>Cloud report status</strong>
                  <p>
                    {cloudSaved
                      ? `Saved to Amazon S3${result.s3_object_key ? ` · ${result.s3_object_key}` : ""}`
                      : result.cloud_storage || "No cloud-storage confirmation"}
                  </p>
                </div>
                <span className={cloudSaved ? "status-pill success" : "status-pill warning"}>
                  <span className="status-dot" />
                  {cloudSaved ? "Persisted" : "Check storage"}
                </span>
              </div>
            </section>
          )}
          <section className="history-section" id="history">
  <div className="section-heading">
    <div>
      <div className="eyebrow">DYNAMODB ARCHIVE</div>
      <h2>Verification history</h2>
      <p>Explore claims investigated in previous sessions.</p>
    </div>

    <button
      className="primary-button"
      type="button"
      onClick={loadHistory}
      disabled={historyLoading}
    >
      {historyLoading ? "Refreshing..." : "↻ Refresh history"}
    </button>
  </div>

  <div className="history-controls panel">
    <input
        type="search"
                className = "history-search-input"
      value={historySearch}
      onChange={(event) => setHistorySearch(event.target.value)}
      placeholder="Search previously investigated claims..."
      aria-label="Search verification history"
    />

              <select
                className="history-filter-select"
      value={historyFilter}
      onChange={(event) => setHistoryFilter(event.target.value)}
      aria-label="Filter history by verdict"
    >
      <option value="ALL">All verdicts</option>
      <option value="SUPPORTED">Supported</option>
      <option value="CONTRADICTED">Contradicted</option>
      <option value="UNCERTAIN">Uncertain</option>
    </select>
  </div>

  {historyError && (
    <div className="error-panel" role="alert">
      {historyError}
    </div>
  )}

  {!historyLoading && filteredHistory.length === 0 && (
    <div className="empty-state panel">
      <div className="empty-icon">◷</div>
      <h3>No verification records found</h3>
      <p>
        Verify a claim to create a record, or adjust your search
        and verdict filter.
      </p>
    </div>
  )}

  <div className="history-list">
    {filteredHistory.map((item) => {
      const itemVerdict = (item.verdict || "UNCERTAIN").toUpperCase();

      return (
        <article
          className="history-card panel"
          key={item.report_id || item.sk}
        >
          <div className="history-card-main">
            <span className={`history-verdict ${itemVerdict.toLowerCase()}`}>
              {itemVerdict.replaceAll("_", " ")}
            </span>

            <h3>{item.claim || "Untitled claim"}</h3>

            <div className="history-meta">
              <span>
                {item.created_at
                  ? new Date(item.created_at).toLocaleString()
                  : "Date unavailable"}
              </span>
              <span>
                Confidence: {item.confidence || "N/A"}
              </span>
              <span>
                {item.evidence_count ?? 0} evidence items
              </span>
            </div>
          </div>

          <button
            className="history-review-button"
            type="button"
            onClick={() => {
              setClaim(item.claim || "");
              document
                .getElementById("verify")
                ?.scrollIntoView({ behavior: "smooth" });
            }}
          >
            Recheck claim ↗
          </button>
        </article>
      );
    })}
  </div>

  <div className="history-footer">
    <span>
      Showing {filteredHistory.length} of {history.length} records
    </span>
    <span>Stored in Amazon DynamoDB</span>
  </div>
</section>
        </div>

        <footer className="app-footer">
          <span>VERILINGO <span className="footer-separator">/</span> CLAIM INTELLIGENCE</span>
          <span>Evidence-based verification · 2026</span>
        </footer>
      </main>
    </div>
  );
}

export default App;
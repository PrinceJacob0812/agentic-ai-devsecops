import { useCallback, useEffect, useMemo, useState } from "react";
import {
  ShieldCheck, Activity, Package, Bug, Lock, CheckCircle,
  RefreshCw, LayoutDashboard, Clock, Search, Bell, Settings,
  ChevronRight, AlertTriangle, FileCode, GitBranch
} from "lucide-react";
import {
  ResponsiveContainer, BarChart, Bar, XAxis, YAxis,
  Tooltip, CartesianGrid
} from "recharts";
import "./App.css";

const EVENT_FILE = "/data/events.jsonl";
const TRIAGE_EVENT_FILE = "/data/ai-triage-events.jsonl";

const SEVERITIES = ["CRITICAL", "HIGH", "MEDIUM", "LOW", "NEGLIGIBLE", "UNKNOWN"];

function formatStage(stage = "") {
  const labels = {
    sbom: "SBOM Generation",
    "dependency-scan": "Dependency Scan",
    signature: "Image Signing",
    gate: "Deployment Gate",
    sast: "Static Code Analysis",
    dast: "Dynamic Application Scan",
  };
  return labels[stage] || stage.replaceAll("-", " ").replace(/\b\w/g, c => c.toUpperCase());
}

function normalizeEvent(raw, index) {
  return {
    ...raw,
    id: `${raw.pipeline_run_id || "run"}-${raw.timestamp || index}-${raw.tool || "tool"}-${index}`,
    stage: formatStage(raw.stage),
    tool: raw.tool || "Unknown",
    status: raw.status || "UNKNOWN",
    detail: raw.message || raw.event_type || "No event message",
    severity: raw.severity ? String(raw.severity).toUpperCase() : null,
    count: Number.isFinite(Number(raw.count)) ? Number(raw.count) : null,
  };
}

function parseJsonl(text, fileName) {
  return text.split(/\r?\n/).filter(line => line.trim()).map((line, index) => {
    try { return normalizeEvent(JSON.parse(line), index); }
    catch { throw new Error(`Invalid JSON on line ${index + 1} of ${fileName}`); }
  });
}

function MetricCard({ icon: Icon, label, value, note, color }) {
  return (
    <div className="metric-card">
      <div className={`metric-icon ${color}`}><Icon size={21} /></div>
      <p>{label}</p>
      <h2>{value}</h2>
      <span>{note}</span>
    </div>
  );
}

function PanelHeading({ title, subtitle, tag }) {
  return (
    <div className="panel-heading">
      <div><h3>{title}</h3><p>{subtitle}</p></div>
      {tag && <span className="tag">{tag}</span>}
    </div>
  );
}

function VulnerabilityChart({ data }) {
  return (
    <div className="chart">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#263244" />
          <XAxis dataKey="name" stroke="#94a3b8" tick={{ fontSize: 11 }} />
          <YAxis stroke="#94a3b8" tick={{ fontSize: 11 }} allowDecimals={false} />
          <Tooltip contentStyle={{ background: "#172235", border: "1px solid #334155", borderRadius: 8 }} />
          <Bar dataKey="count" fill="#38bdf8" radius={[5, 5, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

function EventTable({ data }) {
  return (
    <div className="table-wrap">
      <table>
        <thead><tr><th>STAGE</th><th>TOOL</th><th>STATUS</th><th>DETAILS</th></tr></thead>
        <tbody>
          {data.length ? data.map(event => (
            <tr key={event.id}>
              <td>{event.stage}</td>
              <td>{event.tool}</td>
              <td><span className="status-pill">{event.status}</span></td>
              <td>{event.detail}</td>
            </tr>
          )) : <tr><td colSpan="4">No matching events found.</td></tr>}
        </tbody>
      </table>
    </div>
  );
}

function Overview({ events, severityData, totalFindings, search, onRefresh, loading }) {
  const filteredEvents = events.filter(event =>
    `${event.stage} ${event.tool} ${event.status} ${event.detail}`.toLowerCase().includes(search.toLowerCase())
  );
  const sbomEvent = events.find(event => event.tool.toLowerCase() === "syft");
  const signatureEvent = events.find(event => event.tool.toLowerCase() === "cosign");
  const gateEvent = events.find(event => event.tool.toLowerCase() === "opa");
  const pipelinePassed = gateEvent?.status?.toUpperCase() === "PASSED";

  return (
    <>
      <section className="welcome-row">
        <div><h2>Security Overview</h2><p>Monitor your application security and supply chain health.</p></div>
        <button className="refresh-button" onClick={onRefresh} disabled={loading}>
          <RefreshCw size={16} className={loading ? "spin" : ""} /> {loading ? "Loading..." : "Refresh"}
        </button>
      </section>

      <section className="metrics-grid">
        <MetricCard icon={ShieldCheck} label="Pipeline Status" value={pipelinePassed ? "PASSED" : gateEvent?.status || "UNKNOWN"} note={gateEvent?.detail || "No OPA event found"} color="green" />
        <MetricCard icon={Bug} label="Vulnerabilities" value={totalFindings} note="Sum of reported severity counts" color="orange" />
        <MetricCard icon={Package} label="SBOM Components" value={sbomEvent?.count ?? "—"} note={sbomEvent ? "Reported by Syft" : "No Syft count found"} color="blue" />
        <MetricCard icon={Lock} label="Image Signature" value={signatureEvent?.status === "PASSED" ? "Verified" : signatureEvent?.status || "Unknown"} note={signatureEvent?.detail || "No Cosign event found"} color="purple" />
      </section>

      <section className="content-grid">
        <div className="panel chart-panel">
          <PanelHeading title="Vulnerability Overview" subtitle="Findings by severity" tag="Grype Scan" />
          <VulnerabilityChart data={severityData} />
        </div>
        <div className="panel">
          <PanelHeading title="Security Controls" subtitle="Supply chain verification" />
          {[
            ["SBOM Validation", sbomEvent?.detail || "No Syft event found", sbomEvent?.status === "PASSED" ? CheckCircle : Clock],
            ["Cosign Signature", signatureEvent?.status || "No event found", signatureEvent?.status === "PASSED" ? CheckCircle : Clock],
            ["OPA Deployment Gate", gateEvent?.status || "No event found", gateEvent?.status === "PASSED" ? CheckCircle : Clock],
            ["AI Security Triage", "Dashboard integration pending", Clock],
          ].map(([name, status, Icon]) => (
            <div className="control-row" key={name}>
              <Icon size={19} color={status.toLowerCase().includes("pending") || status.toLowerCase().includes("no event") ? "#f59e0b" : "#22c55e"} />
              <div><strong>{name}</strong><small>{status}</small></div><ChevronRight size={17} />
            </div>
          ))}
        </div>
      </section>

      <section className="panel events-panel">
        <PanelHeading title="Recent Pipeline Events" subtitle="Events loaded from the JSONL file" tag="JSONL Events" />
        <EventTable data={filteredEvents} />
      </section>
    </>
  );
}

function PipelinePage({ events }) {
  const pipelineEvents = events.filter(event =>
    ["syft", "grype", "cosign", "opa", "semgrep", "owasp zap"]
      .includes(event.tool.toLowerCase())
  );

  return (
    <section className="panel">
      <PanelHeading
        title="Pipeline Execution"
        subtitle="DevSecOps pipeline events"
        tag="CI/CD"
      />

      {pipelineEvents.map(event => (
        <div className="control-row" key={event.id}>
          <GitBranch size={20} color="#38bdf8" />
          <div>
            <strong>{event.stage}</strong>
            <small>{event.tool} · {event.detail}</small>
          </div>
          <span className="status-pill">{event.status}</span>
        </div>
      ))}

      {!pipelineEvents.length && (
        <p>No pipeline events found in the JSONL file.</p>
      )}
    </section>
  );
}

function VulnerabilitiesPage({ severityData, totalFindings }) {
  return (
    <>
      <section className="metrics-grid">
        <MetricCard icon={Bug} label="Total Findings" value={totalFindings} note="Sum of reported severity counts" color="orange" />
        <MetricCard icon={AlertTriangle} label="Critical" value={severityData.find(item => item.name === "Critical")?.count ?? 0} note="No Critical event means none reported in this file" color="green" />
        <MetricCard icon={AlertTriangle} label="High" value={severityData.find(item => item.name === "High")?.count ?? 0} note="High severity findings" color="orange" />
      </section>
      <section className="panel chart-panel">
        <PanelHeading title="Vulnerability Findings" subtitle="JSONL severity breakdown" tag="Grype" />
        <VulnerabilityChart data={severityData} />
        {severityData.map(item => <div className="control-row" key={item.name}><strong>{item.name}</strong><span>{item.count} findings</span></div>)}
      </section>
    </>
  );
}

function SBOMPage({ events }) {
  const sbomEvent = events.find(event => event.tool.toLowerCase() === "syft");
  return (
    <section className="panel">
      <PanelHeading title="Software Bill of Materials" subtitle="Application dependency inventory" tag="CycloneDX" />
      <div className="metrics-grid">
        <MetricCard icon={Package} label="Total Components" value={sbomEvent?.count ?? "—"} note="Reported by Syft" color="blue" />
        <MetricCard icon={FileCode} label="SBOM Format" value="CycloneDX" note="Format configured in pipeline; not included in this event" color="purple" />
      </div>
      <div className="control-row"><Package size={20} /><div><strong>SBOM Generator</strong><small>Syft</small></div><span className="status-pill">{sbomEvent?.status || "NOT REPORTED"}</span></div>
      <div className="control-row"><CheckCircle size={20} color="#22c55e" /><div><strong>SBOM Validation</strong><small>{sbomEvent?.detail || "No SBOM validation event found"}</small></div><span className="status-pill">{sbomEvent?.status || "UNKNOWN"}</span></div>
    </section>
  );
}

function AITriagePage({ triageEvents, loading, error, onRefresh }) {
  const reviewed = triageEvents.filter(event => event.status === "REVIEWED").length;
  const open = triageEvents.filter(event => event.status === "OPEN").length;

  return (
    <>
      <section className="metrics-grid">
        <MetricCard icon={Activity} label="Analyzed Findings" value={triageEvents.length} note="AI triage events loaded" color="blue" />
        <MetricCard icon={AlertTriangle} label="Open Findings" value={open} note="Classified as true positives" color="orange" />
        <MetricCard icon={CheckCircle} label="Needs Review" value={reviewed} note="False positives or insufficient evidence" color="green" />
      </section>
      <section className="panel">
        <div className="panel-heading">
          <div><h3>AI Security Triage</h3><p>Finding analysis, risk explanation, evidence and remediation from the AI triage output</p></div>
          <button className="refresh-button" onClick={onRefresh} disabled={loading}>
            <RefreshCw size={16} className={loading ? "spin" : ""} /> {loading ? "Loading..." : "Refresh"}
          </button>
        </div>
        {error && <p role="alert">{error}</p>}
        {!error && loading && <p>Loading AI triage results...</p>}
        {!loading && !error && triageEvents.length === 0 && (
          <div className="empty-state">
            <Clock size={24} color="#f59e0b" />
            <h3>No AI triage results loaded yet</h3>
            <p>Run the AI triage workflow and place its generated <code>ai-triage-events.jsonl</code> file in <code>dashboard/public/data/</code>. Refresh this page to display the results.</p>
          </div>
        )}
        {triageEvents.map(event => (
          <article className="triage-card" key={event.id}>
            <div className="triage-card-header">
              <div><strong>{event.finding_id || event.rule_id || "Security finding"}</strong><small>{event.file || "File not provided"} · {event.rule_id || "No rule ID"}</small></div>
              <span className={event.status === "OPEN" ? "status-pill status-open" : "status-pill"}>{event.status || "UNKNOWN"}</span>
            </div>
            <div className="triage-meta">
              <span>Risk: <strong>{event.severity || "UNKNOWN"}</strong></span>
              <span>Classification: <strong>{(event.classification || "NOT CLASSIFIED").replaceAll("_", " ")}</strong></span>
              <span>Confidence: <strong>{Number.isFinite(Number(event.confidence)) ? event.confidence + "%" : "—"}</strong></span>
            </div>
            <p><strong>Explanation:</strong> {event.detail}</p>
            {Array.isArray(event.evidence) && event.evidence.length > 0 && <div><strong>Evidence</strong><ul>{event.evidence.map((item, index) => <li key={index}>{item}</li>)}</ul></div>}
            {event.remediation && <p><strong>Remediation:</strong> {event.remediation}</p>}
            {event.triage_error && <p className="triage-warning"><strong>Analysis note:</strong> {event.triage_error}</p>}
          </article>
        ))}
      </section>
    </>
  );
}

function SettingsPage() {
  return (
    <section className="panel">
      <PanelHeading title="Dashboard Settings" subtitle="SecureFlow workspace configuration" />
      {[
        ["Workspace", "Agentic AI DevSecOps", Settings],
        ["Security Platform", "CNAPP Security Workspace", ShieldCheck],
        ["Monitoring", "Pipeline event monitoring from public/data/events.jsonl", Activity],
      ].map(([name, detail, Icon]) => <div className="control-row" key={name}><Icon size={20} /><div><strong>{name}</strong><small>{detail}</small></div></div>)}
    </section>
  );
}

function App() {
  const [activeTab, setActiveTab] = useState("Overview");
  const [search, setSearch] = useState("");
  const [events, setEvents] = useState([]);
  const [triageEvents, setTriageEvents] = useState([]);
  const [triageLoading, setTriageLoading] = useState(true);
  const [triageError, setTriageError] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [lastUpdated, setLastUpdated] = useState(null);

  const loadEvents = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const response = await fetch(`${EVENT_FILE}?_=${Date.now()}`, { cache: "no-store" });
      if (!response.ok) throw new Error(`Could not load ${EVENT_FILE} (HTTP ${response.status})`);
      const text = await response.text();
      const parsed = text.split(/\r?\n/).filter(line => line.trim()).map((line, index) => {
        try { return normalizeEvent(JSON.parse(line), index); }
        catch { throw new Error(`Invalid JSON on line ${index + 1} of events.jsonl`); }
      });
      setEvents(parsed);
      setLastUpdated(new Date());
    } catch (err) {
      setError(err.message || "Unable to load pipeline events.");
      setEvents([]);
    } finally {
      setLoading(false);
    }
  }, []);

  const loadTriageEvents = useCallback(async () => {
    setTriageLoading(true);
    setTriageError("");
    try {
      const response = await fetch(`${TRIAGE_EVENT_FILE}?_=${Date.now()}`, { cache: "no-store" });
      if (response.status === 404) {
        setTriageEvents([]);
        return;
      }
      if (!response.ok) throw new Error(`Could not load AI triage data (HTTP ${response.status})`);
      setTriageEvents(parseJsonl(await response.text(), "ai-triage-events.jsonl"));
    } catch (err) {
      setTriageError(err.message || "Unable to load AI triage results.");
      setTriageEvents([]);
    } finally {
      setTriageLoading(false);
    }
  }, []);

  useEffect(() => { loadEvents(); loadTriageEvents(); }, [loadEvents, loadTriageEvents]);

  const severityData = useMemo(() => {
    const counts = Object.fromEntries(SEVERITIES.map(severity => [severity, 0]));
    events.forEach(event => {
      if (event.severity && Object.prototype.hasOwnProperty.call(counts, event.severity)) {
        counts[event.severity] += event.count ?? 1;
      }
    });
    return [
      { name: "Critical", count: counts.CRITICAL },
      { name: "High", count: counts.HIGH },
      { name: "Medium", count: counts.MEDIUM },
      { name: "Low", count: counts.LOW },
      { name: "Negligible", count: counts.NEGLIGIBLE },
      { name: "Unknown", count: counts.UNKNOWN },
    ];
  }, [events]);

  const totalFindings = severityData.reduce((sum, item) => sum + item.count, 0);
  const navigation = [
    ["Overview", LayoutDashboard], ["Pipeline", Activity],
    ["Vulnerabilities", Bug], ["SBOM Explorer", Package],
    ["AI Triage", ShieldCheck], ["Settings", Settings],
  ];

  const renderTabContent = () => {
    switch (activeTab) {
      case "Overview": return <Overview events={events} severityData={severityData} totalFindings={totalFindings} search={search} onRefresh={loadEvents} loading={loading} />;
      case "Pipeline": return <PipelinePage events={events} />;
      case "Vulnerabilities": return <VulnerabilitiesPage severityData={severityData} totalFindings={totalFindings} />;
      case "SBOM Explorer": return <SBOMPage events={events} />;
      case "AI Triage": return <AITriagePage triageEvents={triageEvents} loading={triageLoading} error={triageError} onRefresh={loadTriageEvents} />;
      case "Settings": return <SettingsPage />;
      default: return <h2>Page not found</h2>;
    }
  };

  return (
    <div className="dashboard">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-icon"><ShieldCheck size={25} /></div>
          <div><h2>SecureFlow</h2><span>CNAPP SECURITY</span></div>
        </div>
        <p className="nav-label">WORKSPACE</p>
        {navigation.map(([name, Icon]) => (
          <button key={name} className={`nav-item ${activeTab === name ? "active" : ""}`} onClick={() => setActiveTab(name)}>
            <Icon size={18} />{name}
          </button>
        ))}
        <div className="sidebar-bottom">
          <div className="user-card"><div className="avatar">PJ</div><div><strong>M4 Security</strong><small>Project Engineer</small></div></div>
        </div>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <div><span className="breadcrumb">Workspace / Security Center</span><h1>{activeTab}</h1></div>
          <div className="top-actions">
            <label className="search-box"><Search size={17} /><input placeholder="Search events..." value={search} onChange={event => setSearch(event.target.value)} /></label>
            <button className="icon-button" aria-label="Notifications"><Bell size={19} /></button>
            <div className="avatar">PJ</div>
          </div>
        </header>

        {error && <div className="panel" role="alert"><strong>Unable to load dashboard data</strong><p>{error}</p><button className="refresh-button" onClick={loadEvents}><RefreshCw size={16} /> Try again</button><p>Check that the file exists at dashboard/public/data/events.jsonl.</p></div>}
        {loading && events.length === 0 && !error && <div className="panel">Loading pipeline events...</div>}
        {!loading && !error && events.length === 0 && <div className="panel">The JSONL file loaded, but it contains no events.</div>}
        {(!error && (events.length > 0 || !loading)) && renderTabContent()}

        <footer>
          <span><span className="live-dot" /> SecureFlow Monitoring</span>
          <span>{lastUpdated ? `Last updated ${lastUpdated.toLocaleTimeString()}` : "Waiting for pipeline data"} · Agentic AI • DevSecOps • Supply Chain Security</span>
        </footer>
      </main>
    </div>
  );
}

export default App;

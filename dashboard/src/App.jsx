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

const SEVERITIES = ["CRITICAL", "HIGH", "MEDIUM", "LOW", "NEGLIGIBLE", "UNKNOWN"];

function formatStage(stage = "") {
  const labels = {
    sbom: "SBOM Generation",
    "dependency-scan": "Dependency Scan",
    signature: "Image Signing",
    gate: "Deployment Gate",
    sast: "Static Code Analysis",
    dast: "Dynamic Application Scan",
    "sast-triage": "AI Security Triage",
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
  const triageCount = events.filter(event => event.tool.toLowerCase() === "ai-triage").length;
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
            ["AI Security Triage", triageCount ? `${triageCount} findings imported from M2` : "Waiting for the next M2 pipeline run", triageCount ? CheckCircle : Clock],
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
    ["syft", "grype", "cosign", "opa", "semgrep", "owasp zap", "ai-triage"]
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

function AITriagePage({ events }) {
  const triageEvents = events.filter(event => event.tool.toLowerCase() === "ai-triage");
  const riskOrder = { CRITICAL: 0, HIGH: 1, MEDIUM: 2, LOW: 3, INFO: 4 };
  const sortedEvents = [...triageEvents].sort((a, b) =>
    (riskOrder[a.severity] ?? 5) - (riskOrder[b.severity] ?? 5)
  );
  return (
    <section className="panel">
      <PanelHeading title="AI Security Triage" subtitle="AI-assisted vulnerability analysis" tag="Groq AI" />
      {triageEvents.length === 0 ? (
        <div className="control-row"><Clock size={22} color="#f59e0b" /><div><strong>No AI triage events yet</strong><small>Events will appear after a successful M2 triage workflow run on main.</small></div></div>
      ) : (
        <>
          <div className="metrics-grid">
            <MetricCard icon={ShieldCheck} label="Triaged Findings" value={triageEvents.length} note="Imported from the M2 workflow artifact" color="blue" />
            <MetricCard icon={AlertTriangle} label="True Positives" value={triageEvents.filter(event => event.classification === "TRUE_POSITIVE").length} note="Kept open for human review" color="orange" />
            <MetricCard icon={CheckCircle} label="Reviewed" value={triageEvents.filter(event => event.status === "REVIEWED").length} note="AI classification; not auto-suppressed" color="green" />
          </div>
          {sortedEvents.map(event => (
            <article className="control-row" key={event.id} style={{ alignItems: "flex-start" }}>
              <AlertTriangle size={19} color={event.severity === "CRITICAL" || event.severity === "HIGH" ? "#fb923c" : "#38bdf8"} />
              <div style={{ flex: 1, minWidth: 0 }}>
                <strong>{event.severity || "UNRATED"} · {event.classification || "UNCLASSIFIED"}</strong>
                <small>{event.file || "File not supplied"} {event.rule_id ? `· ${event.rule_id}` : ""} {event.confidence != null ? `· Confidence ${event.confidence}%` : ""}</small>
                <p style={{ marginTop: 8, whiteSpace: "pre-wrap" }}>{event.detail}</p>
                {event.evidence?.length > 0 && <small style={{ display: "block", marginTop: 8 }}>Evidence: {event.evidence.join(" · ")}</small>}
                {event.remediation && <small style={{ display: "block", marginTop: 8 }}>Remediation: {event.remediation}</small>}
                <small style={{ display: "block", marginTop: 8 }}>Status: {event.status} · Run: {event.pipeline_run_id || "unknown"}</small>
              </div>
            </article>
          ))}
        </>
      )}
    </section>
  );
}

function SettingsPage() {
  return (
    <section className="panel">
      <PanelHeading title="Dashboard Settings" subtitle="SecureFlow workspace configuration" />
      {[
        ["Workspace", "Agentic AI DevSecOps", Settings],
        ["Security Platform", "CNAPP Security Workspace", ShieldCheck],
        ["Monitoring", "Automatically synced JSONL pipeline artifacts", Activity],
      ].map(([name, detail, Icon]) => <div className="control-row" key={name}><Icon size={20} /><div><strong>{name}</strong><small>{detail}</small></div></div>)}
    </section>
  );
}

function App() {
  const [activeTab, setActiveTab] = useState("Overview");
  const [search, setSearch] = useState("");
  const [events, setEvents] = useState([]);
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

  useEffect(() => { loadEvents(); }, [loadEvents]);

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
      case "AI Triage": return <AITriagePage events={events} />;
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

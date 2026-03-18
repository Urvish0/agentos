"use client";

import { useEffect, useState } from "react";
import { SystemMetrics, ModelUsage } from "@/lib/types";
import { fetchSystemMetrics } from "@/lib/api";

export default function MetricsPage() {
  const [metrics, setMetrics] = useState<SystemMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadMetrics = () => {
    fetchSystemMetrics()
      .then(setMetrics)
      .catch((err: Error) => setError(err.message))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadMetrics();
    const interval = setInterval(loadMetrics, 10000); // Refresh every 10s
    return () => clearInterval(interval);
  }, []);

  if (loading && !metrics) {
    return (
      <div className="animate-fade-in">
        <div className="skeleton" style={{ width: 180, height: 32, marginBottom: 12 }} />
        <div className="skeleton" style={{ width: 300, height: 16, marginBottom: 32 }} />
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(300px, 1fr))", gap: "20px" }}>
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="skeleton" style={{ height: 160, borderRadius: "var(--radius-lg)" }} />
          ))}
        </div>
      </div>
    );
  }

  if (error || !metrics) {
    return (
      <div className="animate-fade-in">
        <h1 style={{ fontSize: "26px", fontWeight: 700, color: "var(--text-primary)", marginBottom: "8px" }}>Metrics</h1>
        <div className="card" style={{ padding: "40px", textAlign: "center" }}>
          <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="var(--accent-red)" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" style={{ marginBottom: 14 }}>
            <circle cx="12" cy="12" r="10" />
            <line x1="12" y1="8" x2="12" y2="12" />
            <line x1="12" y1="16" x2="12.01" y2="16" />
          </svg>
          <h3 style={{ fontSize: "16px", fontWeight: 600, color: "var(--text-primary)", margin: "0 0 6px" }}>Cannot load metrics</h3>
          <p style={{ fontSize: "13px", color: "var(--text-secondary)", margin: 0 }}>{error || "Check backend connection"}</p>
        </div>
      </div>
    );
  }

  const formatNumber = (num: number) => num.toLocaleString();
  const formatLatency = (ms: number) => (ms >= 1000 ? `${(ms / 1000).toFixed(2)}s` : `${Math.round(ms)}ms`);

  return (
    <div className="animate-fade-in">
      <header style={{ marginBottom: "32px" }}>
        <h1 style={{ fontSize: "28px", fontWeight: 800, color: "var(--text-primary)", letterSpacing: "-0.03em", margin: "0 0 6px" }}>
          System Metrics
        </h1>
        <p style={{ fontSize: "14px", color: "var(--text-secondary)", margin: 0 }}>
          Real-time observability across all agents and tasks.
        </p>
      </header>

      {/* Top Stats Row */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(260px, 1fr))", gap: "20px", marginBottom: "32px" }}>
        <MetricCard
          label="Total Tokens"
          value={formatNumber(metrics.total_tokens)}
          subtext="Lifetime consumption"
          icon={<TokenIcon />}
          color="hsl(210, 100%, 65%)"
        />
        <MetricCard
          label="Avg Latency"
          value={formatLatency(metrics.avg_latency_ms)}
          subtext="Per task execution"
          icon={<LatencyIcon />}
          color="hsl(270, 80%, 70%)"
        />
        <MetricCard
          label="Success Rate"
          value={`${metrics.success_rate}%`}
          subtext="Task completion ratio"
          icon={<SuccessIcon />}
          color="hsl(160, 70%, 55%)"
        />
        <MetricCard
          label="Total Tasks"
          value={formatNumber(metrics.total_tasks)}
          subtext="All-time throughput"
          icon={<TaskIcon />}
          color="hsl(38, 90%, 60%)"
        />
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(400px, 1fr))", gap: "24px" }}>
        {/* Model Usage Breakdown */}
        <section className="card" style={{ padding: "24px" }}>
          <h2 style={{ fontSize: "15px", fontWeight: 600, color: "var(--text-primary)", marginBottom: "20px", display: "flex", alignItems: "center", gap: "8px" }}>
            <span style={{ width: 8, height: 8, borderRadius: "50%", background: "var(--accent-cyan)" }} />
            Token Usage by Model
          </h2>
          <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
            {metrics.model_usage.length > 0 ? (
              metrics.model_usage.sort((a, b) => b.tokens - a.tokens).map((model) => (
                <ModelProgressBar key={model.model} model={model} maxTokens={Math.max(...metrics.model_usage.map(m => m.tokens))} />
              ))
            ) : (
              <p style={{ fontSize: "13px", color: "var(--text-tertiary)", textAlign: "center", padding: "20px" }}>No model data available yet.</p>
            )}
          </div>
        </section>

        {/* Success Rate Gauge Visualization */}
        <section className="card" style={{ padding: "24px", display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center" }}>
          <h2 style={{ fontSize: "15px", fontWeight: 600, color: "var(--text-primary)", alignSelf: "flex-start", marginBottom: "20px", display: "flex", alignItems: "center", gap: "8px" }}>
            <span style={{ width: 8, height: 8, borderRadius: "50%", background: "hsl(160, 70%, 55%)" }} />
            Task Health
          </h2>
          <Gauge value={metrics.success_rate} />
          <div style={{ textAlign: "center", marginTop: "16px" }}>
            <p style={{ fontSize: "13px", color: "var(--text-secondary)", margin: 0 }}>
              <strong>{metrics.success_rate}%</strong> of tasks completed successfully.
            </p>
          </div>
        </section>
      </div>
    </div>
  );
}

function MetricCard({ label, value, subtext, icon, color }: { label: string; value: string; subtext: string; icon: React.ReactNode; color: string }) {
  return (
    <div className="card" style={{ padding: "24px", position: "relative", overflow: "hidden" }}>
      {/* Decorative background glow */}
      <div style={{ position: "absolute", top: "-20px", right: "-20px", width: "100px", height: "100px", background: color, filter: "blur(60px)", opacity: 0.15 }} />
      
      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "16px" }}>
        <span style={{ fontSize: "12px", fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.06em", color: "var(--text-tertiary)" }}>
          {label}
        </span>
        <div style={{ color }}>{icon}</div>
      </div>
      <div style={{ fontSize: "32px", fontWeight: 700, color: "var(--text-primary)", letterSpacing: "-0.03em", marginBottom: "4px" }}>
        {value}
      </div>
      <div style={{ fontSize: "12px", color: "var(--text-tertiary)" }}>{subtext}</div>
    </div>
  );
}

function ModelProgressBar({ model, maxTokens }: { model: ModelUsage; maxTokens: number }) {
  const percentage = maxTokens > 0 ? (model.tokens / maxTokens) * 100 : 0;
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "6px" }}>
      <div style={{ display: "flex", justifyContent: "space-between", fontSize: "13px" }}>
        <span style={{ fontWeight: 500, color: "var(--text-secondary)", fontFamily: "var(--font-mono)" }}>{model.model}</span>
        <span style={{ color: "var(--text-primary)", fontWeight: 600 }}>{model.tokens.toLocaleString()} tokens</span>
      </div>
      <div style={{ height: "6px", background: "var(--bg-tertiary)", borderRadius: "3px", overflow: "hidden" }}>
        <div 
          style={{ 
            height: "100%", 
            width: `${percentage}%`, 
            background: "linear-gradient(90deg, var(--accent-cyan), var(--accent-emerald))",
            borderRadius: "3px",
            transition: "width 1s cubic-bezier(0.4, 0, 0.2, 1)"
          }} 
        />
      </div>
      <div style={{ fontSize: "11px", color: "var(--text-tertiary)" }}>{model.tasks} total tasks</div>
    </div>
  );
}

function Gauge({ value }: { value: number }) {
  const radius = 70;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (value / 100) * circumference;
  
  return (
    <div style={{ position: "relative", width: "160px", height: "160px" }}>
      <svg width="160" height="160" viewBox="0 0 160 160">
        <circle cx="80" cy="80" r={radius} stroke="var(--bg-tertiary)" strokeWidth="12" fill="transparent" />
        <circle 
          cx="80" cy="80" r={radius} 
          stroke="hsl(160, 70%, 55%)" 
          strokeWidth="12" 
          strokeDasharray={circumference} 
          strokeDashoffset={offset} 
          strokeLinecap="round" 
          fill="transparent" 
          transform="rotate(-90 80 80)"
          style={{ transition: "stroke-dashoffset 1.5s ease-out" }}
        />
      </svg>
      <div style={{ position: "absolute", top: "50%", left: "50%", transform: "translate(-50%, -50%)", textAlign: "center" }}>
        <div style={{ fontSize: "32px", fontWeight: 800, color: "var(--text-primary)", letterSpacing: "-0.03em" }}>{value}%</div>
        <div style={{ fontSize: "10px", fontWeight: 600, color: "var(--text-tertiary)", textTransform: "uppercase" }}>Success</div>
      </div>
    </div>
  );
}

// Icons
const TokenIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="12" cy="12" r="8" /><line x1="12" y1="8" x2="12" y2="16" /><line x1="8" y1="12" x2="16" y2="12" />
  </svg>
);

const LatencyIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="12" cy="12" r="10" /><polyline points="12 6 12 12 16 14" />
  </svg>
);

const SuccessIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" /><polyline points="22 4 12 14.01 9 11.01" />
  </svg>
);

const TaskIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M9 11l3 3L22 4" /><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11" />
  </svg>
);

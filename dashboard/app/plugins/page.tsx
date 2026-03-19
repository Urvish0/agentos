"use client";

import { useEffect, useState } from "react";
import { Plugin } from "@/lib/types";
import { fetchPlugins, updatePluginState, installPlugin } from "@/lib/api";
import StatusBadge from "@/components/StatusBadge";

/**
 * Plugin Management Page - Dashboard UI for Phase 10.6
 */
export default function PluginsPage() {
  const [plugins, setPlugins] = useState<Plugin[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [installPath, setInstallPath] = useState("");
  const [isInstalling, setIsInstalling] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);

  useEffect(() => {
    loadPlugins();
  }, []);

  const loadPlugins = async () => {
    setLoading(true);
    try {
      const data = await fetchPlugins();
      setPlugins(data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleToggle = async (name: string, currentState: boolean) => {
    try {
      await updatePluginState(name, !currentState);
      // Refresh list to show "pending_restart" if applicable
      await loadPlugins();
    } catch (err: any) {
      alert("Failed to update plugin: " + err.message);
    }
  };

  const handleInstall = async () => {
    if (!installPath) return;
    setIsInstalling(true);
    try {
      await installPlugin(installPath);
      setInstallPath("");
      setIsModalOpen(false);
      await loadPlugins();
    } catch (err: any) {
      alert("Installation failed: " + err.message);
    } finally {
      setIsInstalling(false);
    }
  };

  return (
    <div className="animate-fade-in" style={{ paddingBottom: "40px" }}>
      {/* Header */}
      <header style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-end", marginBottom: "32px" }}>
        <div>
          <h1 style={{ fontSize: "28px", fontWeight: 800, color: "var(--text-primary)", letterSpacing: "-0.03em", margin: "0 0 8px" }}>
            Plugin Ecosystem
          </h1>
          <p style={{ fontSize: "14px", color: "var(--text-secondary)", margin: 0 }}>
            Extend your AgentOS with custom tools, models, and observability hooks.
          </p>
        </div>
        <button 
          onClick={() => setIsModalOpen(true)}
          className="btn-primary"
          style={{ display: "flex", alignItems: "center", gap: "8px" }}
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            <line x1="12" y1="5" x2="12" y2="19" /><line x1="5" y1="12" x2="19" y2="12" />
          </svg>
          Install Plugin
        </button>
      </header>

      {/* Stats/Overview Row */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: "20px", marginBottom: "32px" }}>
        <div className="card" style={{ padding: "20px" }}>
          <div style={{ fontSize: "11px", fontWeight: 700, color: "var(--text-tertiary)", textTransform: "uppercase", marginBottom: "4px" }}>Active Plugins</div>
          <div style={{ fontSize: "24px", fontWeight: 800, color: "var(--accent-emerald)" }}>
            {plugins.filter(p => p.enabled).length}
          </div>
        </div>
        <div className="card" style={{ padding: "20px" }}>
          <div style={{ fontSize: "11px", fontWeight: 700, color: "var(--text-tertiary)", textTransform: "uppercase", marginBottom: "4px" }}>Total Available</div>
          <div style={{ fontSize: "24px", fontWeight: 800, color: "var(--text-primary)" }}>
            {plugins.length}
          </div>
        </div>
      </div>

      {loading && (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(340px, 1fr))", gap: "20px" }}>
          {[1,2,3].map(i => <div key={i} className="skeleton" style={{ height: "180px", borderRadius: "12px" }} />)}
        </div>
      )}

      {error && (
        <div className="card" style={{ padding: "40px", textAlign: "center", border: "1px solid var(--accent-red-glow)" }}>
          <div style={{ color: "var(--accent-red)", marginBottom: "12px" }}>⚠️ {error}</div>
          <button onClick={loadPlugins} className="btn-shell">Retry Connection</button>
        </div>
      )}

      {!loading && !error && (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(340px, 1fr))", gap: "20px" }}>
          {plugins.map((plugin) => (
            <div key={plugin.name} className="card plugin-card" style={{ 
              padding: "24px", 
              position: "relative",
              border: plugin.enabled ? "1px solid var(--accent-cyan-glow)" : "1px solid var(--border-primary)",
              opacity: plugin.enabled ? 1 : 0.8
            }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "16px" }}>
                <div style={{ 
                  width: "48px", height: "48px", borderRadius: "10px", 
                  background: "var(--bg-tertiary)", display: "flex", alignItems: "center", justifyContent: "center",
                  fontSize: "20px", border: "1px solid var(--border-secondary)"
                }}>
                  {plugin.type === "tool" ? "🛠️" : plugin.type === "metric" ? "📊" : "🔌"}
                </div>
                <div style={{ display: "flex", flexDirection: "column", alignItems: "flex-end", gap: "8px" }}>
                  <label className="switch">
                    <input 
                      type="checkbox" 
                      checked={plugin.enabled} 
                      onChange={() => handleToggle(plugin.name, plugin.enabled)}
                    />
                    <span className="slider"></span>
                  </label>
                  <StatusBadge status={plugin.status || (plugin.enabled ? "active" : "disabled")} />
                </div>
              </div>

              <div>
                <h3 style={{ fontSize: "17px", fontWeight: 700, margin: "0 0 4px" }}>{plugin.name}</h3>
                <div style={{ display: "flex", gap: "8px", fontSize: "11px", fontWeight: 600, textTransform: "uppercase", color: "var(--text-tertiary)" }}>
                  <span>v{plugin.version}</span>
                  <span>•</span>
                  <span>{plugin.type}</span>
                </div>
                <p style={{ fontSize: "13px", color: "var(--text-secondary)", marginTop: "12px", lineHeight: "1.5" }}>
                  Extends AgentOS with custom {plugin.type} capabilities. 
                  {plugin.status === "pending_restart" && (
                    <span style={{ color: "var(--accent-orange)", display: "block", marginTop: "8px", fontWeight: 600 }}>
                      ⚠️ Restart required to apply changes.
                    </span>
                  )}
                </p>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Empty State */}
      {!loading && !error && plugins.length === 0 && (
        <div className="card" style={{ padding: "60px 40px", textAlign: "center" }}>
          <div style={{ fontSize: "40px", marginBottom: "20px" }}>📦</div>
          <h3>No Plugins Found</h3>
          <p style={{ color: "var(--text-secondary)", maxWidth: "400px", margin: "10px auto" }}>
            Plugins allow you to add new skills to your agents. Try installing one from the project root!
          </p>
        </div>
      )}

      {/* Install Modal */}
      {isModalOpen && (
        <div style={{
          position: "fixed", top: 0, left: 0, right: 0, bottom: 0,
          backgroundColor: "rgba(0,0,0,0.85)", backdropFilter: "blur(8px)",
          display: "flex", alignItems: "center", justifyContent: "center", zIndex: 1000,
          padding: "20px"
        }}>
          <div className="card" style={{ width: "100%", maxWidth: "480px", padding: "32px", border: "1px solid var(--border-color)" }}>
            <h2 style={{ fontSize: "20px", fontWeight: 600, marginBottom: "8px" }}>Install New Plugin</h2>
            <p style={{ fontSize: "13px", color: "var(--text-secondary)", marginBottom: "24px" }}>
              Provide the local path or URL to the plugin source directory.
            </p>
            
            <input 
              type="text" 
              value={installPath} 
              onChange={(e) => setInstallPath(e.target.value)}
              placeholder="e.g. ./my_plugins/custom_tool" 
              className="input-custom"
            />

            <div style={{ display: "flex", gap: "12px", marginTop: "32px" }}>
              <button 
                onClick={() => setIsModalOpen(false)}
                className="btn-shell" style={{ flex: 1, textAlign: "center" }}
              >
                Cancel
              </button>
              <button 
                onClick={handleInstall}
                disabled={isInstalling || !installPath}
                className="btn-primary" style={{ flex: 2 }}
              >
                {isInstalling ? "Installing..." : "Install Now"}
              </button>
            </div>
          </div>
        </div>
      )}

      <style jsx>{`
        .plugin-card {
          transition: transform 0.2s, box-shadow 0.2s;
        }
        .plugin-card:hover {
          transform: translateY(-2px);
          box-shadow: 0 8px 24px rgba(0,0,0,0.2);
        }
        .input-custom {
          width: 100%;
          background: var(--bg-tertiary);
          border: 1px solid var(--border-primary);
          color: var(--text-primary);
          padding: 12px;
          border-radius: var(--radius-sm);
          font-size: 13px;
          outline: none;
        }
        .input-custom:focus {
          border-color: var(--accent-cyan);
        }
        /* Toggle Switch CSS */
        .switch {
          position: relative;
          display: inline-block;
          width: 36px;
          height: 20px;
        }
        .switch input { opacity: 0; width: 0; height: 0; }
        .slider {
          position: absolute;
          cursor: pointer;
          top: 0; left: 0; right: 0; bottom: 0;
          background-color: var(--bg-tertiary);
          transition: .4s;
          border-radius: 20px;
          border: 1px solid var(--border-primary);
        }
        .slider:before {
          position: absolute;
          content: "";
          height: 12px;
          width: 12px;
          left: 3px;
          bottom: 3px;
          background-color: var(--text-tertiary);
          transition: .4s;
          border-radius: 50%;
        }
        input:checked + .slider {
          background-color: var(--accent-cyan);
          border-color: var(--accent-cyan);
        }
        input:checked + .slider:before {
          transform: translateX(16px);
          background-color: black;
        }
        .btn-shell {
          background: transparent;
          border: 1px solid var(--border-primary);
          color: var(--text-secondary);
          padding: 8px 16px;
          border-radius: var(--radius-sm);
          cursor: pointer;
          font-size: 13px;
        }
        .btn-shell:hover {
          border-color: var(--text-primary);
          color: var(--text-primary);
        }
      `}</style>
    </div>
  );
}

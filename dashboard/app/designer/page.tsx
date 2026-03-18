"use client";

import React, { useState, useEffect } from 'react';
import WorkflowCanvas from '@/components/designer/WorkflowCanvas';
import { WorkflowNode, WorkflowEdge } from '@/lib/workflow_types';
import { fetchAgents } from '@/lib/api';
import { Agent } from '@/lib/types';

export default function WorkflowDesignerPage() {
  const [nodes, setNodes] = useState<WorkflowNode[]>([
    { id: '1', type: 'trigger', label: 'HTTP Trigger', x: 50, y: 150, data: {}, description: 'Starts the workflow via POST' },
    { id: '2', type: 'agent', label: 'Research Bot', x: 300, y: 150, data: {}, description: 'Searches the web for info' },
  ]);
  const [edges, setEdges] = useState<WorkflowEdge[]>([
    { id: 'e1-2', source: '1', target: '2' },
  ]);
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);
  const [agents, setAgents] = useState<Agent[]>([]);

  useEffect(() => {
    fetchAgents().then(setAgents).catch(console.error);
  }, []);

  const addNode = (type: string, agent?: Agent) => {
    const newNode: WorkflowNode = {
      id: Math.random().toString(36).substr(2, 9),
      type: type as any,
      label: agent ? agent.name : (type.charAt(0).toUpperCase() + type.slice(1)),
      x: 100,
      y: 100,
      data: agent ? { agent_id: agent.id } : {},
      description: agent ? agent.description : `A new ${type} block`
    };
    setNodes([...nodes, newNode]);
  };

  const deleteSelected = () => {
    if (!selectedNodeId) return;
    setNodes(nodes.filter(n => n.id !== selectedNodeId));
    setEdges(edges.filter(e => e.source !== selectedNodeId && e.target !== selectedNodeId));
    setSelectedNodeId(null);
  };

  const exportWorkflow = () => {
    const data = { nodes, edges };
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'workflow.json';
    a.click();
  };

  return (
    <div className="animate-fade-in" style={{ height: 'calc(100vh - 100px)', display: 'flex', flexDirection: 'column' }}>
      {/* Header / Tools */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <div>
          <h1 style={{ fontSize: '24px', fontWeight: 800, color: 'var(--text-primary)', margin: 0 }}>Workflow Designer</h1>
          <p style={{ fontSize: '12px', color: 'var(--text-secondary)', marginTop: '4px' }}>
            Compose complex multi-agent pipelines visually.
          </p>
        </div>
        <div style={{ display: 'flex', gap: '10px' }}>
          <button 
            onClick={exportWorkflow}
            className="card"
            style={{ padding: '8px 16px', fontSize: '12px', fontWeight: 600, background: 'var(--bg-tertiary)', border: '1px solid var(--border-primary)', color: 'var(--text-primary)', cursor: 'pointer' }}
          >
            Export JSON
          </button>
          <button 
            onClick={() => { setNodes([]); setEdges([]); setSelectedNodeId(null); }}
            style={{ 
              padding: '8px 16px', 
              fontSize: '12px', 
              fontWeight: 600, 
              background: 'transparent', 
              border: '1px solid var(--border-primary)', 
              color: 'var(--accent-red)',
              cursor: 'pointer',
              borderRadius: 'var(--radius-md)'
            }}
          >
            Clear Canvas
          </button>
          <button 
            onClick={deleteSelected}
            disabled={!selectedNodeId}
            style={{ 
              padding: '8px 16px', 
              fontSize: '12px', 
              fontWeight: 600, 
              background: selectedNodeId ? 'hsl(0, 50%, 20%)' : 'transparent', 
              border: `1px solid ${selectedNodeId ? 'hsl(0, 50%, 40%)' : 'var(--border-primary)'}`, 
              color: selectedNodeId ? 'hsl(0, 70%, 70%)' : 'var(--text-tertiary)',
              cursor: selectedNodeId ? 'pointer' : 'not-allowed',
              borderRadius: 'var(--radius-md)'
            }}
          >
            Delete Selected
          </button>
        </div>
      </div>

      <div style={{ display: 'flex', gap: '20px', flex: 1, minHeight: 0 }}>
        {/* Sidebar - Component Library */}
        <div className="card" style={{ width: '240px', padding: '16px', display: 'flex', flexDirection: 'column', gap: '20px', overflowY: 'auto' }}>
          <div>
            <h3 style={{ fontSize: '11px', fontWeight: 700, textTransform: 'uppercase', color: 'var(--text-tertiary)', marginBottom: '12px', letterSpacing: '0.05em' }}>
              Base Blocks
            </h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              <LibraryItem label="HTTP Trigger" type="trigger" onClick={() => addNode('trigger')} />
              <LibraryItem label="Condition" type="condition" onClick={() => addNode('condition')} />
              <LibraryItem label="End Point" type="end" onClick={() => addNode('end')} />
            </div>
          </div>

          <div>
            <h3 style={{ fontSize: '11px', fontWeight: 700, textTransform: 'uppercase', color: 'var(--text-tertiary)', marginBottom: '12px', letterSpacing: '0.05em' }}>
              Your Agents
            </h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              {agents.map(agent => (
                <LibraryItem key={agent.id} label={agent.name} type="agent" onClick={() => addNode('agent', agent)} />
              ))}
              {agents.length === 0 && (
                <p style={{ fontSize: '11px', color: 'var(--text-tertiary)', textAlign: 'center' }}>No agents registered</p>
              )}
            </div>
          </div>
        </div>

        {/* Designer Surface */}
        <div style={{ flex: 1, position: 'relative' }}>
          <WorkflowCanvas 
            nodes={nodes}
            edges={edges}
            onNodesChange={setNodes}
            onEdgesChange={setEdges}
            selectedNodeId={selectedNodeId}
            onSelectNode={setSelectedNodeId}
          />
          {/* Canvas Guide */}
          <div style={{ position: 'absolute', bottom: '16px', right: '16px', pointerEvents: 'none', background: 'var(--bg-primary)', padding: '8px 12px', borderRadius: '4px', border: '1px solid var(--border-primary)', fontSize: '10px', color: 'var(--text-tertiary)', display: 'flex', gap: '12px' }}>
            <span>Drag to Move</span>
            <span>Shift + Drag to Pan</span>
          </div>
        </div>
      </div>
    </div>
  );
}

function LibraryItem({ label, type, onClick }: { label: string; type: string; onClick: () => void }) {
  const color = type === 'agent' ? 'var(--accent-cyan)' : type === 'trigger' ? 'var(--accent-emerald)' : 'var(--text-tertiary)';
  return (
    <div 
      onClick={onClick}
      style={{
        padding: '10px 12px',
        background: 'var(--bg-tertiary)',
        border: '1px solid var(--border-primary)',
        borderRadius: 'var(--radius-md)',
        cursor: 'pointer',
        fontSize: '12.5px',
        fontWeight: 500,
        color: 'var(--text-primary)',
        display: 'flex',
        alignItems: 'center',
        gap: '10px',
        transition: 'all 0.2s'
      }}
      onMouseEnter={e => {
        e.currentTarget.style.borderColor = color;
        e.currentTarget.style.background = 'rgba(255,255,255,0.03)';
      }}
      onMouseLeave={e => {
        e.currentTarget.style.borderColor = 'var(--border-primary)';
        e.currentTarget.style.background = 'var(--bg-tertiary)';
      }}
    >
      <div style={{ width: '6px', height: '6px', borderRadius: '50%', background: color }} />
      {label}
    </div>
  );
}

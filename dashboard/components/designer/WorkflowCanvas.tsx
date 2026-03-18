/**
 * WorkflowCanvas — The main interactive surface for the Visual Designer.
 * 
 * Features:
 * - Dot grid background (CSS)
 * - Draggable nodes (Agent/Tool blocks)
 * - Bezier curve connections (SVG)
 * - Panning support
 */

"use client";

import React, { useState, useRef, useEffect } from 'react';
import { WorkflowNode, WorkflowEdge } from '@/lib/workflow_types';

interface WorkflowCanvasProps {
  nodes: WorkflowNode[];
  edges: WorkflowEdge[];
  onNodesChange: (nodes: WorkflowNode[]) => void;
  onEdgesChange: (edges: WorkflowEdge[]) => void;
  selectedNodeId: string | null;
  onSelectNode: (id: string | null) => void;
}

export default function WorkflowCanvas({
  nodes,
  edges,
  onNodesChange,
  onEdgesChange,
  selectedNodeId,
  onSelectNode
}: WorkflowCanvasProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [isDraggingNode, setIsDraggingNode] = useState(false);
  const [draggedNodeId, setDraggedNodeId] = useState<string | null>(null);
  const [offset, setOffset] = useState({ x: 0, y: 0 });
  const [pan, setPan] = useState({ x: 0, y: 0 });
  const [isPanning, setIsPanning] = useState(false);
  const [lastMousePos, setLastMousePos] = useState({ x: 0, y: 0 });

  // Connection State
  const [drawingEdge, setDrawingEdge] = useState<{ sourceId: string; startPos: { x: number; y: number }; currentPos: { x: number; y: number } } | null>(null);

  // Panning logic (Space + Drag or Middle Mouse)
  const handleMouseDown = (e: React.MouseEvent) => {
    if (e.button === 1 || (e.button === 0 && e.shiftKey)) {
      setIsPanning(true);
      setLastMousePos({ x: e.clientX, y: e.clientY });
      return;
    }
    
    // Deselect if clicking on background
    if (e.target === containerRef.current || (e.target as HTMLElement).id === 'svg-canvas') {
      onSelectNode(null);
    }
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    const rect = containerRef.current?.getBoundingClientRect();
    if (!rect) return;

    if (isPanning) {
      const dx = e.clientX - lastMousePos.x;
      const dy = e.clientY - lastMousePos.y;
      setPan(prev => ({ x: prev.x + dx, y: prev.y + dy }));
      setLastMousePos({ x: e.clientX, y: e.clientY });
      return;
    }

    if (drawingEdge) {
      const currentPos = {
        x: e.clientX - rect.left - pan.x,
        y: e.clientY - rect.top - pan.y
      };
      setDrawingEdge({ ...drawingEdge, currentPos });
      return;
    }

    if (isDraggingNode && draggedNodeId) {
      const newX = e.clientX - rect.left - offset.x - pan.x;
      const newY = e.clientY - rect.top - offset.y - pan.y;

      const updatedNodes = nodes.map(node => 
        node.id === draggedNodeId 
          ? { ...node, x: Math.round(newX / 10) * 10, y: Math.round(newY / 10) * 10 } 
          : node
      );
      onNodesChange(updatedNodes);
    }
  };

  const handleMouseUp = (e: React.MouseEvent) => {
    if (drawingEdge) {
      // Logic for completing the edge moved to handlePortMouseUp
      setDrawingEdge(null);
    }
    setIsDraggingNode(false);
    setDraggedNodeId(null);
    setIsPanning(false);
  };

  const startDraggingNode = (id: string, e: React.MouseEvent) => {
    if (drawingEdge) return; // Don't drag while drawing edge
    e.stopPropagation();
    onSelectNode(id);
    const node = nodes.find(n => n.id === id);
    if (!node) return;
    
    const rect = (e.currentTarget as HTMLElement).getBoundingClientRect();
    setOffset({
      x: e.clientX - rect.left,
      y: e.clientY - rect.top
    });
    setDraggedNodeId(id);
    setIsDraggingNode(true);
  };

  const startDrawingEdge = (sourceId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    const node = nodes.find(n => n.id === sourceId);
    if (!node) return;
    
    const startPos = { x: node.x + 180, y: node.y + 40 }; // Start from Right port
    setDrawingEdge({ sourceId, startPos, currentPos: { ...startPos } });
  };

  const completeEdge = (targetId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (drawingEdge && drawingEdge.sourceId !== targetId) {
      const newEdge: WorkflowEdge = {
        id: `e${drawingEdge.sourceId}-${targetId}`,
        source: drawingEdge.sourceId,
        target: targetId
      };
      // Prevent duplicates
      if (!edges.find(e => e.source === newEdge.source && e.target === newEdge.target)) {
        onEdgesChange([...edges, newEdge]);
      }
    }
    setDrawingEdge(null);
  };

  // Bezier curve calculations
  const getPortPos = (id: string, side: 'left' | 'right') => {
    const node = nodes.find(n => n.id === id);
    if (!node) return { x: 0, y: 0 };
    return { 
      x: side === 'left' ? node.x : node.x + 180, 
      y: node.y + 40 
    };
  };

  const getBezierPath = (ax: number, ay: number, bx: number, by: number) => {
    const midX = (ax + bx) / 2;
    return `M ${ax} ${ay} C ${midX} ${ay}, ${midX} ${by}, ${bx} ${by}`;
  };

  return (
    <div 
      ref={containerRef}
      onMouseDown={handleMouseDown}
      onMouseMove={handleMouseMove}
      onMouseUp={handleMouseUp}
      onMouseLeave={handleMouseUp}
      style={{
        width: '100%',
        height: 'calc(100vh - 160px)',
        background: 'var(--bg-secondary)',
        backgroundImage: 'radial-gradient(rgba(255,255,255,0.05) 1px, transparent 1px)',
        backgroundSize: '20px 20px',
        backgroundPosition: `${pan.x}px ${pan.y}px`,
        borderRadius: 'var(--radius-lg)',
        border: '1px solid var(--border-primary)',
        position: 'relative',
        overflow: 'hidden',
        cursor: isPanning ? 'grabbing' : 'crosshair'
      }}
    >
      <div style={{ 
        transform: `translate(${pan.x}px, ${pan.y}px)`, 
        position: 'absolute', 
        top: 0, 
        left: 0,
        pointerEvents: 'none',
        width: '1000%', 
        height: '1000%'
      }}>
        <svg 
          id="svg-canvas"
          style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', pointerEvents: 'none' }}
        >
          <defs>
            <marker id="arrowhead" markerWidth="8" markerHeight="6" refX="8" refY="3" orient="auto">
              <polygon points="0 0, 8 3, 0 6" fill="var(--accent-cyan)" />
            </marker>
          </defs>
          {edges.map(edge => {
            const start = getPortPos(edge.source, 'right');
            const end = getPortPos(edge.target, 'left');
            return (
              <path
                key={edge.id}
                d={getBezierPath(start.x, start.y, end.x, end.y)}
                stroke="var(--accent-cyan)"
                strokeOpacity="0.6"
                strokeWidth="2.5"
                fill="transparent"
                markerEnd="url(#arrowhead)"
              />
            );
          })}
          {drawingEdge && (
            <path
              d={getBezierPath(drawingEdge.startPos.x, drawingEdge.startPos.y, drawingEdge.currentPos.x, drawingEdge.currentPos.y)}
              stroke="var(--accent-cyan)"
              strokeDasharray="4 4"
              strokeWidth="2"
              fill="transparent"
              style={{ opacity: 0.6 }}
            />
          )}
        </svg>

        {nodes.map(node => (
          <div
            key={node.id}
            onMouseDown={(e) => startDraggingNode(node.id, e)}
            style={{
              position: 'absolute',
              left: node.x,
              top: node.y,
              width: '180px',
              minHeight: '80px',
              padding: '12px',
              background: 'var(--bg-primary)',
              border: `1px solid ${selectedNodeId === node.id ? 'var(--accent-cyan)' : 'var(--border-primary)'}`,
              borderRadius: 'var(--radius-md)',
              boxShadow: selectedNodeId === node.id 
                ? '0 0 24px -6px var(--accent-cyan-glow)' 
                : '0 4px 16px rgba(0,0,0,0.4)',
              cursor: isDraggingNode ? 'grabbing' : 'grab',
              pointerEvents: 'auto',
              userSelect: 'none',
              zIndex: draggedNodeId === node.id ? 100 : 1
            }}
          >
            {/* IN PORT (Left) */}
            <div 
              onMouseUp={(e) => completeEdge(node.id, e)}
              style={{
                position: 'absolute', left: '-8px', top: 'calc(50% - 8px)',
                width: '16px', height: '16px', borderRadius: '50%',
                background: 'var(--bg-primary)', border: '2px solid var(--border-primary)',
                zIndex: 10, cursor: 'crosshair', transition: 'all 0.2s'
              }}
              onMouseEnter={e => { e.currentTarget.style.borderColor = 'var(--accent-cyan)'; e.currentTarget.style.transform = 'scale(1.2)'; }}
              onMouseLeave={e => { e.currentTarget.style.borderColor = 'var(--border-primary)'; e.currentTarget.style.transform = 'scale(1)'; }}
            />

            {/* OUT PORT (Right) */}
            <div 
              onMouseDown={(e) => startDrawingEdge(node.id, e)}
              style={{
                position: 'absolute', right: '-8px', top: 'calc(50% - 8px)',
                width: '16px', height: '16px', borderRadius: '50%',
                background: 'var(--bg-primary)', border: '2px solid var(--border-primary)',
                zIndex: 10, cursor: 'crosshair', transition: 'all 0.2s'
              }}
              onMouseEnter={e => { e.currentTarget.style.borderColor = 'var(--accent-cyan)'; e.currentTarget.style.transform = 'scale(1.2)'; }}
              onMouseLeave={e => { e.currentTarget.style.borderColor = 'var(--border-primary)'; e.currentTarget.style.transform = 'scale(1)'; }}
            />

            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
              <div style={{ 
                width: '8px', 
                height: '8px', 
                borderRadius: '50%', 
                background: node.type === 'agent' ? 'var(--accent-cyan)' : node.type === 'trigger' ? 'var(--accent-emerald)' : 'var(--text-tertiary)' 
              }} />
              <span style={{ fontSize: '10px', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.04em', color: 'var(--text-tertiary)' }}>
                {node.type}
              </span>
            </div>
            <div style={{ fontSize: '13px', fontWeight: 600, color: 'var(--text-primary)', marginBottom: '4px' }}>
              {node.label}
            </div>
            <div style={{ fontSize: '11px', color: 'var(--text-secondary)', lineHeight: 1.4, maxHeight: '32px', overflow: 'hidden' }}>
              {node.description || 'No description'}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

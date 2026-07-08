import { useCallback, useState, useEffect } from 'react';
import {
  ReactFlow,
  Node,
  Edge,
  Controls,
  Background,
  MiniMap,
  useNodesState,
  useEdgesState,
  addEdge,
  Connection,
  MarkerType,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { motion } from 'framer-motion';
import { User, Mail, Phone, Globe, Building2, Server, Search } from 'lucide-react';
import { PageHeader, PageContainer } from '../components/layout';
import { GlassCard, AnimatedButton, Badge } from '../components/ui';
import { api } from '../lib/api';
import React from 'react';

const icons: Record<string, any> = {
  username: User,
  email: Mail,
  phone: Phone,
  domain: Globe,
  company: Building2,
  ip: Server,
};

const colors: Record<string, string> = {
  username: '#00d4ff',
  email: '#8b5cf6',
  phone: '#10b981',
  domain: '#f59e0b',
  company: '#ef4444',
  ip: '#6366f1',
};

function createNodes(data: any[]): Node[] {
  return data.map((node, index) => {
    const typeLabel = node.type || 'entity';
    const displayVal = node.label || node.value || node.id;
    return {
      id: String(node.id),
      type: 'default',
      position: { x: (index % 3) * 220 + 50, y: Math.floor(index / 3) * 160 + 50 },
      data: {
        label: (
          <div className="flex items-center gap-2 px-3 py-2 min-w-[150px]">
            <div
              className="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0"
              style={{ backgroundColor: (colors[typeLabel] || '#00d4ff') + '20' }}
            >
              {React.createElement(icons[typeLabel] || User, {
                className: 'w-4 h-4',
                style: { color: colors[typeLabel] || '#00d4ff' }
              })}
            </div>
            <div className="overflow-hidden">
              <p className="text-[10px] text-white/50 capitalize font-mono leading-none">{typeLabel}</p>
              <p className="text-xs font-semibold text-white truncate mt-1">{displayVal}</p>
            </div>
          </div>
        ),
      },
      style: {
        background: 'rgba(13, 21, 32, 0.85)',
        backdropFilter: 'blur(12px)',
        border: `1.5px solid ${colors[typeLabel] || 'rgba(255, 255, 255, 0.1)'}`,
        borderRadius: '12px',
        boxShadow: '0 8px 32px rgba(0, 0, 0, 0.3)',
        color: '#fff',
        padding: 0
      },
    };
  });
}

function createEdges(data: any[]): Edge[] {
  return data.map((edge) => ({
    id: String(edge.id || `${edge.source}-${edge.target}`),
    source: String(edge.source),
    target: String(edge.target),
    type: 'smoothstep',
    animated: true,
    style: {
      stroke: '#00d4ff',
      strokeWidth: 2,
      opacity: 0.6,
    },
    markerEnd: {
      type: MarkerType.ArrowClosed,
      color: '#00d4ff',
    },
    label: edge.type || 'associated',
    labelStyle: { fill: '#fff', fontSize: 9, opacity: 0.7, fontFamily: 'monospace' },
    labelBgStyle: { fill: 'rgba(13, 21, 32, 0.8)', fillOpacity: 0.9 },
    labelBgPadding: [4, 2] as [number, number],
    labelBgBorderRadius: 4,
  }));
}

export default function CorrelationPage() {
  const [filterTarget, setFilterTarget] = useState('');
  const [searching, setSearching] = useState(false);
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);

  const fetchGraph = async (query?: string) => {
    setSearching(true);
    try {
      const res = await api.getCorrelationGraph(query);
      const rawNodes = res.nodes || [];
      const rawEdges = res.edges || [];
      
      setNodes(createNodes(rawNodes));
      setEdges(createEdges(rawEdges));
    } catch (err: any) {
      console.error(err);
      alert(`Failed to load graph: ${err.message || err}`);
    } finally {
      setSearching(false);
    }
  };

  useEffect(() => {
    fetchGraph();
  }, []);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    fetchGraph(filterTarget);
  };

  const onConnect = useCallback(
    (params: Connection) =>
      setEdges((eds) =>
        addEdge(
          {
            ...params,
            animated: true,
            style: { stroke: '#00d4ff', strokeWidth: 2 },
            markerEnd: { type: MarkerType.ArrowClosed, color: '#00d4ff' },
          },
          eds
        )
      ),
    [setEdges]
  );

  return (
    <PageContainer>
      <PageHeader
        title="Correlation Engine"
        subtitle="Visualize and analyze entity relationships"
        action={
          <div className="flex gap-2">
            <Badge variant="info">{nodes.length} Entities</Badge>
            <Badge variant="success">{edges.length} Connections</Badge>
          </div>
        }
      />

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        <div className="lg:col-span-1 space-y-4">
          <GlassCard className="p-4">
            <h3 className="font-medium text-white mb-3 font-mono">Filter Target</h3>
            <form onSubmit={handleSearch} className="space-y-3">
              <input
                type="text"
                value={filterTarget}
                onChange={(e) => setFilterTarget(e.target.value)}
                placeholder="Search target, e.g. admin"
                className="w-full p-2.5 bg-glass-dark border border-glass-border rounded-lg text-white text-sm placeholder:text-white/30 focus:outline-none focus:ring-1 focus:ring-accent-cyan/30"
              />
              <AnimatedButton className="w-full" type="submit" disabled={searching}>
                <Search className="w-4 h-4" />
                {searching ? 'Querying...' : 'Filter Graph'}
              </AnimatedButton>
            </form>
          </GlassCard>

          <GlassCard className="p-4">
            <h3 className="font-medium text-white mb-4 font-mono">Legend</h3>
            <div className="space-y-2">
              {[
                { type: 'Username', color: '#00d4ff', icon: User },
                { type: 'Email', color: '#8b5cf6', icon: Mail },
                { type: 'Phone', color: '#10b981', icon: Phone },
                { type: 'Domain', color: '#f59e0b', icon: Globe },
                { type: 'Company', color: '#ef4444', icon: Building2 },
                { type: 'IP', color: '#6366f1', icon: Server },
              ].map((item) => (
                <div key={item.type} className="flex items-center gap-3">
                  <div
                    className="w-6 h-6 rounded flex items-center justify-center"
                    style={{ backgroundColor: item.color + '20' }}
                  >
                    {React.createElement(item.icon, {
                      className: 'w-3 h-3',
                      style: { color: item.color }
                    })}
                  </div>
                  <span className="text-xs text-white/70">{item.type}</span>
                </div>
              ))}
            </div>
          </GlassCard>

          <GlassCard className="p-4">
            <h3 className="font-medium text-white mb-2 font-mono">Controls</h3>
            <div className="space-y-2 text-xs text-white/50">
              <p>• Drag nodes to rearrange structure</p>
              <p>• Connect nodes by dragging edges</p>
              <p>• Scroll to zoom in/out</p>
              <p>• Click and drag to pan canvas</p>
            </div>
          </GlassCard>
        </div>

        <div className="lg:col-span-3">
          <GlassCard className="h-[600px] overflow-hidden relative">
            {searching && (
              <div className="absolute inset-0 bg-glass-dark/80 backdrop-blur-sm z-10 flex items-center justify-center gap-2">
                <div className="w-5 h-5 border-2 border-accent-cyan/30 border-t-accent-cyan rounded-full animate-spin" />
                <span className="text-sm text-white/70">Rendering correlation map...</span>
              </div>
            )}
            <ReactFlow
              nodes={nodes}
              edges={edges}
              onNodesChange={onNodesChange}
              onEdgesChange={onEdgesChange}
              onConnect={onConnect}
              fitView
              attributionPosition="bottom-left"
            >
              <Background color="rgba(0, 212, 255, 0.08)" gap={20} />
              <Controls
                style={{
                  background: 'rgba(13, 21, 32, 0.8)',
                  border: '1px solid rgba(255, 255, 255, 0.1)',
                  color: 'white',
                }}
              />
              <MiniMap
                style={{
                  background: 'rgba(13, 21, 32, 0.8)',
                  border: '1px solid rgba(255, 255, 255, 0.1)',
                }}
                nodeColor={(node) => {
                  return '#00d4ff';
                }}
                maskColor="rgba(0, 0, 0, 0.6)"
              />
            </ReactFlow>
          </GlassCard>
        </div>
      </div>
    </PageContainer>
  );
}

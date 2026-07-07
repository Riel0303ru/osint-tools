import { useCallback } from 'react';
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
import { User, Mail, Phone, Globe, Building2, Server, Link2 } from 'lucide-react';
import { PageHeader, PageContainer } from '../components/layout';
import { GlassCard, RiskBadge, Badge } from '../components/ui';
import { correlationNodes, correlationEdges } from '../lib/mockData';

const nodeTypes = {
  // Custom node types can be added here
};

function createNodes(data: any[]): Node[] {
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

  return data.map((node, index) => ({
    id: node.id,
    type: 'default',
    position: { x: (index % 3) * 200 + 100, y: Math.floor(index / 3) * 150 + 100 },
    data: {
      label: (
        <div className="flex items-center gap-2 px-3 py-2">
          <div
            className="w-8 h-8 rounded-lg flex items-center justify-center"
            style={{ backgroundColor: colors[node.type] + '20' }}
          >
            {node.value ? null : React.createElement(icons[node.type] || User, {
              className: 'w-4 h-4',
              style: { color: colors[node.type] }
            })}
          </div>
          <div>
            <p className="text-xs text-white/50">{node.type}</p>
            <p className="text-sm font-medium text-white">{node.data?.label || node.id}</p>
          </div>
        </div>
      ),
    },
    style: {
      background: 'rgba(13, 21, 32, 0.8)',
      backdropFilter: 'blur(12px)',
      border: '1px solid rgba(255, 255, 255, 0.1)',
      borderRadius: '12px',
      boxShadow: '0 8px 32px rgba(0, 0, 0, 0.3)',
    },
  }));
}

function createEdges(data: any[]): Edge[] {
  return data.map((edge) => ({
    id: edge.id,
    source: edge.source,
    target: edge.target,
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
    label: edge.type,
    labelStyle: { fill: '#fff', fontSize: 10, opacity: 0.6 },
    labelBgStyle: { fill: 'rgba(0,0,0,0.5)', fillOpacity: 0.8 },
    labelBgPadding: [4, 2] as [number, number],
    labelBgBorderRadius: 4,
  }));
}

export default function CorrelationPage() {
  const [nodes, setNodes, onNodesChange] = useNodesState(
    createNodes([
      { id: '1', type: 'username', data: { label: 'johndoe' } },
      { id: '2', type: 'email', data: { label: 'john@mail.com' } },
      { id: '3', type: 'phone', data: { label: '+1-555-123' } },
      { id: '4', type: 'domain', data: { label: 'johndoe.com' } },
      { id: '5', type: 'company', data: { label: 'TechCorp' } },
      { id: '6', type: 'ip', data: { label: '192.168.1.1' } },
    ])
  );
  const [edges, setEdges, onEdgesChange] = useEdgesState(
    createEdges([
      { id: 'e1', source: '1', target: '2', type: 'linked' },
      { id: 'e2', source: '2', target: '3', type: 'associated' },
      { id: 'e3', source: '2', target: '4', type: 'registered' },
      { id: 'e4', source: '4', target: '5', type: 'employee' },
      { id: 'e5', source: '4', target: '6', type: 'hosted' },
    ])
  );

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
            <Badge variant="info">6 Entities</Badge>
            <Badge variant="success">5 Connections</Badge>
          </div>
        }
      />

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        <div className="lg:col-span-1">
          <GlassCard className="p-4">
            <h3 className="font-medium text-white mb-4">Legend</h3>
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
                    <item.icon className="w-3 h-3" style={{ color: item.color }} />
                  </div>
                  <span className="text-sm text-white/70">{item.type}</span>
                </div>
              ))}
            </div>
          </GlassCard>

          <GlassCard className="p-4 mt-4">
            <h3 className="font-medium text-white mb-4">Controls</h3>
            <div className="space-y-3 text-sm text-white/60">
              <p>Drag nodes to rearrange</p>
              <p>Connect nodes by dragging</p>
              <p>Scroll to zoom</p>
              <p>Click and drag to pan</p>
            </div>
          </GlassCard>
        </div>

        <div className="lg:col-span-3">
          <GlassCard className="h-[600px] overflow-hidden">
            <ReactFlow
              nodes={nodes}
              edges={edges}
              onNodesChange={onNodesChange}
              onEdgesChange={onEdgesChange}
              onConnect={onConnect}
              fitView
              attributionPosition="bottom-left"
            >
              <Background color="rgba(0, 212, 255, 0.1)" gap={20} />
              <Controls
                style={{
                  button: {
                    background: 'rgba(13, 21, 32, 0.8)',
                    border: '1px solid rgba(255, 255, 255, 0.1)',
                    color: 'white',
                  },
                }}
              />
              <MiniMap
                style={{
                  background: 'rgba(13, 21, 32, 0.8)',
                  border: '1px solid rgba(255, 255, 255, 0.1)',
                }}
                nodeColor="#00d4ff"
                maskColor="rgba(0, 0, 0, 0.6)"
              />
            </ReactFlow>
          </GlassCard>
        </div>
      </div>
    </PageContainer>
  );
}

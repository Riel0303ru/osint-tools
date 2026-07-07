import { motion } from 'framer-motion';
import { GitBranch, ZoomIn, ZoomOut, Move, Filter } from 'lucide-react';
import { PageHeader, PageContainer } from '../components/layout';
import { GlassCard, AnimatedButton, Badge } from '../components/ui';

export default function GraphPage() {
  return (
    <PageContainer>
      <PageHeader
        title="Graph Analysis"
        subtitle="Advanced graph visualization and relationship analysis"
        action={
          <div className="flex gap-2">
            <AnimatedButton variant="ghost" size="sm">
              <ZoomIn className="w-4 h-4" />
            </AnimatedButton>
            <AnimatedButton variant="ghost" size="sm">
              <ZoomOut className="w-4 h-4" />
            </AnimatedButton>
            <AnimatedButton variant="ghost" size="sm">
              <Move className="w-4 h-4" />
            </AnimatedButton>
          </div>
        }
      />

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        <div className="lg:col-span-1">
          <GlassCard className="p-4">
            <h3 className="font-medium text-white mb-4 flex items-center gap-2">
              <Filter className="w-4 h-4" />
              Filters
            </h3>
            <div className="space-y-3">
              {['All Entities', 'Users', 'Domains', 'IPs', 'Companies'].map((filter) => (
                <button
                  key={filter}
                  className="w-full text-left px-3 py-2 rounded-lg text-sm text-white/70 hover:bg-white/10 hover:text-white transition-colors"
                >
                  {filter}
                </button>
              ))}
            </div>
          </GlassCard>
        </div>

        <div className="lg:col-span-3">
          <GlassCard className="h-[600px] flex items-center justify-center">
            <div className="text-center">
              <GitBranch className="w-16 h-16 text-white/20 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-white/60 mb-2">Graph Visualization</h3>
              <p className="text-sm text-white/40 max-w-md">
                Visualize complex relationships between entities with advanced graph algorithms
              </p>
              <div className="flex gap-2 justify-center mt-4">
                <Badge variant="info">Community Detection</Badge>
                <Badge variant="success">Path Analysis</Badge>
                <Badge variant="warning">Centrality</Badge>
              </div>
            </div>
          </GlassCard>
        </div>
      </div>
    </PageContainer>
  );
}

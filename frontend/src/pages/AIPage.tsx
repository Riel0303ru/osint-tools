import { motion } from 'framer-motion';
import { Brain, Sparkles, Send, AlertTriangle, TrendingUp, Target } from 'lucide-react';
import { PageHeader, PageContainer } from '../components/layout';
import { GlassCard, AnimatedButton, Badge } from '../components/ui';
import { api } from '../lib/api';
import { cn } from '../lib/utils';
import { useState } from 'react';

export default function AIPage() {
  const [query, setQuery] = useState('Summarize findings');
  const [target, setTarget] = useState('');
  const [targetType, setTargetType] = useState('username');
  const [analyzing, setAnalyzing] = useState(false);
  const [insights, setInsights] = useState<any[]>([
    {
      title: 'AI Intelligence Narrative',
      description: 'Perform a query on any active target using Gemini‑guided cognitive correlations.',
      confidence: 100,
      priority: 'medium',
      type: 'insight',
    }
  ]);

  const handleAnalyze = async () => {
    if (!target.trim()) {
      alert('Please enter a target first.');
      return;
    }
    setAnalyzing(true);
    try {
      const data = await api.analyzeAI(query, target, targetType);
      const analysis = data.ai_analysis || {};
      
      const list = [];
      if (analysis.summary || analysis.narrative) {
        list.push({
          title: 'AI Intelligence Narrative',
          description: analysis.narrative || analysis.summary,
          confidence: Math.round((analysis.confidence || 0.9) * 100),
          priority: analysis.risk_level?.toLowerCase() === 'high' || analysis.risk_level?.toLowerCase() === 'critical' ? 'high' : 'medium',
          type: 'insight'
        });
      }
      if (analysis.threat_pattern) {
        list.push({
          title: 'Threat Pattern Classification',
          description: analysis.threat_pattern,
          confidence: 90,
          priority: 'high',
          type: 'threat'
        });
      }
      if (analysis.mitigation) {
        list.push({
          title: 'Mitigation Directive',
          description: analysis.mitigation,
          confidence: 100,
          priority: 'high',
          type: 'recommendation'
        });
      }

      if (list.length === 0) {
        list.push({
          title: 'Analysis Accomplished',
          description: data.narrative || JSON.stringify(data),
          confidence: 85,
          priority: 'medium',
          type: 'insight'
        });
      }

      setInsights(list);
    } catch (e: any) {
      console.error(e);
      alert(`AI analysis failed: ${e.message || e}`);
    } finally {
      setAnalyzing(false);
    }
  };

  return (
    <PageContainer>
      <PageHeader title="AI Analysis" subtitle="Intelligence insights and automated threat assessment" />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1 space-y-4">
          <GlassCard className="p-4 space-y-3">
            <div className="flex items-center gap-2 mb-2">
              <Sparkles className="w-5 h-5 text-accent-cyan" />
              <h3 className="font-medium text-white font-mono">Ask AI</h3>
            </div>
            <div>
              <label className="text-xs text-white/50 block mb-1">Target Identifier</label>
              <input
                type="text"
                value={target}
                onChange={(e) => setTarget(e.target.value)}
                placeholder="e.g. johndoe, 8.8.8.8, domain.com"
                className="w-full p-2.5 bg-glass-dark border border-glass-border rounded-lg text-white text-sm placeholder:text-white/30 focus:outline-none focus:ring-1 focus:ring-accent-cyan/30"
              />
            </div>
            <div>
              <label className="text-xs text-white/50 block mb-1">Target Type</label>
              <select
                value={targetType}
                onChange={(e) => setTargetType(e.target.value)}
                className="w-full p-2.5 bg-glass-dark border border-glass-border rounded-lg text-white text-sm focus:outline-none focus:ring-1 focus:ring-accent-cyan/30"
              >
                <option value="username">Username</option>
                <option value="email">Email</option>
                <option value="domain">Domain</option>
                <option value="ip">IP Address</option>
                <option value="phone">Phone Number</option>
              </select>
            </div>
            <div>
              <label className="text-xs text-white/50 block mb-1">Prompt Query</label>
              <textarea
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Ask for intelligence insights..."
                className="w-full h-24 p-3 bg-glass-dark border border-glass-border rounded-lg text-white text-sm placeholder:text-white/40 resize-none focus:outline-none focus:ring-1 focus:ring-accent-cyan/30"
              />
            </div>
            <AnimatedButton className="w-full mt-2" onClick={handleAnalyze} disabled={analyzing}>
              {analyzing ? (
                <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              ) : (
                <Send className="w-4 h-4" />
              )}
              Analyze
            </AnimatedButton>
          </GlassCard>

          <GlassCard className="p-4">
            <h4 className="text-sm font-medium text-white/70 mb-3">Quick Actions</h4>
            <div className="space-y-2">
              {['Summarize findings', 'Assess risk level', 'Find correlations', 'Draft mitigation advice'].map(
                (action) => (
                  <button
                    key={action}
                    className="w-full text-left px-3 py-2 rounded-lg text-sm text-white/70 hover:bg-white/10 hover:text-white transition-colors"
                    onClick={() => setQuery(action)}
                  >
                    {action}
                  </button>
                )
              )}
            </div>
          </GlassCard>
        </div>

        <div className="lg:col-span-2">
          {analyzing && (
            <GlassCard className="p-6 mb-4 flex items-center justify-center gap-3">
              <div className="w-6 h-6 border-2 border-accent-cyan/30 border-t-accent-cyan rounded-full animate-spin" />
              <p className="text-sm text-white/60">Gemini is synthesizing target footprints...</p>
            </GlassCard>
          )}

          <div className="space-y-4">
            {insights.map((insight, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
              >
                <GlassCard className="p-4">
                  <div className="flex items-start gap-4">
                    <div
                      className={cn(
                        "p-3 rounded-lg",
                        insight.type === 'threat'
                          ? 'bg-accent-red/10'
                          : insight.type === 'recommendation'
                          ? 'bg-accent-cyan/10'
                          : 'bg-accent-violet/10'
                      )}
                    >
                      {insight.type === 'threat' ? (
                        <AlertTriangle className="w-5 h-5 text-accent-red" />
                      ) : insight.type === 'recommendation' ? (
                        <Target className="w-5 h-5 text-accent-cyan" />
                      ) : (
                        <TrendingUp className="w-5 h-5 text-accent-violet" />
                      )}
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center justify-between mb-1">
                        <h4 className="font-medium text-white">{insight.title}</h4>
                        <Badge variant={insight.priority === 'high' ? 'error' : 'info'}>
                          {insight.priority}
                        </Badge>
                      </div>
                      <p className="text-sm text-white/70 mb-2 leading-relaxed whitespace-pre-wrap">{insight.description}</p>
                      <div className="flex items-center justify-between text-xs text-white/40">
                        <span>Confidence: {insight.confidence}%</span>
                      </div>
                    </div>
                  </div>
                </GlassCard>
              </motion.div>
            ))}
          </div>
        </div>
      </div>
    </PageContainer>
  );
}

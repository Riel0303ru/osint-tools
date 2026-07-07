import { motion } from 'framer-motion';
import { Brain, Sparkles, Send, AlertTriangle, TrendingUp, Target } from 'lucide-react';
import { PageHeader, PageContainer } from '../components/layout';
import { GlassCard, AnimatedButton, Badge, RiskBadge } from '../components/ui';
import { useState } from 'react';

export default function AIPage() {
  const [query, setQuery] = useState('');

  const insights = [
    {
      title: 'Pattern Detected: Coordinated Activity',
      description: 'Analysis reveals synchronized account creation across 3 platforms within 24 hours',
      confidence: 92,
      priority: 'high',
      type: 'threat',
    },
    {
      title: 'Identity Correlation Suggestion',
      description: 'Email and phone records suggest 85% match with known identity profile',
      confidence: 85,
      priority: 'medium',
      type: 'insight',
    },
    {
      title: 'Risk Mitigation Recommendation',
      description: 'Enable MFA for accounts linked to exposed credentials',
      confidence: 100,
      priority: 'high',
      type: 'recommendation',
    },
  ];

  return (
    <PageContainer>
      <PageHeader title="AI Analysis" subtitle="Intelligence insights and automated threat assessment" />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1">
          <GlassCard className="p-4">
            <div className="flex items-center gap-2 mb-4">
              <Sparkles className="w-5 h-5 text-accent-cyan" />
              <h3 className="font-medium text-white">Ask AI</h3>
            </div>
            <textarea
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Ask for intelligence insights..."
              className="w-full h-32 p-3 bg-glass-dark border border-glass-border rounded-lg text-white placeholder:text-white/40 resize-none focus:outline-none focus:ring-2 focus:ring-accent-cyan/30"
            />
            <AnimatedButton className="w-full mt-3">
              <Send className="w-4 h-4" />
              Analyze
            </AnimatedButton>
          </GlassCard>

          <GlassCard className="p-4 mt-4">
            <h4 className="text-sm font-medium text-white/70 mb-3">Quick Actions</h4>
            <div className="space-y-2">
              {['Summarize findings', 'Assess risk level', 'Find correlations', 'Generate report'].map(
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
                      className={`p-3 rounded-lg ${
                        insight.type === 'threat'
                          ? 'bg-accent-red/10'
                          : insight.type === 'recommendation'
                          ? 'bg-accent-cyan/10'
                          : 'bg-accent-violet/10'
                      }`}
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
                      <div className="flex items-center gap-2 mb-1">
                        <h4 className="font-medium text-white">{insight.title}</h4>
                        <Badge variant={insight.priority === 'high' ? 'error' : 'info'}>
                          {insight.priority}
                        </Badge>
                      </div>
                      <p className="text-sm text-white/60 mb-2">{insight.description}</p>
                      <div className="flex items-center justify-between">
                        <span className="text-xs text-white/40">
                          Confidence: {insight.confidence}%
                        </span>
                        <AnimatedButton variant="ghost" size="sm">
                          Investigate
                        </AnimatedButton>
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

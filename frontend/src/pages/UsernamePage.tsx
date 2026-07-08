import { motion } from 'framer-motion';
import { User, ExternalLink, Globe, AlertTriangle, Check, X, Search } from 'lucide-react';
import { PageHeader, PageContainer } from '../components/layout';
import {
  GlassCard,
  AnimatedButton,
  RiskBadge,
  Badge,
  DataCard,
  KeyValueItem,
  SearchInput,
} from '../components/ui';
import { ScanLauncher, ResultsHeader, ResultSection, FindingCard } from '../components/intelligence/ScanLauncher';
import { api } from '../lib/api';
import { cn } from '../lib/utils';
import { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';

export default function UsernamePage() {
  const [searchParams] = useSearchParams();
  const [target, setTarget] = useState('');
  const [scanning, setScanning] = useState(false);
  const [results, setResults] = useState<any>(null);

  const handleScan = async (query: string) => {
    setTarget(query);
    setScanning(true);
    setResults(null);
    try {
      const data = await api.scanUsername(query);
      const linked = data.find((r: any) => r.platform === 'Identity Correlation');
      const persona = data.find((r: any) => r.platform === 'Persona Classification');
      const platforms = data.filter((r: any) => r.platform !== 'Identity Correlation' && r.platform !== 'Persona Classification');
      
      const maxIntelScore = Math.max(...data.map((r: any) => r.intelligence_score || 0), 0);
      let level: 'safe' | 'low' | 'medium' | 'high' | 'critical' = 'safe';
      if (maxIntelScore > 80) level = 'critical';
      else if (maxIntelScore > 60) level = 'high';
      else if (maxIntelScore > 40) level = 'medium';
      else if (maxIntelScore > 20) level = 'low';

      let aiText = '';
      try {
        const aiRes = await api.analyzeAI("Summarize findings and assess digital persona identity", query, "username");
        aiText = aiRes.ai_analysis?.summary || aiRes.ai_analysis?.narrative || aiRes.narrative || '';
      } catch (e) {
        aiText = `Analysis of target "${query}" complete. Persona classification: ${persona?.extra?.persona?.persona || 'unknown'}.`;
      }

      setResults({
        target: query,
        platforms: platforms.map((p: any) => ({
          platform: p.platform,
          exists: p.status === 'FOUND',
          url: p.url,
          confidence: Math.round((p.confidence || 0) * 100),
          extra: p.extra
        })),
        riskScore: { level, score: Math.round(maxIntelScore) },
        timestamp: new Date().toISOString(),
        linkedAccounts: linked?.extra?.linked_accounts || [],
        persona: persona?.extra?.persona || null,
        aiText
      });
    } catch (error: any) {
      console.error(error);
      alert(`Scan failed: ${error.message || error}`);
    } finally {
      setScanning(false);
    }
  };

  useEffect(() => {
    const q = searchParams.get('q');
    if (q) {
      handleScan(q);
    }
  }, [searchParams]);

  return (
    <PageContainer>
      <PageHeader
        title="Username Intelligence"
        subtitle="Discover social media presence and digital footprint analysis"
        action={
          <AnimatedButton variant="secondary">
            <Search className="w-4 h-4" />
            History
          </AnimatedButton>
        }
      />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Scan Panel */}
        <div className="lg:col-span-1">
          <ScanLauncher
            type="username"
            onScan={handleScan}
            placeholder="Enter username to investigate..."
          />

          {scanning && (
            <motion.div
              className="mt-4"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
            >
              <GlassCard className="p-4">
                <div className="flex items-center gap-3">
                  <motion.div
                    animate={{ rotate: 360 }}
                    transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                    className="w-6 h-6 border-2 border-accent-cyan/30 border-t-accent-cyan rounded-full"
                  />
                  <div>
                    <p className="text-sm font-medium text-white">Scanning...</p>
                    <p className="text-xs text-white/50">Analyzing platforms</p>
                  </div>
                </div>
              </GlassCard>
            </motion.div>
          )}
        </div>

        {/* Results Panel */}
        <div className="lg:col-span-2">
          {results ? (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="space-y-6"
            >
              <ResultsHeader
                title="Username Analysis"
                target={results.target}
                riskScore={results.riskScore}
                timestamp={results.timestamp}
                exportable
                onExport={() => {
                  api.generateReport(results.target).then((res) => {
                    if (res.pdf_generated) {
                      window.open(api.getDownloadReportUrl(results.target), '_blank');
                    } else {
                      alert('Report generated but PDF file download is unavailable.');
                    }
                  }).catch(err => alert(`Report generation failed: ${err.message}`));
                }}
              />

              {/* Platform Discoveries */}
              <ResultSection title="Platform Discoveries">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {results.platforms.map((platform: any, index: number) => (
                    <motion.div
                      key={platform.platform}
                      className={cn(
                        'p-4 rounded-lg border transition-all',
                        platform.exists
                          ? 'border-accent-cyan/20 bg-accent-cyan/5'
                          : 'border-white/5 bg-white/[0.02]'
                      )}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.05 }}
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          <div
                            className={cn(
                              'w-10 h-10 rounded-lg flex items-center justify-center',
                              platform.exists
                                ? 'bg-accent-cyan/20 text-accent-cyan'
                                : 'bg-white/5 text-white/30'
                            )}
                          >
                            <Globe className="w-5 h-5" />
                          </div>
                          <div>
                            <h4 className="font-medium text-white">
                              {platform.platform}
                            </h4>
                            {platform.exists && platform.url && (
                              <a
                                href={platform.url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-xs text-accent-cyan hover:underline flex items-center gap-1"
                              >
                                View Profile
                                <ExternalLink className="w-3 h-3" />
                              </a>
                            )}
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          {platform.exists ? (
                            <Check className="w-5 h-5 text-accent-emerald" />
                          ) : (
                            <X className="w-5 h-5 text-white/30" />
                          )}
                          <span className="text-xs text-white/50">
                            {platform.confidence}%
                          </span>
                        </div>
                      </div>
                    </motion.div>
                  ))}
                </div>
              </ResultSection>

              {/* Identity Correlations */}
              {results.linkedAccounts && results.linkedAccounts.length > 0 && (
                <ResultSection title="Identity Correlations" defaultOpen={true}>
                  <div className="space-y-3">
                    {results.linkedAccounts.map((acc: any, i: number) => (
                      <FindingCard
                        key={i}
                        title="Platform Association Found"
                        description={`Linked profile match between ${acc.platform_a} and ${acc.platform_b}`}
                        severity={acc.confidence > 0.8 ? "medium" : "low"}
                        source="Cross-Platform Engine"
                        action={
                          acc.url_b ? (
                            <a href={acc.url_b} target="_blank" rel="noopener noreferrer">
                              <AnimatedButton variant="ghost" size="sm">
                                <ExternalLink className="w-4 h-4" />
                              </AnimatedButton>
                            </a>
                          ) : undefined
                        }
                      />
                    ))}
                  </div>
                </ResultSection>
              )}

              {/* AI Insights */}
              {results.aiText && (
                <ResultSection title="AI Intelligence Summary" defaultOpen={true}>
                  <GlassCard variant="light" className="p-4">
                    <p className="text-sm text-white/80 leading-relaxed whitespace-pre-wrap">
                      {results.aiText}
                    </p>
                    {results.persona && (
                      <div className="flex gap-2 mt-4">
                        <Badge variant="info">Digital Persona: {results.persona.persona?.toUpperCase()}</Badge>
                        <Badge variant="success">Confidence: {Math.round(results.persona.confidence * 100)}%</Badge>
                      </div>
                    )}
                  </GlassCard>
                </ResultSection>
              )}
            </motion.div>
          ) : (
            <GlassCard className="p-12 flex flex-col items-center justify-center text-center">
              <User className="w-16 h-16 text-white/20 mb-4" />
              <h3 className="text-lg font-medium text-white/60 mb-2">
                No Username Scanned
              </h3>
              <p className="text-sm text-white/40 max-w-md">
                Enter a username in the scan panel to begin intelligence analysis.
                Results will appear here with platform discoveries, correlations,
                and AI insights.
              </p>
            </GlassCard>
          )}
        </div>
      </div>
    </PageContainer>
  );
}


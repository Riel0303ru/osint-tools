import { motion } from 'framer-motion';
import { Skull, AlertTriangle, Search, Database } from 'lucide-react';
import { PageHeader, PageContainer } from '../components/layout';
import { GlassCard, RiskBadge, Badge } from '../components/ui';
import { ScanLauncher, ResultsHeader, ResultSection } from '../components/intelligence/ScanLauncher';
import { useState } from 'react';

export default function DarkWebPage() {
  const [results, setResults] = useState<any>(null);

  const handleScan = (query: string) => {
    setTimeout(() => {
      setResults({
        target: query,
        breaches: [{ name: 'Collection #1', date: '2019-01', records: '772M' }],
        mentions: [{ platform: 'Forum', date: '2024-01', content: 'User data posted' }],
        exposedData: [{ type: 'Email', count: 45 }],
        riskScore: { level: 'critical', score: 85 },
        timestamp: new Date().toISOString(),
      });
    }, 1500);
  };

  return (
    <PageContainer>
      <PageHeader title="Dark Web Intelligence" subtitle="Breach monitoring and data exposure analysis" />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1">
          <ScanLauncher type="darkweb" onScan={handleScan} placeholder="Enter email or keyword..." />
        </div>

        <div className="lg:col-span-2">
          {results ? (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-6">
              <ResultsHeader title="Dark Web Analysis" target={results.target} riskScore={results.riskScore} timestamp={results.timestamp} />

              <ResultSection title="Breach Exposure">
                <div className="space-y-3">
                  {results.breaches.map((breach: any, i: number) => (
                    <div key={i} className="p-4 rounded-lg border border-accent-red/30 bg-accent-red/5">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <AlertTriangle className="w-4 h-4 text-accent-red" />
                          <span className="font-medium text-white">{breach.name}</span>
                        </div>
                        <div className="text-right">
                          <p className="text-xs text-white/50">{breach.date}</p>
                          <p className="text-sm text-accent-red">{breach.records} records</p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </ResultSection>

              <ResultSection title="Exposed Data">
                <div className="grid grid-cols-3 gap-4">
                  {results.exposedData.map((data: any, i: number) => (
                    <GlassCard key={i} variant="light" className="p-4 text-center">
                      <Database className="w-5 h-5 text-accent-red mx-auto mb-2" />
                      <p className="text-2xl font-bold text-white">{data.count}</p>
                      <p className="text-xs text-white/50">{data.type} Exposed</p>
                    </GlassCard>
                  ))}
                </div>
              </ResultSection>

              <ResultSection title="Dark Web Mentions">
                <div className="space-y-2">
                  {results.mentions.map((mention: any, i: number) => (
                    <div key={i} className="p-3 bg-white/5 rounded-lg">
                      <div className="flex items-center justify-between mb-1">
                        <Badge variant="error">{mention.platform}</Badge>
                        <span className="text-xs text-white/40">{mention.date}</span>
                      </div>
                      <p className="text-sm text-white/80">{mention.content}</p>
                    </div>
                  ))}
                </div>
              </ResultSection>
            </motion.div>
          ) : (
            <GlassCard className="p-12 flex flex-col items-center justify-center text-center">
              <Skull className="w-16 h-16 text-white/20 mb-4" />
              <h3 className="text-lg font-medium text-white/60">No Dark Web Scan</h3>
              <p className="text-sm text-white/40">Enter a target to check for data exposures</p>
            </GlassCard>
          )}
        </div>
      </div>
    </PageContainer>
  );
}

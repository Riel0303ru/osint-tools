import { motion } from 'framer-motion';
import { Mail, AlertTriangle, Shield, Globe, Database, ExternalLink } from 'lucide-react';
import { PageHeader, PageContainer } from '../components/layout';
import { GlassCard, AnimatedButton, RiskBadge, Badge, DataCard } from '../components/ui';
import { ScanLauncher, ResultsHeader, ResultSection, FindingCard } from '../components/intelligence/ScanLauncher';
import { breachData } from '../lib/mockData';
import { cn } from '../lib/utils';
import { useState } from 'react';

export default function EmailPage() {
  const [results, setResults] = useState<any>(null);
  const [scanning, setScanning] = useState(false);

  const handleScan = (query: string) => {
    setScanning(true);
    setTimeout(() => {
      setScanning(false);
      setResults({
        target: query,
        breaches: breachData,
        reputation: { score: 75, deliverable: true, disposable: false },
        riskScore: { level: 'high', score: 72 },
        timestamp: new Date().toISOString(),
      });
    }, 2000);
  };

  return (
    <PageContainer>
      <PageHeader
        title="Email Intelligence"
        subtitle="Breach detection, reputation analysis, and email validation"
      />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1">
          <ScanLauncher
            type="email"
            onScan={handleScan}
            placeholder="Enter email address..."
          />
        </div>

        <div className="lg:col-span-2">
          {results ? (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="space-y-6"
            >
              <ResultsHeader
                title="Email Analysis"
                target={results.target}
                riskScore={results.riskScore}
                timestamp={results.timestamp}
                exportable
                onExport={() => console.log('Export')}
              />

              {/* Breach Results */}
              <ResultSection title="Data Breach Exposure">
                <div className="space-y-3">
                  {results.breaches.map((breach: any, index: number) => (
                    <motion.div
                      key={breach.name}
                      className="p-4 rounded-lg border border-accent-red/20 bg-accent-red/5"
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: index * 0.1 }}
                    >
                      <div className="flex items-start justify-between">
                        <div>
                          <h4 className="font-medium text-white flex items-center gap-2">
                            <AlertTriangle className="w-4 h-4 text-accent-red" />
                            {breach.name}
                          </h4>
                          <p className="text-xs text-white/50 mt-1">
                            Breached: {new Date(breach.breachDate).toLocaleDateString()}
                          </p>
                        </div>
                        <Badge variant="error">{breach.pwnCount.toLocaleString()} affected</Badge>
                      </div>
                      <div className="flex gap-2 mt-3">
                        {breach.dataClasses.map((dc: string) => (
                          <span
                            key={dc}
                            className="text-xs px-2 py-1 bg-white/10 rounded text-white/70"
                          >
                            {dc}
                          </span>
                        ))}
                      </div>
                    </motion.div>
                  ))}
                </div>
              </ResultSection>

              {/* Email Reputation */}
              <ResultSection title="Email Reputation">
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <GlassCard variant="light" className="p-4 text-center">
                    <Shield className="w-6 h-6 text-accent-emerald mx-auto mb-2" />
                    <p className="text-xs text-white/50">Deliverable</p>
                    <p className="text-lg font-bold text-accent-emerald">Yes</p>
                  </GlassCard>
                  <GlassCard variant="light" className="p-4 text-center">
                    <Database className="w-6 h-6 text-white/50 mx-auto mb-2" />
                    <p className="text-xs text-white/50">Disposable</p>
                    <p className="text-lg font-bold text-white">No</p>
                  </GlassCard>
                  <GlassCard variant="light" className="p-4 text-center">
                    <Globe className="w-6 h-6 text-white/50 mx-auto mb-2" />
                    <p className="text-xs text-white/50">MX Valid</p>
                    <p className="text-lg font-bold text-white">Yes</p>
                  </GlassCard>
                  <GlassCard variant="light" className="p-4 text-center">
                    <Shield className="w-6 h-6 text-accent-amber mx-auto mb-2" />
                    <p className="text-xs text-white/50">Reputation</p>
                    <p className="text-lg font-bold text-accent-amber">75%</p>
                  </GlassCard>
                </div>
              </ResultSection>
            </motion.div>
          ) : (
            <GlassCard className="p-12 flex flex-col items-center justify-center text-center">
              <Mail className="w-16 h-16 text-white/20 mb-4" />
              <h3 className="text-lg font-medium text-white/60 mb-2">
                No Email Analyzed
              </h3>
              <p className="text-sm text-white/40 max-w-md">
                Enter an email address to check for breaches, validate reputation,
                and analyze email intelligence data.
              </p>
            </GlassCard>
          )}
        </div>
      </div>
    </PageContainer>
  );
}

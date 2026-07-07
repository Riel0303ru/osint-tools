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
import { platformDiscoveryData } from '../lib/mockData';
import { cn } from '../lib/utils';
import { useState } from 'react';

export default function UsernamePage() {
  const [target, setTarget] = useState('');
  const [scanning, setScanning] = useState(false);
  const [results, setResults] = useState<any>(null);

  const handleScan = (query: string) => {
    setTarget(query);
    setScanning(true);
    // Simulate scan
    setTimeout(() => {
      setScanning(false);
      setResults({
        target: query,
        platforms: platformDiscoveryData,
        riskScore: { level: 'medium', score: 45 },
        timestamp: new Date().toISOString(),
      });
    }, 2000);
  };

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
                onExport={() => console.log('Export')}
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
              <ResultSection title="Identity Correlations" defaultOpen={false}>
                <div className="space-y-3">
                  <FindingCard
                    title="Email Address Found"
                    description="Associated email detected on GitHub profile"
                    severity="medium"
                    source="GitHub"
                    action={
                      <AnimatedButton variant="ghost" size="sm">
                        <ExternalLink className="w-4 h-4" />
                      </AnimatedButton>
                    }
                  />
                  <FindingCard
                    title="Name Pattern Match"
                    description="DisplayName matches expected format across 3 platforms"
                    severity="low"
                    source="Cross-Platform"
                  />
                </div>
              </ResultSection>

              {/* AI Insights */}
              <ResultSection title="AI Intelligence Summary" defaultOpen={false}>
                <GlassCard variant="light" className="p-4">
                  <p className="text-sm text-white/80 leading-relaxed">
                    The username "{results.target}" has a significant digital footprint across
                    multiple platforms. A correlation analysis suggests a high likelihood that
                    this identity is authentic, with consistent profile attributes across GitHub,
                    LinkedIn, and Twitter. No suspicious activity patterns were detected.
                    Consider expanding the investigation to include email intelligence for
                    a more comprehensive identity profile.
                  </p>
                  <div className="flex gap-2 mt-4">
                    <Badge variant="success">Consistent Identity</Badge>
                    <Badge variant="info">Professional Presence</Badge>
                  </div>
                </GlassCard>
              </ResultSection>
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

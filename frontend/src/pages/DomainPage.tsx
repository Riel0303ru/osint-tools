import { motion } from 'framer-motion';
import { Globe, Server, Shield, Lock, Database, ExternalLink } from 'lucide-react';
import { PageHeader, PageContainer } from '../components/layout';
import { GlassCard, AnimatedButton, RiskBadge, Badge, KeyValueItem } from '../components/ui';
import { ScanLauncher, ResultsHeader, ResultSection } from '../components/intelligence/ScanLauncher';
import { domainIntelligenceData } from '../lib/mockData';
import { cn } from '../lib/utils';
import { useState } from 'react';

export default function DomainPage() {
  const [results, setResults] = useState<any>(null);
  const [scanning, setScanning] = useState(false);

  const handleScan = (query: string) => {
    setScanning(true);
    setTimeout(() => {
      setScanning(false);
      setResults({
        target: query,
        ...domainIntelligenceData,
        riskScore: { level: 'low', score: 25 },
        timestamp: new Date().toISOString(),
      });
    }, 2000);
  };

  return (
    <PageContainer>
      <PageHeader
        title="Domain Intelligence"
        subtitle="WHOIS, DNS records, SSL analysis, and security assessment"
      />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1">
          <ScanLauncher
            type="domain"
            onScan={handleScan}
            placeholder="Enter domain name..."
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
                title="Domain Analysis"
                target={results.target}
                riskScore={results.riskScore}
                timestamp={results.timestamp}
                exportable
                onExport={() => console.log('Export')}
              />

              {/* WHOIS Data */}
              <ResultSection title="WHOIS Information">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-1">
                    <KeyValueItem label="Registrar" value={results.whois.registrar} />
                    <KeyValueItem label="Created" value={new Date(results.whois.createdDate).toLocaleDateString()} />
                    <KeyValueItem label="Expiry" value={new Date(results.whois.expiryDate).toLocaleDateString()} />
                    <KeyValueItem label="Organization" value={results.whois.registrant.organization} />
                    <KeyValueItem label="Country" value={results.whois.registrant.country} />
                  </div>
                  <div className="space-y-1">
                    <h4 className="text-sm font-medium text-white/70 mb-2">Name Servers</h4>
                    {results.whois.nameServers.map((ns: string) => (
                      <div key={ns} className="text-xs text-white/60 bg-white/5 px-3 py-2 rounded">
                        {ns}
                      </div>
                    ))}
                  </div>
                </div>
              </ResultSection>

              {/* DNS Records */}
              <ResultSection title="DNS Records">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <h4 className="text-sm font-medium text-accent-cyan mb-2 flex items-center gap-2">
                      <Server className="w-4 h-4" /> A Records
                    </h4>
                    {results.dns.a.map((ip: string) => (
                      <div key={ip} className="text-xs text-white/70 bg-white/5 px-3 py-2 rounded mb-1 font-mono">
                        {ip}
                      </div>
                    ))}
                  </div>
                  <div>
                    <h4 className="text-sm font-medium text-accent-violet mb-2 flex items-center gap-2">
                      <Server className="w-4 h-4" /> MX Records
                    </h4>
                    {results.dns.mx.map((mx: any) => (
                      <div key={mx.exchange} className="text-xs text-white/70 bg-white/5 px-3 py-2 rounded mb-1 font-mono">
                        {mx.priority} {mx.exchange}
                      </div>
                    ))}
                  </div>
                  <div>
                    <h4 className="text-sm font-medium text-white/70 mb-2 flex items-center gap-2">
                      <Shield className="w-4 h-4" /> TXT Records
                    </h4>
                    {results.dns.txt.map((txt: string, i: number) => (
                      <div key={i} className="text-xs text-white/60 bg-white/5 px-3 py-2 rounded mb-1 line-clamp-1">
                        {txt}
                      </div>
                    ))}
                  </div>
                </div>
              </ResultSection>

              {/* SSL Certificate */}
              <ResultSection title="SSL Certificate">
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <GlassCard variant="light" className="p-4 text-center">
                    <Lock className="w-6 h-6 text-accent-emerald mx-auto mb-2" />
                    <p className="text-xs text-white/50">Valid</p>
                    <p className="text-lg font-bold text-accent-emerald">Yes</p>
                  </GlassCard>
                  <GlassCard variant="light" className="p-4 text-center">
                    <Shield className="w-6 h-6 text-white/50 mx-auto mb-2" />
                    <p className="text-xs text-white/50">Issuer</p>
                    <p className="text-sm font-bold text-white truncate">{results.ssl.issuer}</p>
                  </GlassCard>
                  <GlassCard variant="light" className="p-4 text-center">
                    <Database className="w-6 h-6 text-white/50 mx-auto mb-2" />
                    <p className="text-xs text-white/50">Valid From</p>
                    <p className="text-sm font-bold text-white">{new Date(results.ssl.validFrom).toLocaleDateString()}</p>
                  </GlassCard>
                  <GlassCard variant="light" className="p-4 text-center">
                    <Database className="w-6 h-6 text-white/50 mx-auto mb-2" />
                    <p className="text-xs text-white/50">Valid To</p>
                    <p className="text-sm font-bold text-white">{new Date(results.ssl.validTo).toLocaleDateString()}</p>
                  </GlassCard>
                </div>
              </ResultSection>

              {/* Technologies */}
              <ResultSection title="Technology Stack">
                <div className="flex flex-wrap gap-2">
                  {results.technologies.map((tech: any) => (
                    <Badge key={tech.name} variant={tech.confidence > 80 ? 'success' : 'default'}>
                      {tech.name}
                      <span className="ml-1 opacity-60">{tech.confidence}%</span>
                    </Badge>
                  ))}
                </div>
              </ResultSection>

              {/* Subdomains */}
              <ResultSection title="Subdomains" defaultOpen={false}>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                  {results.subdomains.map((sub: any) => (
                    <div
                      key={sub.subdomain}
                      className={cn(
                        'p-3 rounded-lg flex items-center justify-between',
                        sub.status === 'active' ? 'bg-accent-emerald/10 border border-accent-emerald/20' : 'bg-white/5'
                      )}
                    >
                      <div>
                        <span className="text-sm text-white">{sub.subdomain}.{results.target}</span>
                        {sub.ip && (
                          <p className="text-xs text-white/50 font-mono">{sub.ip}</p>
                        )}
                      </div>
                      <Badge variant={sub.status === 'active' ? 'success' : 'default'}>
                        {sub.status}
                      </Badge>
                    </div>
                  ))}
                </div>
              </ResultSection>
            </motion.div>
          ) : (
            <GlassCard className="p-12 flex flex-col items-center justify-center text-center">
              <Globe className="w-16 h-16 text-white/20 mb-4" />
              <h3 className="text-lg font-medium text-white/60 mb-2">
                No Domain Analyzed
              </h3>
              <p className="text-sm text-white/40 max-w-md">
                Enter a domain to analyze WHOIS, DNS records, SSL certificates,
                technologies, and security posture.
              </p>
            </GlassCard>
          )}
        </div>
      </div>
    </PageContainer>
  );
}

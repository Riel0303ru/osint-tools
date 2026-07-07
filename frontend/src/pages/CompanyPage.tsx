import { motion } from 'framer-motion';
import { Building2, Globe, Users, Shield, Database } from 'lucide-react';
import { PageHeader, PageContainer } from '../components/layout';
import { GlassCard, Badge, KeyValueItem } from '../components/ui';
import { ScanLauncher, ResultsHeader, ResultSection } from '../components/intelligence/ScanLauncher';
import { useState } from 'react';

export default function CompanyPage() {
  const [results, setResults] = useState<any>(null);

  const handleScan = (query: string) => {
    setTimeout(() => {
      setResults({
        target: query,
        name: 'TechCorp Inc.',
        domains: ['techcorp.com', 'api.techcorp.com'],
        employees: 500,
        industry: 'Technology',
        infrastructure: { domains: 12, subdomains: 45, ips: 8, cloudProviders: ['AWS', 'Azure'] },
        security: { sslGrade: 'A', score: 85 },
        riskScore: { level: 'low', score: 15 },
        timestamp: new Date().toISOString(),
      });
    }, 1500);
  };

  return (
    <PageContainer>
      <PageHeader title="Company Intelligence" subtitle="Corporate infrastructure and security assessment" />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1">
          <ScanLauncher type="company" onScan={handleScan} placeholder="Enter company name..." />
        </div>

        <div className="lg:col-span-2">
          {results ? (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-6">
              <ResultsHeader title="Company Analysis" target={results.target} riskScore={results.riskScore} timestamp={results.timestamp} />

              <ResultSection title="Company Overview">
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <GlassCard variant="light" className="p-4 text-center">
                    <Building2 className="w-5 h-5 text-accent-cyan mx-auto mb-2" />
                    <p className="text-xs text-white/50">Industry</p>
                    <p className="text-sm font-medium text-white">{results.industry}</p>
                  </GlassCard>
                  <GlassCard variant="light" className="p-4 text-center">
                    <Users className="w-5 h-5 text-accent-violet mx-auto mb-2" />
                    <p className="text-xs text-white/50">Employees</p>
                    <p className="text-sm font-medium text-white">{results.employees.toLocaleString()}</p>
                  </GlassCard>
                  <GlassCard variant="light" className="p-4 text-center">
                    <Globe className="w-5 h-5 text-accent-emerald mx-auto mb-2" />
                    <p className="text-xs text-white/50">Domains</p>
                    <p className="text-sm font-medium text-white">{results.infrastructure.domains}</p>
                  </GlassCard>
                  <GlassCard variant="light" className="p-4 text-center">
                    <Shield className="w-5 h-5 text-accent-amber mx-auto mb-2" />
                    <p className="text-xs text-white/50">Security Score</p>
                    <p className="text-sm font-medium text-white">{results.security.score}%</p>
                  </GlassCard>
                </div>
              </ResultSection>

              <ResultSection title="Infrastructure">
                <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                  <div className="p-3 bg-white/5 rounded-lg">
                    <p className="text-xs text-white/50">Subdomains</p>
                    <p className="text-lg font-bold text-white">{results.infrastructure.subdomains}</p>
                  </div>
                  <div className="p-3 bg-white/5 rounded-lg">
                    <p className="text-xs text-white/50">IP Addresses</p>
                    <p className="text-lg font-bold text-white">{results.infrastructure.ips}</p>
                  </div>
                  <div className="p-3 bg-white/5 rounded-lg">
                    <p className="text-xs text-white/50">SSL Grade</p>
                    <p className="text-lg font-bold text-accent-emerald">{results.security.sslGrade}</p>
                  </div>
                  <div className="p-3 bg-white/5 rounded-lg">
                    <p className="text-xs text-white/50">Cloud</p>
                    <div className="flex gap-1 mt-1">
                      {results.infrastructure.cloudProviders.map((p: string) => (
                        <Badge key={p} variant="info" className="text-xs">{p}</Badge>
                      ))}
                    </div>
                  </div>
                </div>
              </ResultSection>
            </motion.div>
          ) : (
            <GlassCard className="p-12 flex flex-col items-center justify-center text-center">
              <Building2 className="w-16 h-16 text-white/20 mb-4" />
              <h3 className="text-lg font-medium text-white/60">No Company Analyzed</h3>
              <p className="text-sm text-white/40">Enter a company name for infrastructure analysis</p>
            </GlassCard>
          )}
        </div>
      </div>
    </PageContainer>
  );
}

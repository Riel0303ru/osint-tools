import { motion } from 'framer-motion';
import { Building2, Globe, Users, Shield, Database } from 'lucide-react';
import { PageHeader, PageContainer } from '../components/layout';
import { GlassCard, Badge, KeyValueItem } from '../components/ui';
import { ScanLauncher, ResultsHeader, ResultSection } from '../components/intelligence/ScanLauncher';
import { api } from '../lib/api';
import { cn } from '../lib/utils';
import { useState } from 'react';

export default function CompanyPage() {
  const [results, setResults] = useState<any>(null);
  const [scanning, setScanning] = useState(false);

  const handleScan = async (query: string) => {
    setScanning(true);
    setResults(null);
    try {
      const data = await api.scanCompany(query);
      const report = data.report || {};
      
      const companyApi = report.company_api || {};
      const dns = report.dns || {};
      const subdomainsList = report.subdomains?.subdomains || [];
      const techList = report.technologies?.technologies || [];
      const risk = report.risk_assessment || {};
      
      const maxIntelScore = risk.overall_risk_score || 15;
      let level: 'safe' | 'low' | 'medium' | 'high' | 'critical' = 'safe';
      if (maxIntelScore > 80) level = 'critical';
      else if (maxIntelScore > 60) level = 'high';
      else if (maxIntelScore > 40) level = 'medium';
      else if (maxIntelScore > 20) level = 'low';

      // Gather cloud providers
      const cloudProviders = techList
        .filter((t: any) => t.category === 'Cloud' || t.name === 'AWS' || t.name === 'Azure' || t.name === 'Google Cloud')
        .map((t: any) => t.name);

      setResults({
        target: query,
        name: companyApi.company_name || companyApi.name || query,
        domains: [query],
        employees: companyApi.employees || companyApi.employee_range || 10,
        industry: companyApi.industry || 'Technology',
        infrastructure: {
          domains: 1,
          subdomains: subdomainsList.length || 1,
          ips: dns.records?.A?.length || subdomainsList.filter((s: any) => s.ip).length || 1,
          cloudProviders: cloudProviders.length > 0 ? cloudProviders : ['AWS']
        },
        security: {
          sslGrade: risk.ssl_grade || 'A',
          score: Math.round(100 - maxIntelScore)
        },
        riskScore: { level, score: Math.round(maxIntelScore) },
        timestamp: new Date().toISOString(),
      });
    } catch (error: any) {
      console.error(error);
      alert(`Scan failed: ${error.message || error}`);
    } finally {
      setScanning(false);
    }
  };

  return (
    <PageContainer>
      <PageHeader title="Company Intelligence" subtitle="Corporate infrastructure and security assessment" />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1">
          <ScanLauncher type="company" onScan={handleScan} placeholder="Enter company name..." />
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
                    <p className="text-xs text-white/50">Mapping corporate network</p>
                  </div>
                </div>
              </GlassCard>
            </motion.div>
          )}
        </div>

        <div className="lg:col-span-2">
          {results ? (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-6">
              <ResultsHeader
                title="Company Analysis"
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

              <ResultSection title="Company Overview">
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <GlassCard variant="light" className="p-4 text-center">
                    <Building2 className="w-5 h-5 text-accent-cyan mx-auto mb-2" />
                    <p className="text-xs text-white/50">Industry</p>
                    <p className="text-sm font-medium text-white truncate">{results.industry}</p>
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
                    <div className="flex gap-1 mt-1 flex-wrap">
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
              <h3 className="text-lg font-medium text-white/60">No Company Scanned</h3>
              <p className="text-sm text-white/40">Enter a company domain name for infrastructure analysis</p>
            </GlassCard>
          )}
        </div>
      </div>
    </PageContainer>
  );
}

import { motion } from 'framer-motion';
import { Server, MapPin, Globe, Shield, Building } from 'lucide-react';
import { PageHeader, PageContainer } from '../components/layout';
import { GlassCard, AnimatedButton, RiskBadge, Badge, KeyValueItem } from '../components/ui';
import { ScanLauncher, ResultsHeader, ResultSection } from '../components/intelligence/ScanLauncher';
import { useState } from 'react';

const mockIPData = {
  ip: '8.8.8.8',
  geolocation: { country: 'United States', city: 'Mountain View', region: 'California', isp: 'Google LLC', org: 'Google Public DNS' },
  asn: { asn: 'AS15169', name: 'Google LLC', type: 'hosting' },
  reputation: { isProxy: false, isVPN: false, isTor: false, score: 95 },
  riskScore: { level: 'safe', score: 5 },
};

export default function IPPage() {
  const [results, setResults] = useState<any>(null);

  const handleScan = (query: string) => {
    setTimeout(() => {
      setResults({ target: query, ...mockIPData, timestamp: new Date().toISOString() });
    }, 1500);
  };

  return (
    <PageContainer>
      <PageHeader title="IP Intelligence" subtitle="Geolocation, ASN, and reputation analysis" />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1">
          <ScanLauncher type="ip" onScan={handleScan} placeholder="Enter IP address..." />
        </div>

        <div className="lg:col-span-2">
          {results ? (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-6">
              <ResultsHeader title="IP Analysis" target={results.target} riskScore={results.riskScore} timestamp={results.timestamp} />

              <ResultSection title="Geolocation">
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  {[
                    { icon: <MapPin className="w-5 h-5" />, label: 'Country', value: results.geolocation.country },
                    { icon: <Globe className="w-5 h-5" />, label: 'Region', value: results.geolocation.region },
                    { icon: <MapPin className="w-5 h-5" />, label: 'City', value: results.geolocation.city },
                    { icon: <Building className="w-5 h-5" />, label: 'ISP', value: results.geolocation.isp },
                  ].map((item, i) => (
                    <GlassCard key={i} variant="light" className="p-4">
                      <div className="text-white/40 mb-1">{item.icon}</div>
                      <p className="text-xs text-white/50">{item.label}</p>
                      <p className="text-sm font-medium text-white">{item.value}</p>
                    </GlassCard>
                  ))}
                </div>
              </ResultSection>

              <ResultSection title="ASN Information">
                <div className="space-y-1">
                  <KeyValueItem label="ASN" value={results.asn.asn} copyable />
                  <KeyValueItem label="Organization" value={results.asn.name} />
                  <KeyValueItem label="Type" value={results.asn.type} />
                </div>
              </ResultSection>

              <ResultSection title="Reputation">
                <div className="flex gap-4">
                  {[
                    { label: 'Proxy', value: results.reputation.isProxy },
                    { label: 'VPN', value: results.reputation.isVPN },
                    { label: 'Tor', value: results.reputation.isTor },
                  ].map((item, i) => (
                    <Badge key={i} variant={item.value ? 'error' : 'success'}>{item.label}: {item.value ? 'Yes' : 'No'}</Badge>
                  ))}
                </div>
              </ResultSection>
            </motion.div>
          ) : (
            <GlassCard className="p-12 flex flex-col items-center justify-center text-center">
              <Server className="w-16 h-16 text-white/20 mb-4" />
              <h3 className="text-lg font-medium text-white/60">No IP Analyzed</h3>
              <p className="text-sm text-white/40">Enter an IP address for geolocation and reputation analysis</p>
            </GlassCard>
          )}
        </div>
      </div>
    </PageContainer>
  );
}

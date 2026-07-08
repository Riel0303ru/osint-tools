import { motion } from 'framer-motion';
import { Server, MapPin, Globe, Shield, Building } from 'lucide-react';
import { PageHeader, PageContainer } from '../components/layout';
import { GlassCard, AnimatedButton, RiskBadge, Badge, KeyValueItem } from '../components/ui';
import { ScanLauncher, ResultsHeader, ResultSection } from '../components/intelligence/ScanLauncher';
import { api } from '../lib/api';
import { cn } from '../lib/utils';
import { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';

export default function IPPage() {
  const [searchParams] = useSearchParams();
  const [results, setResults] = useState<any>(null);
  const [scanning, setScanning] = useState(false);

  const handleScan = async (query: string) => {
    setScanning(true);
    setResults(null);
    try {
      const data = await api.scanIP(query);
      const ipinfo = data.find((r: any) => r.platform === 'IP Geolocation' || r.platform === 'IPGeolocator' || r.platform === 'IPInfo' || r.status === 'FOUND');
      
      const maxIntelScore = Math.max(...data.map((r: any) => r.intelligence_score || 0), 0);
      let level: 'safe' | 'low' | 'medium' | 'high' | 'critical' = 'safe';
      if (maxIntelScore > 80) level = 'critical';
      else if (maxIntelScore > 60) level = 'high';
      else if (maxIntelScore > 40) level = 'medium';
      else if (maxIntelScore > 20) level = 'low';

      const extra = ipinfo?.extra || {};
      setResults({
        target: query,
        geolocation: {
          country: extra.country || extra.country_name || 'Unknown',
          city: extra.city || 'Unknown',
          region: extra.region || extra.region_name || 'Unknown',
          isp: extra.isp || extra.org || 'Unknown'
        },
        asn: {
          asn: extra.asn ? (String(extra.asn).startsWith('AS') ? String(extra.asn) : `AS${extra.asn}`) : 'Unknown',
          name: extra.asn_name || extra.org || 'Unknown',
          type: extra.infrastructure_type || 'hosting'
        },
        reputation: {
          isProxy: !!extra.is_proxy,
          isVPN: !!extra.is_vpn,
          isTor: !!extra.is_tor,
          score: 100 - (extra.abuse_score || 0)
        },
        riskScore: { level, score: Math.round(maxIntelScore) },
        timestamp: new Date().toISOString()
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
      <PageHeader title="IP Intelligence" subtitle="Geolocation, ASN, and reputation analysis" />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1">
          <ScanLauncher type="ip" onScan={handleScan} placeholder="Enter IP address..." />
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
                    <p className="text-xs text-white/50">Querying geolocators</p>
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
                title="IP Analysis"
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
                      <p className="text-sm font-medium text-white truncate">{item.value}</p>
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
                <div className="flex gap-4 flex-wrap">
                  {[
                    { label: 'Proxy', value: results.reputation.isProxy },
                    { label: 'VPN', value: results.reputation.isVPN },
                    { label: 'Tor', value: results.reputation.isTor },
                  ].map((item, i) => (
                    <Badge key={i} variant={item.value ? 'error' : 'success'}>{item.label}: {item.value ? 'Yes' : 'No'}</Badge>
                  ))}
                  <Badge variant={results.reputation.score > 70 ? 'success' : results.reputation.score > 40 ? 'warning' : 'error'}>
                    Reputation Score: {results.reputation.score}%
                  </Badge>
                </div>
              </ResultSection>
            </motion.div>
          ) : (
            <GlassCard className="p-12 flex flex-col items-center justify-center text-center">
              <Server className="w-16 h-16 text-white/20 mb-4" />
              <h3 className="text-lg font-medium text-white/60">No IP Scanned</h3>
              <p className="text-sm text-white/40">Enter an IP address for geolocation and reputation analysis</p>
            </GlassCard>
          )}
        </div>
      </div>
    </PageContainer>
  );
}


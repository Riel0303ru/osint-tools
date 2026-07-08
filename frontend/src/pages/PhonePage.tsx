import { motion } from 'framer-motion';
import { Phone, AlertTriangle, CheckCircle, MessageCircle } from 'lucide-react';
import { PageHeader, PageContainer } from '../components/layout';
import { GlassCard, Badge } from '../components/ui';
import { ScanLauncher, ResultsHeader, ResultSection } from '../components/intelligence/ScanLauncher';
import { api } from '../lib/api';
import { cn } from '../lib/utils';
import { useState } from 'react';

export default function PhonePage() {
  const [results, setResults] = useState<any>(null);
  const [scanning, setScanning] = useState(false);

  const handleScan = async (query: string) => {
    setScanning(true);
    setResults(null);
    try {
      const data = await api.scanPhone(query);
      const numverify = data.find((r: any) => r.platform === 'Numverify');
      const whatsapp = data.find((r: any) => r.platform === 'WhatsApp');
      const telegram = data.find((r: any) => r.platform === 'Telegram');
      
      const maxIntelScore = Math.max(...data.map((r: any) => r.intelligence_score || 0), 0);
      let level: 'safe' | 'low' | 'medium' | 'high' | 'critical' = 'safe';
      if (maxIntelScore > 80) level = 'critical';
      else if (maxIntelScore > 60) level = 'high';
      else if (maxIntelScore > 40) level = 'medium';
      else if (maxIntelScore > 20) level = 'low';

      const valid = numverify?.extra?.valid ?? (numverify ? numverify.status === 'FOUND' : true);
      const lineType = numverify?.extra?.line_type || 'mobile';
      const carrier = numverify?.extra?.carrier || 'Unknown Carrier';
      const countryName = numverify?.extra?.country_name || numverify?.extra?.country || 'Unknown';

      setResults({
        target: query,
        valid,
        type: lineType,
        carrier,
        location: { country: countryName },
        whatsapp: whatsapp?.status === 'FOUND',
        telegram: telegram?.status === 'FOUND',
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
      <PageHeader title="Phone Intelligence" subtitle="Phone validation, carrier lookup, and messaging app detection" />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1">
          <ScanLauncher type="phone" onScan={handleScan} placeholder="Enter phone number..." />
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
                    <p className="text-xs text-white/50">Analyzing number metadata</p>
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
                title="Phone Analysis"
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

              <ResultSection title="Phone Details">
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  {[
                    { label: 'Valid', value: results.valid, icon: <CheckCircle className="w-5 h-5" /> },
                    { label: 'Type', value: results.type },
                    { label: 'Carrier', value: results.carrier },
                    { label: 'Country', value: results.location.country },
                  ].map((item, i) => (
                    <GlassCard key={i} variant="light" className="p-4 text-center">
                      {item.icon && <div className="text-accent-emerald mb-2">{item.icon}</div>}
                      <p className="text-xs text-white/50">{item.label}</p>
                      <p className="text-sm font-medium text-white truncate">{typeof item.value === 'boolean' ? (item.value ? 'Yes' : 'No') : item.value}</p>
                    </GlassCard>
                  ))}
                </div>
              </ResultSection>

              <ResultSection title="Messaging Apps">
                <div className="flex gap-4">
                  <div className={cn("p-4 rounded-lg flex-1 transition-all", results.whatsapp ? 'bg-accent-emerald/10 border border-accent-emerald/20' : 'bg-white/5')}>
                    <MessageCircle className={cn("w-5 h-5 mb-2", results.whatsapp ? 'text-accent-emerald' : 'text-white/30')} />
                    <p className="text-sm font-medium text-white">WhatsApp</p>
                    <Badge variant={results.whatsapp ? 'success' : 'default'} className="mt-2">
                      {results.whatsapp ? 'Detected' : 'Not Found'}
                    </Badge>
                  </div>
                  <div className={cn("p-4 rounded-lg flex-1 transition-all", results.telegram ? 'bg-accent-cyan/10 border border-accent-cyan/20' : 'bg-white/5')}>
                    <MessageCircle className={cn("w-5 h-5 mb-2", results.telegram ? 'text-accent-cyan' : 'text-white/30')} />
                    <p className="text-sm font-medium text-white">Telegram</p>
                    <Badge variant={results.telegram ? 'success' : 'default'} className="mt-2">
                      {results.telegram ? 'Detected' : 'Not Found'}
                    </Badge>
                  </div>
                </div>
              </ResultSection>
            </motion.div>
          ) : (
            <GlassCard className="p-12 flex flex-col items-center justify-center text-center">
              <Phone className="w-16 h-16 text-white/20 mb-4" />
              <h3 className="text-lg font-medium text-white/60">No Phone Scanned</h3>
              <p className="text-sm text-white/40">Enter a phone number for validation and analysis</p>
            </GlassCard>
          )}
        </div>
      </div>
    </PageContainer>
  );
}

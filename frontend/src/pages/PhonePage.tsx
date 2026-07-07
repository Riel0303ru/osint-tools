import { motion } from 'framer-motion';
import { Phone, AlertTriangle, CheckCircle, MessageCircle } from 'lucide-react';
import { PageHeader, PageContainer } from '../components/layout';
import { GlassCard, Badge } from '../components/ui';
import { ScanLauncher, ResultsHeader, ResultSection } from '../components/intelligence/ScanLauncher';
import { useState } from 'react';

export default function PhonePage() {
  const [results, setResults] = useState<any>(null);

  const handleScan = (query: string) => {
    setTimeout(() => {
      setResults({
        target: query,
        valid: true,
        type: 'mobile',
        carrier: 'Verizon Wireless',
        location: { country: 'United States', region: 'California' },
        whatsapp: true,
        telegram: false,
        riskScore: { level: 'low', score: 20 },
        timestamp: new Date().toISOString(),
      });
    }, 1500);
  };

  return (
    <PageContainer>
      <PageHeader title="Phone Intelligence" subtitle="Phone validation, carrier lookup, and messaging app detection" />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1">
          <ScanLauncher type="phone" onScan={handleScan} placeholder="Enter phone number..." />
        </div>

        <div className="lg:col-span-2">
          {results ? (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-6">
              <ResultsHeader title="Phone Analysis" target={results.target} riskScore={results.riskScore} timestamp={results.timestamp} />

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
                      <p className="text-sm font-medium text-white">{typeof item.value === 'boolean' ? (item.value ? 'Yes' : 'No') : item.value}</p>
                    </GlassCard>
                  ))}
                </div>
              </ResultSection>

              <ResultSection title="Messaging Apps">
                <div className="flex gap-4">
                  <div className={`p-4 rounded-lg flex-1 ${results.whatsapp ? 'bg-accent-emerald/10 border border-accent-emerald/20' : 'bg-white/5'}`}>
                    <MessageCircle className={`w-5 h-5 mb-2 ${results.whatsapp ? 'text-accent-emerald' : 'text-white/30'}`} />
                    <p className="text-sm font-medium text-white">WhatsApp</p>
                    <Badge variant={results.whatsapp ? 'success' : 'default'} className="mt-2">
                      {results.whatsapp ? 'Detected' : 'Not Found'}
                    </Badge>
                  </div>
                  <div className={`p-4 rounded-lg flex-1 ${results.telegram ? 'bg-accent-cyan/10 border border-accent-cyan/20' : 'bg-white/5'}`}>
                    <MessageCircle className={`w-5 h-5 mb-2 ${results.telegram ? 'text-accent-cyan' : 'text-white/30'}`} />
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
              <h3 className="text-lg font-medium text-white/60">No Phone Analyzed</h3>
              <p className="text-sm text-white/40">Enter a phone number for validation and analysis</p>
            </GlassCard>
          )}
        </div>
      </div>
    </PageContainer>
  );
}

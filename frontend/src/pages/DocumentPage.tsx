import { motion } from 'framer-motion';
import { FileText, Upload, AlertTriangle, Eye, Lock } from 'lucide-react';
import { PageHeader, PageContainer } from '../components/layout';
import { GlassCard, Badge, KeyValueItem } from '../components/ui';
import { ResultsHeader, ResultSection } from '../components/intelligence/ScanLauncher';
import { useState, useCallback } from 'react';

export default function DocumentPage() {
  const [results, setResults] = useState<any>(null);

  const handleUpload = () => {
    setTimeout(() => {
      setResults({
        target: 'document.pdf',
        metadata: { author: 'John Doe', pages: 12, words: 4500, created: '2024-01-15' },
        sensitive: [{ type: 'Email', value: 'secret@email.com', risk: 'medium' }, { type: 'API Key', value: 'sk-xxx...', risk: 'high' }],
        riskScore: { level: 'high', score: 65 },
        timestamp: new Date().toISOString(),
      });
    }, 1500);
  };

  return (
    <PageContainer>
      <PageHeader title="Document Intelligence" subtitle="Metadata extraction, OCR, and sensitive data detection" />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1">
          <GlassCard className="p-6">
            <h3 className="font-medium text-white mb-4">Upload Document</h3>
            <div className="border-2 border-dashed border-white/20 rounded-xl p-8 text-center hover:border-white/40 transition-colors cursor-pointer" onClick={handleUpload}>
              <Upload className="w-10 h-10 text-white/40 mx-auto mb-3" />
              <p className="text-sm text-white/60">PDF, DOCX, XLSX, PPTX</p>
              <p className="text-xs text-white/40 mt-1">Click to upload</p>
            </div>
          </GlassCard>
        </div>

        <div className="lg:col-span-2">
          {results ? (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-6">
              <ResultsHeader title="Document Analysis" target={results.target} riskScore={results.riskScore} timestamp={results.timestamp} />

              <ResultSection title="Document Metadata">
                <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                  {Object.entries(results.metadata).map(([key, value]) => (
                    <div key={key} className="p-3 bg-white/5 rounded-lg">
                      <p className="text-xs text-white/50 capitalize">{key}</p>
                      <p className="text-sm font-medium text-white">{String(value)}</p>
                    </div>
                  ))}
                </div>
              </ResultSection>

              <ResultSection title="Sensitive Data Detected">
                <div className="space-y-3">
                  {results.sensitive.map((item: any, i: number) => (
                    <div key={i} className={`p-4 rounded-lg border ${item.risk === 'high' ? 'border-accent-red/30 bg-accent-red/5' : 'border-accent-amber/30 bg-accent-amber/5'}`}>
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <AlertTriangle className={`w-4 h-4 ${item.risk === 'high' ? 'text-accent-red' : 'text-accent-amber'}`} />
                          <span className="font-medium text-white">{item.type}</span>
                        </div>
                        <Badge variant={item.risk === 'high' ? 'error' : 'warning'}>{item.risk} risk</Badge>
                      </div>
                      <p className="text-xs text-white/60 mt-2 font-mono">{item.value}</p>
                    </div>
                  ))}
                </div>
              </ResultSection>
            </motion.div>
          ) : (
            <GlassCard className="p-12 flex flex-col items-center justify-center text-center">
              <FileText className="w-16 h-16 text-white/20 mb-4" />
              <h3 className="text-lg font-medium text-white/60">No Document Uploaded</h3>
              <p className="text-sm text-white/40">Upload a document for metadata and sensitive data analysis</p>
            </GlassCard>
          )}
        </div>
      </div>
    </PageContainer>
  );
}

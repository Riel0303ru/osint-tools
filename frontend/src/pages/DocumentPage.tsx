import { motion } from 'framer-motion';
import { FileText, Upload, AlertTriangle, Eye, Lock } from 'lucide-react';
import { PageHeader, PageContainer } from '../components/layout';
import { GlassCard, Badge, KeyValueItem } from '../components/ui';
import { ResultsHeader, ResultSection } from '../components/intelligence/ScanLauncher';
import { api } from '../lib/api';
import { cn } from '../lib/utils';
import { useState, useRef } from 'react';

export default function DocumentPage() {
  const [results, setResults] = useState<any>(null);
  const [scanning, setScanning] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const processFile = async (file: File) => {
    setScanning(true);
    setResults(null);
    try {
      const data = await api.scanDocument(file);
      
      const meta = data.find((r: any) => r.platform === 'Document Metadata' || r.platform === 'Metadata Extraction');
      const sensitiveResults = data.filter((r: any) => r.platform !== 'Document Metadata' && r.platform !== 'Metadata Extraction' && r.status === 'FOUND');
      
      const maxIntelScore = Math.max(...data.map((r: any) => r.intelligence_score || 0), 0);
      let level: 'safe' | 'low' | 'medium' | 'high' | 'critical' = 'safe';
      if (maxIntelScore > 80) level = 'critical';
      else if (maxIntelScore > 60) level = 'high';
      else if (maxIntelScore > 40) level = 'medium';
      else if (maxIntelScore > 20) level = 'low';

      // Parse metadata
      const metaExtra = meta?.extra || {};
      const metadata = {
        author: metaExtra.author || 'Unknown',
        pages: metaExtra.pages || 'N/A',
        words: metaExtra.words || 'N/A',
        created: metaExtra.created_date || metaExtra.creation_date || 'Unknown',
      };

      // Parse sensitive
      const sensitive: any[] = [];
      sensitiveResults.forEach((r: any) => {
        const list = r.extra?.findings || r.extra?.detected || [];
        if (list.length > 0) {
          list.forEach((item: any) => {
            sensitive.push({
              type: item.type || r.platform,
              value: item.value || item.text || 'Exposed value',
              risk: item.risk || (item.type?.toLowerCase().includes('key') ? 'high' : 'medium')
            });
          });
        } else {
          // Fallback if structured findings are not lists
          sensitive.push({
            type: r.platform,
            value: r.url || JSON.stringify(r.extra),
            risk: 'medium'
          });
        }
      });

      setResults({
        target: file.name,
        metadata,
        sensitive,
        riskScore: { level, score: Math.round(maxIntelScore) },
        timestamp: new Date().toISOString(),
      });
    } catch (error: any) {
      console.error(error);
      alert(`Document scan failed: ${error.message || error}`);
    } finally {
      setScanning(false);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      processFile(e.target.files[0]);
    }
  };

  return (
    <PageContainer>
      <PageHeader title="Document Intelligence" subtitle="Metadata extraction, OCR, and sensitive data detection" />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1 space-y-4">
          <GlassCard className="p-6">
            <h3 className="font-medium text-white mb-4">Upload Document</h3>
            <div
              className="border-2 border-dashed border-white/20 rounded-xl p-8 text-center hover:border-white/40 transition-colors cursor-pointer"
              onClick={() => fileInputRef.current?.click()}
            >
              <Upload className="w-10 h-10 text-white/40 mx-auto mb-3" />
              <p className="text-sm text-white/60">PDF, DOCX, XLSX, PPTX</p>
              <p className="text-xs text-white/40 mt-1">Click to upload</p>
              <input
                type="file"
                className="hidden"
                ref={fileInputRef}
                onChange={handleFileChange}
                accept=".pdf,.docx,.xlsx,.pptx,.txt"
              />
            </div>
          </GlassCard>

          {scanning && (
            <GlassCard className="p-4 flex items-center gap-3">
              <motion.div
                animate={{ rotate: 360 }}
                transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                className="w-6 h-6 border-2 border-accent-cyan/30 border-t-accent-cyan rounded-full"
              />
              <div>
                <p className="text-sm font-medium text-white">Scanning Document...</p>
                <p className="text-xs text-white/50">Extracting texts & sensitive keys</p>
              </div>
            </GlassCard>
          )}
        </div>

        <div className="lg:col-span-2">
          {results ? (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-6">
              <ResultsHeader
                title="Document Analysis"
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
                {results.sensitive.length > 0 ? (
                  <div className="space-y-3">
                    {results.sensitive.map((item: any, i: number) => (
                      <div key={i} className={cn("p-4 rounded-lg border", item.risk === 'high' ? 'border-accent-red/30 bg-accent-red/5' : 'border-accent-amber/30 bg-accent-amber/5')}>
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            <AlertTriangle className={cn("w-4 h-4", item.risk === 'high' ? 'text-accent-red' : 'text-accent-amber')} />
                            <span className="font-medium text-white">{item.type}</span>
                          </div>
                          <Badge variant={item.risk === 'high' ? 'error' : 'warning'}>{item.risk} risk</Badge>
                        </div>
                        <p className="text-xs text-white/60 mt-2 font-mono break-all">{item.value}</p>
                      </div>
                    ))}
                  </div>
                ) : (
                  <GlassCard className="p-6 text-center text-white/50">
                    No credentials, emails, or phone numbers detected in this file.
                  </GlassCard>
                )}
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

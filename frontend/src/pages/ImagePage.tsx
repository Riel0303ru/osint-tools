import { motion } from 'framer-motion';
import { Image, Upload, MapPin, Eye, FileText } from 'lucide-react';
import { PageHeader, PageContainer } from '../components/layout';
import { GlassCard, AnimatedButton, Badge, KeyValueItem } from '../components/ui';
import { ScanLauncher, ResultsHeader, ResultSection } from '../components/intelligence/ScanLauncher';
import { useState, useCallback } from 'react';

export default function ImagePage() {
  const [results, setResults] = useState<any>(null);
  const [dragActive, setDragActive] = useState(false);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragActive(false);
    // Simulate upload
    setTimeout(() => {
      setResults({
        target: 'uploaded-image.jpg',
        metadata: { width: 1920, height: 1080, format: 'JPEG', size: '2.4 MB' },
        exif: { make: 'Canon', model: 'EOS R5', dateTime: '2024-01-15', gps: { lat: 37.7749, lng: -122.4194, city: 'San Francisco' } },
        analysis: { faces: 2, objects: ['person', 'car', 'building'], text: 'Detected 23 text regions' },
        riskScore: { level: 'low', score: 10 },
        timestamp: new Date().toISOString(),
      });
    }, 1500);
  }, []);

  return (
    <PageContainer>
      <PageHeader title="Image Intelligence" subtitle="EXIF analysis, reverse search, and object detection" />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1 space-y-4">
          <GlassCard className="p-6">
            <h3 className="font-medium text-white mb-4">Upload Image</h3>
            <div
              className={`border-2 border-dashed rounded-xl p-8 text-center transition-colors ${
                dragActive ? 'border-accent-cyan bg-accent-cyan/10' : 'border-white/20 hover:border-white/40'
              }`}
              onDragOver={(e) => { e.preventDefault(); setDragActive(true); }}
              onDragLeave={() => setDragActive(false)}
              onDrop={handleDrop}
            >
              <Upload className="w-10 h-10 text-white/40 mx-auto mb-3" />
              <p className="text-sm text-white/60">Drag and drop an image</p>
              <p className="text-xs text-white/40 mt-1">or click to browse</p>
              <input type="file" accept="image/*" className="hidden" id="image-upload" />
              <label htmlFor="image-upload" className="mt-4 inline-block">
                <AnimatedButton variant="secondary" size="sm" as="span">Choose File</AnimatedButton>
              </label>
            </div>
          </GlassCard>
        </div>

        <div className="lg:col-span-2">
          {results ? (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-6">
              <ResultsHeader title="Image Analysis" target={results.target} riskScore={results.riskScore} timestamp={results.timestamp} />

              <ResultSection title="Image Metadata">
                <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                  {Object.entries(results.metadata).map(([key, value]) => (
                    <div key={key} className="p-3 bg-white/5 rounded-lg">
                      <p className="text-xs text-white/50 capitalize">{key}</p>
                      <p className="text-sm font-medium text-white">{String(value)}</p>
                    </div>
                  ))}
                </div>
              </ResultSection>

              {results.exif && (
                <ResultSection title="EXIF Data">
                  <div className="space-y-1">
                    <KeyValueItem label="Camera" value={`${results.exif.make} ${results.exif.model}`} />
                    <KeyValueItem label="Date" value={results.exif.dateTime} />
                  </div>
                  {results.exif.gps && (
                    <div className="mt-4 p-4 bg-accent-cyan/10 rounded-lg border border-accent-cyan/20">
                      <div className="flex items-center gap-2 text-accent-cyan mb-2">
                        <MapPin className="w-4 h-4" />
                        <span className="text-sm font-medium">GPS Location Detected</span>
                      </div>
                      <p className="text-sm text-white/80">{results.exif.gps.city}</p>
                      <p className="text-xs text-white/50 font-mono">{results.exif.gps.lat}, {results.exif.gps.lng}</p>
                    </div>
                  )}
                </ResultSection>
              )}

              <ResultSection title="Analysis Results">
                <div className="grid grid-cols-3 gap-4">
                  <div className="p-4 bg-white/5 rounded-lg text-center">
                    <Eye className="w-5 h-5 text-accent-cyan mx-auto mb-2" />
                    <p className="text-2xl font-bold text-white">{results.analysis.faces}</p>
                    <p className="text-xs text-white/50">Faces Detected</p>
                  </div>
                  <div className="p-4 bg-white/5 rounded-lg text-center">
                    <Image className="w-5 h-5 text-accent-violet mx-auto mb-2" />
                    <p className="text-2xl font-bold text-white">{results.analysis.objects.length}</p>
                    <p className="text-xs text-white/50">Objects</p>
                  </div>
                  <div className="p-4 bg-white/5 rounded-lg text-center">
                    <FileText className="w-5 h-5 text-accent-emerald mx-auto mb-2" />
                    <p className="text-sm font-bold text-white">OCR</p>
                    <p className="text-xs text-white/50">Complete</p>
                  </div>
                </div>
                <div className="flex flex-wrap gap-2 mt-4">
                  {results.analysis.objects.map((obj: string) => (
                    <Badge key={obj} variant="default">{obj}</Badge>
                  ))}
                </div>
              </ResultSection>
            </motion.div>
          ) : (
            <GlassCard className="p-12 flex flex-col items-center justify-center text-center">
              <Image className="w-16 h-16 text-white/20 mb-4" />
              <h3 className="text-lg font-medium text-white/60">No Image Uploaded</h3>
              <p className="text-sm text-white/40">Upload an image for EXIF analysis and object detection</p>
            </GlassCard>
          )}
        </div>
      </div>
    </PageContainer>
  );
}

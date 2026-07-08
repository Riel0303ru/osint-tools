import { motion } from 'framer-motion';
import { Image, Upload, MapPin, Eye, FileText, Globe } from 'lucide-react';
import { PageHeader, PageContainer } from '../components/layout';
import { GlassCard, AnimatedButton, Badge, KeyValueItem } from '../components/ui';
import { ScanLauncher, ResultsHeader, ResultSection } from '../components/intelligence/ScanLauncher';
import { api } from '../lib/api';
import { cn } from '../lib/utils';
import { useState, useCallback, useRef } from 'react';

export default function ImagePage() {
  const [results, setResults] = useState<any>(null);
  const [scanning, setScanning] = useState(false);
  const [dragActive, setDragActive] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const processFile = async (file: File) => {
    setScanning(true);
    setResults(null);
    try {
      const data = await api.scanImage(file);
      
      const exif = data.find((r: any) => r.platform === 'EXIF Metadata');
      const ocr = data.find((r: any) => r.platform === 'OCR Text');
      const objects = data.find((r: any) => r.platform === 'Object Detection');
      const stego = data.find((r: any) => r.platform === 'StegCheck' || r.platform === 'Steganography');
      const reverse = data.find((r: any) => r.platform === 'Reverse Image Search');
      
      const maxIntelScore = Math.max(...data.map((r: any) => r.intelligence_score || 0), 0);
      let level: 'safe' | 'low' | 'medium' | 'high' | 'critical' = 'safe';
      if (maxIntelScore > 80) level = 'critical';
      else if (maxIntelScore > 60) level = 'high';
      else if (maxIntelScore > 40) level = 'medium';
      else if (maxIntelScore > 20) level = 'low';

      // Parse metadata
      const exifExtra = exif?.extra || {};
      const metadata = {
        width: exifExtra.width || 'Unknown',
        height: exifExtra.height || 'Unknown',
        format: exifExtra.format || file.type.split('/')[1]?.toUpperCase() || 'JPEG',
        size: (file.size / (1024 * 1024)).toFixed(2) + ' MB'
      };

      // Parse GPS
      let gps = null;
      if (exifExtra.gps_latitude && exifExtra.gps_longitude) {
        gps = {
          lat: exifExtra.gps_latitude,
          lng: exifExtra.gps_longitude,
          city: exifExtra.gps_location_name || 'Coordinates Detected'
        };
      }

      setResults({
        target: file.name,
        metadata,
        exif: exifExtra.camera_make ? {
          make: exifExtra.camera_make,
          model: exifExtra.camera_model || 'Unknown',
          dateTime: exifExtra.date_time || 'Unknown',
          gps
        } : null,
        analysis: {
          faces: objects?.extra?.faces_count || 0,
          objects: objects?.extra?.objects || [],
          text: ocr?.extra?.total_text || ocr?.extra?.text || 'No text regions detected'
        },
        steganography: stego?.extra?.stego_detected ? 'Steganography patterns suspected' : 'No steganography detected',
        reverseSearch: reverse?.extra?.matches || [],
        riskScore: { level, score: Math.round(maxIntelScore) },
        timestamp: new Date().toISOString(),
      });
    } catch (error: any) {
      console.error(error);
      alert(`Image scan failed: ${error.message || error}`);
    } finally {
      setScanning(false);
    }
  };

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      processFile(e.dataTransfer.files[0]);
    }
  }, []);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragActive(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragActive(false);
  }, []);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      processFile(e.target.files[0]);
    }
  };

  return (
    <PageContainer>
      <PageHeader title="Image Intelligence" subtitle="EXIF analysis, reverse search, and object detection" />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1 space-y-4">
          <GlassCard className="p-6">
            <h3 className="font-medium text-white mb-4">Upload Image</h3>
            <div
              className={cn(
                "border-2 border-dashed rounded-xl p-8 text-center transition-colors cursor-pointer",
                dragActive ? 'border-accent-cyan bg-accent-cyan/10' : 'border-white/20 hover:border-white/40'
              )}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current?.click()}
            >
              <Upload className="w-10 h-10 text-white/40 mx-auto mb-3" />
              <p className="text-sm text-white/60">Drag and drop an image</p>
              <p className="text-xs text-white/40 mt-1">or click to browse</p>
              <input
                type="file"
                accept="image/*"
                className="hidden"
                id="image-upload"
                ref={fileInputRef}
                onChange={handleFileChange}
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
                <p className="text-sm font-medium text-white">Analyzing Image...</p>
                <p className="text-xs text-white/50">Running EXIF, Object & OCR workflows</p>
              </div>
            </GlassCard>
          )}
        </div>

        <div className="lg:col-span-2">
          {results ? (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-6">
              <ResultsHeader
                title="Image Analysis"
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
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="p-4 bg-white/5 rounded-lg text-center">
                    <Eye className="w-5 h-5 text-accent-cyan mx-auto mb-2" />
                    <p className="text-2xl font-bold text-white">{results.analysis.faces}</p>
                    <p className="text-xs text-white/50">Faces Detected</p>
                  </div>
                  <div className="p-4 bg-white/5 rounded-lg text-center">
                    <Image className="w-5 h-5 text-accent-violet mx-auto mb-2" />
                    <p className="text-2xl font-bold text-white">{results.analysis.objects.length}</p>
                    <p className="text-xs text-white/50">Objects Identified</p>
                  </div>
                  <div className="p-4 bg-white/5 rounded-lg text-center">
                    <FileText className="w-5 h-5 text-accent-emerald mx-auto mb-2" />
                    <p className="text-sm font-bold text-white truncate px-2">{results.steganography}</p>
                    <p className="text-xs text-white/50">Stego Check</p>
                  </div>
                </div>
              </ResultSection>

              {results.analysis.objects.length > 0 && (
                <ResultSection title="Detected Objects">
                  <div className="flex flex-wrap gap-2">
                    {results.analysis.objects.map((obj: string, i: number) => (
                      <Badge key={i} variant="default">{obj}</Badge>
                    ))}
                  </div>
                </ResultSection>
              )}

              {results.analysis.text && results.analysis.text !== 'No text regions detected' && (
                <ResultSection title="Extracted OCR Text">
                  <GlassCard variant="light" className="p-4 font-mono text-xs whitespace-pre-wrap leading-relaxed text-white/80">
                    {results.analysis.text}
                  </GlassCard>
                </ResultSection>
              )}

              {results.reverseSearch.length > 0 && (
                <ResultSection title="Reverse Image Search Hits">
                  <div className="space-y-2">
                    {results.reverseSearch.map((match: any, i: number) => (
                      <div key={i} className="p-3 bg-white/5 rounded-lg flex items-center justify-between">
                        <div>
                          <p className="text-sm text-white font-medium">{match.title || 'Possible Match'}</p>
                          <a href={match.url} target="_blank" rel="noopener noreferrer" className="text-xs text-accent-cyan flex items-center gap-1 hover:underline">
                            {match.source || 'Visit Source'}
                            <ExternalLink className="w-3 h-3" />
                          </a>
                        </div>
                      </div>
                    ))}
                  </div>
                </ResultSection>
              )}
            </motion.div>
          ) : (
            <GlassCard className="p-12 flex flex-col items-center justify-center text-center">
              <Image className="w-16 h-16 text-white/20 mb-4" />
              <h3 className="text-lg font-medium text-white/60">No Image Uploaded</h3>
              <p className="text-sm text-white/40">Upload a file in the dropzone to trigger EXIF, OCR, and AI object scanning</p>
            </GlassCard>
          )}
        </div>
      </div>
    </PageContainer>
  );
}

import { motion } from 'framer-motion';
import { Video, Upload, Clock, MapPin, Users, FileText } from 'lucide-react';
import { PageHeader, PageContainer } from '../components/layout';
import { GlassCard, Badge } from '../components/ui';
import { ResultsHeader, ResultSection } from '../components/intelligence/ScanLauncher';
import { api } from '../lib/api';
import { cn } from '../lib/utils';
import { useState, useRef } from 'react';

export default function VideoPage() {
  const [results, setResults] = useState<any>(null);
  const [scanning, setScanning] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const processFile = async (file: File) => {
    setScanning(true);
    setResults(null);
    try {
      const data = await api.scanVideo(file);
      
      const meta = data.find((r: any) => r.platform === 'Video Metadata' || r.platform === 'Metadata Extraction');
      const objects = data.find((r: any) => r.platform === 'Object Detection' || r.platform === 'YOLOv8');
      const faces = data.find((r: any) => r.platform === 'Face Detection' || r.platform === 'OpenCV Face');
      const whisper = data.find((r: any) => r.platform === 'Whisper' || r.platform === 'Speech‑to‑Text');
      
      const maxIntelScore = Math.max(...data.map((r: any) => r.intelligence_score || 0), 0);
      let level: 'safe' | 'low' | 'medium' | 'high' | 'critical' = 'safe';
      if (maxIntelScore > 80) level = 'critical';
      else if (maxIntelScore > 60) level = 'high';
      else if (maxIntelScore > 40) level = 'medium';
      else if (maxIntelScore > 20) level = 'low';

      const metaExtra = meta?.extra || {};
      const objectsExtra = objects?.extra || {};
      const facesExtra = faces?.extra || {};
      const whisperExtra = whisper?.extra || {};

      setResults({
        target: file.name,
        metadata: {
          duration: metaExtra.duration || '00:10',
          resolution: metaExtra.resolution || '1920x1080',
          fps: metaExtra.fps || 30,
          size: (file.size / (1024 * 1024)).toFixed(2) + ' MB'
        },
        frames: metaExtra.total_frames || 300,
        analysis: {
          faces: facesExtra.faces_count || 0,
          objects: objectsExtra.objects || [],
          locations: objectsExtra.locations || [],
          transcript: whisperExtra.transcript || ''
        },
        riskScore: { level, score: Math.round(maxIntelScore) },
        timestamp: new Date().toISOString()
      });
    } catch (error: any) {
      console.error(error);
      alert(`Video scan failed: ${error.message || error}`);
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
      <PageHeader title="Video Intelligence" subtitle="Frame extraction, object tracking, and GEOINT analysis" />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1 space-y-4">
          <GlassCard className="p-6">
            <h3 className="font-medium text-white mb-4">Upload Video</h3>
            <div
              className="border-2 border-dashed border-white/20 rounded-xl p-8 text-center hover:border-white/40 transition-colors cursor-pointer"
              onClick={() => fileInputRef.current?.click()}
            >
              <Upload className="w-10 h-10 text-white/40 mx-auto mb-3" />
              <p className="text-sm text-white/60">MP4, MOV, AVI, MKV</p>
              <p className="text-xs text-white/40 mt-1">Click to upload</p>
              <input
                type="file"
                className="hidden"
                ref={fileInputRef}
                onChange={handleFileChange}
                accept=".mp4,.mov,.avi,.mkv,.webm,.m4v"
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
                <p className="text-sm font-medium text-white">Scanning Video...</p>
                <p className="text-xs text-white/50">Processing frames & running whisper audio models</p>
              </div>
            </GlassCard>
          )}
        </div>

        <div className="lg:col-span-2">
          {results ? (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-6">
              <ResultsHeader
                title="Video Analysis"
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

              <ResultSection title="Video Metadata">
                <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                  {Object.entries(results.metadata).map(([key, value]) => (
                    <div key={key} className="p-3 bg-white/5 rounded-lg text-center">
                      <p className="text-xs text-white/50 capitalize">{key}</p>
                      <p className="text-sm font-medium text-white">{String(value)}</p>
                    </div>
                  ))}
                </div>
              </ResultSection>

              <ResultSection title="Timeline Analysis">
                <div className="h-20 bg-white/5 rounded-lg relative overflow-hidden">
                  <motion.div className="absolute inset-y-0 left-0 w-1 bg-accent-cyan" animate={{ left: ['0%', '100%', '0%'] }} transition={{ duration: 10, repeat: Infinity }} />
                  <div className="absolute top-1/2 left-4 transform -translate-y-1/2 text-xs text-white/60">
                    {results.frames.toLocaleString()} frames analyzed
                  </div>
                </div>
              </ResultSection>

              <ResultSection title="Detection Results">
                <div className="grid grid-cols-3 gap-4">
                  <div className="p-4 bg-white/5 rounded-lg text-center">
                    <Users className="w-5 h-5 text-accent-cyan mx-auto mb-2" />
                    <p className="text-2xl font-bold text-white">{results.analysis.faces}</p>
                    <p className="text-xs text-white/50">Faces Tracked</p>
                  </div>
                  <div className="p-4 bg-white/5 rounded-lg text-center">
                    <Video className="w-5 h-5 text-accent-violet mx-auto mb-2" />
                    <p className="text-2xl font-bold text-white">{results.analysis.objects.length}</p>
                    <p className="text-xs text-white/50">Object Types</p>
                  </div>
                  <div className="p-4 bg-white/5 rounded-lg text-center">
                    <MapPin className="w-5 h-5 text-accent-emerald mx-auto mb-2" />
                    <p className="text-sm font-bold text-white">
                      {results.analysis.locations.length > 0 ? results.analysis.locations[0] : 'N/A'}
                    </p>
                    <p className="text-xs text-white/50">Location Tags</p>
                  </div>
                </div>
                
                {results.analysis.objects.length > 0 && (
                  <div className="flex flex-wrap gap-2 mt-4">
                    {results.analysis.objects.map((obj: string, i: number) => (
                      <Badge key={i}>{obj}</Badge>
                    ))}
                  </div>
                )}
              </ResultSection>

              {results.analysis.transcript && (
                <ResultSection title="Audio Transcription">
                  <GlassCard variant="light" className="p-4 leading-relaxed text-sm text-white/80">
                    {results.analysis.transcript}
                  </GlassCard>
                </ResultSection>
              )}
            </motion.div>
          ) : (
            <GlassCard className="p-12 flex flex-col items-center justify-center text-center">
              <Video className="w-16 h-16 text-white/20 mb-4" />
              <h3 className="text-lg font-medium text-white/60">No Video Uploaded</h3>
              <p className="text-sm text-white/40">Upload a video for timeline analysis, object detection, and transcription</p>
            </GlassCard>
          )}
        </div>
      </div>
    </PageContainer>
  );
}

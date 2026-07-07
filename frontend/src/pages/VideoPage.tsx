import { motion } from 'framer-motion';
import { Video, Upload, Clock, MapPin, Users } from 'lucide-react';
import { PageHeader, PageContainer } from '../components/layout';
import { GlassCard, Badge } from '../components/ui';
import { ResultsHeader, ResultSection } from '../components/intelligence/ScanLauncher';
import { useState } from 'react';

export default function VideoPage() {
  const [results, setResults] = useState<any>(null);

  const handleUpload = () => {
    setTimeout(() => {
      setResults({
        target: 'surveillance.mp4',
        metadata: { duration: '05:23', resolution: '1920x1080', fps: 30, size: '45 MB' },
        frames: 8123,
        analysis: { faces: 5, objects: ['person', 'vehicle', 'building'], locations: ['Downtown LA'] },
        riskScore: { level: 'low', score: 25 },
        timestamp: new Date().toISOString(),
      });
    }, 1500);
  };

  return (
    <PageContainer>
      <PageHeader title="Video Intelligence" subtitle="Frame extraction, object tracking, and GEOINT analysis" />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1">
          <GlassCard className="p-6">
            <h3 className="font-medium text-white mb-4">Upload Video</h3>
            <div className="border-2 border-dashed border-white/20 rounded-xl p-8 text-center hover:border-white/40 transition-colors cursor-pointer" onClick={handleUpload}>
              <Upload className="w-10 h-10 text-white/40 mx-auto mb-3" />
              <p className="text-sm text-white/60">MP4, MOV, AVI, MKV</p>
              <p className="text-xs text-white/40 mt-1">Click to upload</p>
            </div>
          </GlassCard>
        </div>

        <div className="lg:col-span-2">
          {results ? (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-6">
              <ResultsHeader title="Video Analysis" target={results.target} riskScore={results.riskScore} timestamp={results.timestamp} />

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
                    <p className="text-sm font-bold text-white">GPS</p>
                    <p className="text-xs text-white/50">Located</p>
                  </div>
                </div>
                <div className="flex flex-wrap gap-2 mt-4">
                  {results.analysis.objects.map((obj: string) => (
                    <Badge key={obj}>{obj}</Badge>
                  ))}
                  {results.analysis.locations.map((loc: string) => (
                    <Badge key={loc} variant="info">{loc}</Badge>
                  ))}
                </div>
              </ResultSection>
            </motion.div>
          ) : (
            <GlassCard className="p-12 flex flex-col items-center justify-center text-center">
              <Video className="w-16 h-16 text-white/20 mb-4" />
              <h3 className="text-lg font-medium text-white/60">No Video Uploaded</h3>
              <p className="text-sm text-white/40">Upload a video for timeline analysis and object detection</p>
            </GlassCard>
          )}
        </div>
      </div>
    </PageContainer>
  );
}

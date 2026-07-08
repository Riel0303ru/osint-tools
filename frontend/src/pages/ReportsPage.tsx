import { motion } from 'framer-motion';
import { FileBarChart, Plus, Download, Trash2, Eye, Calendar, ChevronLeft, ChevronRight } from 'lucide-react';
import { PageHeader, PageContainer } from '../components/layout';
import { GlassCard, AnimatedButton, RiskBadge, Badge } from '../components/ui';
import { api } from '../lib/api';
import { useState, useEffect } from 'react';

export default function ReportsPage() {
  const [reports, setReports] = useState<any[]>([]);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalItems, setTotalItems] = useState(0);
  const [loading, setLoading] = useState(false);
  const [filterType, setFilterType] = useState('All');

  const fetchReports = async (currPage: number) => {
    setLoading(true);
    try {
      const res = await api.getHistory(currPage, 10);
      setReports(res.items || []);
      setTotalItems(res.total || 0);
      setTotalPages(Math.ceil((res.total || 1) / 10));
    } catch (err: any) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchReports(page);
  }, [page]);

  const handleDownload = (target: string) => {
    api.generateReport(target).then((res) => {
      if (res.pdf_generated) {
        window.open(api.getDownloadReportUrl(target), '_blank');
      } else {
        alert('PDF report download is currently processing. Try again shortly.');
      }
    }).catch(err => alert(`Failed to download report: ${err.message}`));
  };

  const filteredReports = reports.filter(r => {
    if (filterType === 'All') return true;
    return r.scan_type?.toLowerCase() === filterType.toLowerCase();
  });

  return (
    <PageContainer>
      <PageHeader
        title="Reports Center"
        subtitle="Generated intelligence reports and export management"
        action={
          <div className="flex gap-2">
            <Badge variant="info">{totalItems} Total Scans</Badge>
          </div>
        }
      />

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        <div className="lg:col-span-1">
          <GlassCard className="p-4 space-y-4">
            <h3 className="font-medium text-white font-mono">Scan Type Filter</h3>
            <div className="space-y-1">
              {['All', 'Username', 'Email', 'Domain', 'IP', 'Phone'].map((filter) => (
                <button
                  key={filter}
                  className={`w-full text-left px-3 py-2 rounded-lg text-xs font-mono transition-colors ${
                    (filterType === filter) 
                      ? 'bg-accent-cyan/15 text-accent-cyan font-bold border border-accent-cyan/20' 
                      : 'text-white/70 hover:bg-white/5 hover:text-white'
                  }`}
                  onClick={() => setFilterType(filter)}
                >
                  {filter}
                </button>
              ))}
            </div>
          </GlassCard>
        </div>

        <div className="lg:col-span-3 space-y-4">
          {loading ? (
            <GlassCard className="p-8 flex items-center justify-center gap-2">
              <div className="w-5 h-5 border-2 border-accent-cyan/30 border-t-accent-cyan rounded-full animate-spin" />
              <span className="text-sm text-white/50">Fetching historical records...</span>
            </GlassCard>
          ) : filteredReports.length > 0 ? (
            <div className="space-y-3">
              {filteredReports.map((report, index) => {
                const targetText = report.target || 'Unknown Target';
                const scanType = report.scan_type || 'Unknown';
                const riskLevel = report.risk_level || 'low';
                const dateStr = report.created_at ? new Date(report.created_at).toLocaleDateString() : 'N/A';
                
                return (
                  <motion.div
                    key={report.id || index}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.05 }}
                  >
                    <GlassCard className="p-4">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-4">
                          <div className="p-3 rounded-lg bg-gradient-to-br from-accent-cyan/20 to-accent-violet/20 flex-shrink-0">
                            <FileBarChart className="w-5 h-5 text-accent-cyan" />
                          </div>
                          <div>
                            <h4 className="font-semibold text-sm text-white font-mono break-all">{targetText}</h4>
                            <div className="flex items-center gap-2 mt-1 flex-wrap">
                              <Badge variant="default" className="capitalize text-[10px]">{scanType}</Badge>
                              <span className="text-[10px] text-white/40 flex items-center gap-1">
                                <Calendar className="w-3 h-3" />
                                {dateStr}
                              </span>
                            </div>
                          </div>
                        </div>
                        <div className="flex items-center gap-3">
                          <RiskBadge level={riskLevel} size="sm" />
                          <div className="flex gap-1">
                            <AnimatedButton variant="ghost" size="sm" onClick={() => handleDownload(targetText)}>
                              <Eye className="w-4 h-4 text-white/60" />
                            </AnimatedButton>
                            <AnimatedButton variant="ghost" size="sm" onClick={() => handleDownload(targetText)}>
                              <Download className="w-4 h-4 text-accent-cyan" />
                            </AnimatedButton>
                          </div>
                        </div>
                      </div>
                    </GlassCard>
                  </motion.div>
                );
              })}

              {/* Pagination controls */}
              <div className="flex items-center justify-between pt-4">
                <span className="text-xs text-white/40 font-mono">
                  Page {page} of {totalPages}
                </span>
                <div className="flex gap-2">
                  <AnimatedButton
                    variant="secondary"
                    size="sm"
                    disabled={page === 1}
                    onClick={() => setPage(p => Math.max(p - 1, 1))}
                  >
                    <ChevronLeft className="w-4 h-4" />
                    Previous
                  </AnimatedButton>
                  <AnimatedButton
                    variant="secondary"
                    size="sm"
                    disabled={page >= totalPages}
                    onClick={() => setPage(p => Math.min(p + 1, totalPages))}
                  >
                    Next
                    <ChevronRight className="w-4 h-4" />
                  </AnimatedButton>
                </div>
              </div>
            </div>
          ) : (
            <GlassCard className="p-12 text-center text-white/50">
              No reports match the selected filters or history is empty.
            </GlassCard>
          )}
        </div>
      </div>
    </PageContainer>
  );
}

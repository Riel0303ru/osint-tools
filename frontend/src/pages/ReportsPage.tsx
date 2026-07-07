import { motion } from 'framer-motion';
import { FileBarChart, Plus, Download, Trash2, Eye, Calendar } from 'lucide-react';
import { PageHeader, PageContainer } from '../components/layout';
import { GlassCard, AnimatedButton, RiskBadge, Badge, EmptyState } from '../components/ui';
import { formatDate } from '../lib/utils';

const mockReports = [
  { id: '1', title: 'Domain Intelligence Report', type: 'Domain', date: '2024-01-15', status: 'completed', risk: 'low' },
  { id: '2', title: 'Username Investigation', type: 'Username', date: '2024-01-14', status: 'completed', risk: 'medium' },
  { id: '3', title: 'Dark Web Exposure Analysis', type: 'Dark Web', date: '2024-01-13', status: 'completed', risk: 'high' },
];

export default function ReportsPage() {
  return (
    <PageContainer>
      <PageHeader
        title="Reports Center"
        subtitle="Generated intelligence reports and export management"
        action={
          <AnimatedButton>
            <Plus className="w-4 h-4" />
            New Report
          </AnimatedButton>
        }
      />

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        <div className="lg:col-span-1">
          <GlassCard className="p-4">
            <h3 className="font-medium text-white mb-4">Filters</h3>
            <div className="space-y-2">
              {['All Reports', 'Completed', 'Draft', 'Generating'].map((filter) => (
                <button
                  key={filter}
                  className="w-full text-left px-3 py-2 rounded-lg text-sm text-white/70 hover:bg-white/10 hover:text-white transition-colors"
                >
                  {filter}
                </button>
              ))}
            </div>
          </GlassCard>
        </div>

        <div className="lg:col-span-3">
          {mockReports.length > 0 ? (
            <div className="space-y-3">
              {mockReports.map((report, index) => (
                <motion.div
                  key={report.id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                >
                  <GlassCard className="p-4">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-4">
                        <div className="p-3 rounded-lg bg-gradient-to-br from-accent-cyan/20 to-accent-violet/20">
                          <FileBarChart className="w-5 h-5 text-accent-cyan" />
                        </div>
                        <div>
                          <h4 className="font-medium text-white">{report.title}</h4>
                          <div className="flex items-center gap-2 mt-1">
                            <Badge variant="default">{report.type}</Badge>
                            <span className="text-xs text-white/50 flex items-center gap-1">
                              <Calendar className="w-3 h-3" />
                              {formatDate(report.date)}
                            </span>
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center gap-3">
                        <RiskBadge level={report.risk as any} size="sm" />
                        <div className="flex gap-1">
                          <AnimatedButton variant="ghost" size="sm">
                            <Eye className="w-4 h-4" />
                          </AnimatedButton>
                          <AnimatedButton variant="ghost" size="sm">
                            <Download className="w-4 h-4" />
                          </AnimatedButton>
                          <AnimatedButton variant="ghost" size="sm" className="text-accent-red hover:text-accent-redLight">
                            <Trash2 className="w-4 h-4" />
                          </AnimatedButton>
                        </div>
                      </div>
                    </div>
                  </GlassCard>
                </motion.div>
              ))}
            </div>
          ) : (
            <GlassCard className="p-12">
              <EmptyState
                icon={<FileBarChart className="w-12 h-12" />}
                title="No Reports Generated"
                description="Create your first intelligence report"
                action={<AnimatedButton><Plus className="w-4 h-4" />Create Report</AnimatedButton>}
              />
            </GlassCard>
          )}
        </div>
      </div>
    </PageContainer>
  );
}

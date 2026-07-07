import { motion } from 'framer-motion';
import {
  Activity,
  AlertTriangle,
  Target,
  Shield,
  TrendingUp,
  Search,
  Clock,
  ArrowRight,
  Sparkles,
  Globe,
  User,
  Mail,
  Server,
} from 'lucide-react';
import { PageHeader, PageContainer } from '../components/layout';
import {
  GlassCard,
  StatCard,
  RiskBadge,
  AnimatedButton,
  ProgressRing,
  LoadingBar,
} from '../components/ui';
import {
  ThreatTimelineChart,
  ModuleUsageChart,
  RiskDistributionChart,
  IntelligenceRadarChart,
} from '../components/charts/Charts';
import {
  threatTimelineData,
  moduleUsageData,
  riskDistributionData,
  intelligenceCoverageData,
  recentActivityData,
} from '../lib/mockData';
import { formatRelativeTime, cn } from '../lib/utils';
import { useNotificationStore } from '../store/appStore';
import { useEffect } from 'react';
import type { ActivityEvent } from '../types';

type QuickScanProps = {
  onSubmit: (type: string, query: string) => void;
};

function QuickScan({ onSubmit }: QuickScanProps) {
  const scanTypes = [
    { id: 'username', label: 'Username', icon: <User className="w-4 h-4" /> },
    { id: 'email', label: 'Email', icon: <Mail className="w-4 h-4" /> },
    { id: 'domain', label: 'Domain', icon: <Globe className="w-4 h-4" /> },
    { id: 'ip', label: 'IP', icon: <Server className="w-4 h-4" /> },
  ];

  return (
    <GlassCard className="p-6">
      <h3 className="text-lg font-semibold text-white mb-4">Quick Intelligence Scan</h3>
      <div className="flex gap-2 mb-4">
        {scanTypes.map((type) => (
          <button
            key={type.id}
            className={cn(
              'flex items-center gap-2 px-4 py-2 rounded-lg',
              'bg-white/5 border border-white/10',
              'text-white/70 hover:text-white hover:bg-white/10',
              'transition-all'
            )}
          >
            {type.icon}
            <span className="text-sm">{type.label}</span>
          </button>
        ))}
      </div>
      <div className="flex gap-3">
        <input
          type="text"
          placeholder="Enter target to scan..."
          className="flex-1 h-11 px-4 bg-glass-dark border border-glass-border rounded-lg text-white placeholder:text-white/40 focus:outline-none focus:ring-2 focus:ring-accent-cyan/30"
        />
        <AnimatedButton
          onClick={() => onSubmit('username', '')}
          glow
        >
          <Search className="w-4 h-4" />
          Scan
        </AnimatedButton>
      </div>
    </GlassCard>
  );
}

type ActivityFeedProps = {
  activities: ActivityEvent[];
};

function ActivityFeed({ activities }: ActivityFeedProps) {
  const typeColors = {
    scan: 'text-accent-cyan',
    correlation: 'text-accent-violet',
    insight: 'text-accent-emerald',
    report: 'text-accent-amber',
    alert: 'text-accent-red',
  };

  const severityBg = {
    safe: '',
    low: '',
    medium: 'border-l-2 border-accent-amber',
    high: 'border-l-2 border-accent-orange',
    critical: 'border-l-2 border-accent-red bg-accent-red/5',
    unknown: '',
  };

  return (
    <GlassCard className="h-full">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-white">Recent Activity</h3>
        <button className="text-xs text-accent-cyan hover:text-accent-cyanLight flex items-center gap-1">
          View all <ArrowRight className="w-3 h-3" />
        </button>
      </div>
      <div className="space-y-3 max-h-[320px] overflow-y-auto scrollbar-hide">
        {activities.map((activity, index) => (
          <motion.div
            key={activity.id}
            className={cn(
              'p-3 rounded-lg bg-white/5 hover:bg-white/10 transition-colors cursor-pointer',
              severityBg[activity.severity]
            )}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.1 }}
          >
            <div className="flex items-start justify-between">
              <div className="flex items-center gap-2">
                <span className={cn('capitalize text-xs font-medium', typeColors[activity.type])}>
                  {activity.type}
                </span>
                {activity.module && (
                  <span className="text-xs text-white/40 px-1.5 py-0.5 rounded bg-white/5">
                    {activity.module}
                  </span>
                )}
              </div>
              <span className="text-xs text-white/40">
                {formatRelativeTime(activity.timestamp)}
              </span>
            </div>
            <p className="text-sm text-white/80 mt-1 line-clamp-2">
              {activity.description}
            </p>
          </motion.div>
        ))}
      </div>
    </GlassCard>
  );
}

function AIInsights() {
  const insights = [
    {
      title: 'Suspicious Domain Pattern',
      description: 'Multiple domains registered within 24h using similar naming patterns detected',
      confidence: 85,
      severity: 'high' as const,
    },
    {
      title: 'Identity Correlation',
      description: '3 potential identity matches found between email and social profiles',
      confidence: 92,
      severity: 'medium' as const,
    },
    {
      title: 'Data Exposure Alert',
      description: 'Email detected in recent breach - credentials may be compromised',
      confidence: 100,
      severity: 'critical' as const,
    },
  ];

  return (
    <GlassCard className="h-full">
      <div className="flex items-center gap-2 mb-4">
        <Sparkles className="w-5 h-5 text-accent-cyan" />
        <h3 className="text-lg font-semibold text-white">AI Insights</h3>
      </div>
      <div className="space-y-3">
        {insights.map((insight, index) => (
          <motion.div
            key={index}
            className={cn(
              'p-3 rounded-lg border transition-all cursor-pointer',
              insight.severity === 'critical' && 'border-accent-red/30 bg-accent-red/5 hover:bg-accent-red/10',
              insight.severity === 'high' && 'border-accent-amber/30 bg-accent-amber/5 hover:bg-accent-amber/10',
              insight.severity === 'medium' && 'border-accent-cyan/30 bg-accent-cyan/5 hover:bg-accent-cyan/10'
            )}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            whileHover={{ scale: 1.02 }}
          >
            <div className="flex items-start justify-between">
              <h4 className="font-medium text-white text-sm">{insight.title}</h4>
              <RiskBadge level={insight.severity} size="sm" />
            </div>
            <p className="text-xs text-white/60 mt-1 line-clamp-2">
              {insight.description}
            </p>
            <div className="flex items-center justify-between mt-2">
              <div className="flex items-center gap-1">
                <div className="w-1.5 h-1.5 rounded-full bg-accent-cyan animate-pulse" />
                <span className="text-xs text-white/40">
                  {insight.confidence}% confidence
                </span>
              </div>
              <button className="text-xs text-accent-cyan hover:text-accent-cyanLight">
                Investigate
              </button>
            </div>
          </motion.div>
        ))}
      </div>
    </GlassCard>
  );
}

function IntelligenceScore() {
  return (
    <GlassCard className="h-full flex flex-col items-center justify-center p-6">
      <h3 className="text-sm font-medium text-white/70 mb-4">Overall Intelligence Score</h3>
      <ProgressRing
        progress={87}
        size={140}
        strokeWidth={10}
        color="gradient"
        showValue
      />
      <div className="mt-4 flex gap-4">
        <div className="text-center">
          <p className="text-2xl font-bold text-accent-cyan">156</p>
          <p className="text-xs text-white/50">Entities</p>
        </div>
        <div className="w-px h-10 bg-white/10" />
        <div className="text-center">
          <p className="text-2xl font-bold text-accent-violet">42</p>
          <p className="text-xs text-white/50">Correlations</p>
        </div>
      </div>
    </GlassCard>
  );
}

function ScanStatsMini() {
  const stats = [
    { label: 'Running', value: 3, color: 'cyan' as const },
    { label: 'Queued', value: 7, color: 'violet' as const },
    { label: 'Completed', value: 156, color: 'emerald' as const },
  ];

  return (
    <GlassCard className="p-4">
      <div className="flex items-center justify-between mb-3">
        <h4 className="text-sm font-medium text-white/70">Scan Queue</h4>
        <div className="flex items-center gap-1">
          <Activity className="w-4 h-4 text-accent-cyan animate-pulse" />
          <span className="text-xs text-accent-cyan">Live</span>
        </div>
      </div>
      <div className="space-y-3">
        {stats.map((stat, index) => (
          <div key={index} className="flex items-center justify-between">
            <span className="text-xs text-white/60">{stat.label}</span>
            <div className="flex items-center gap-2">
              <div className="w-24">
                <LoadingBar />
              </div>
              <span className={cn(
                'text-sm font-medium',
                stat.color === 'cyan' && 'text-accent-cyan',
                stat.color === 'violet' && 'text-accent-violet',
                stat.color === 'emerald' && 'text-accent-emerald'
              )}>
                {stat.value}
              </span>
            </div>
          </div>
        ))}
      </div>
    </GlassCard>
  );
}

export default function DashboardPage() {
  const { addNotification } = useNotificationStore();

  useEffect(() => {
    // Add some sample notifications
    addNotification({
      type: 'info',
      title: 'System Ready',
      message: 'OSINT Fusion intelligence platform initialized successfully',
    });
  }, [addNotification]);

  const handleQuickScan = (type: string, query: string) => {
    console.log('Quick scan:', type, query);
  };

  return (
    <PageContainer>
      <PageHeader
        title="Intelligence Command Center"
        subtitle="Real-time OSINT monitoring and analysis dashboard"
      />

      {/* Stats Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <StatCard
          title="Total Scans"
          value={12456}
          icon={<Search className="w-5 h-5" />}
          change={12}
          changeLabel="vs last week"
          trend="up"
          color="cyan"
          delay={0}
        />
        <StatCard
          title="Active Investigations"
          value={23}
          icon={<Target className="w-5 h-5" />}
          change={5}
          changeLabel="new today"
          trend="up"
          color="violet"
          delay={0.1}
        />
        <StatCard
          title="Threats Detected"
          value={89}
          icon={<AlertTriangle className="w-5 h-5" />}
          change={-8}
          changeLabel="vs yesterday"
          trend="down"
          color="amber"
          delay={0.2}
        />
        <StatCard
          title="Risk Score"
          value="Medium"
          icon={<Shield className="w-5 h-5" />}
          change={-3}
          changeLabel="improvement"
          trend="up"
          color="emerald"
          delay={0.3}
        />
      </div>

      {/* Quick Scan */}
      <div className="mb-6">
        <QuickScan onSubmit={handleQuickScan} />
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <ThreatTimelineChart data={threatTimelineData} />
        <ModuleUsageChart data={moduleUsageData} />
      </div>

      {/* Activity & Insights Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
        <div className="lg:col-span-2">
          <ActivityFeed activities={recentActivityData} />
        </div>
        <AIInsights />
      </div>

      {/* Bottom Row */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        <RiskDistributionChart data={riskDistributionData} />
        <IntelligenceRadarChart data={intelligenceCoverageData} />
        <IntelligenceScore />
        <ScanStatsMini />
      </div>
    </PageContainer>
  );
}

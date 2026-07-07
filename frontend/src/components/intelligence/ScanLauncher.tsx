import { motion } from 'framer-motion';
import { Search, Settings, Play, Pause, RotateCcw } from 'lucide-react';
import { useState } from 'react';
import { GlassCard, AnimatedButton, RiskBadge, ProgressRing, Badge } from '../ui';
import { cn } from '../../lib/utils';

type ScanLauncherProps = {
  type: 'username' | 'email' | 'domain' | 'ip' | 'phone' | 'company' | 'image' | 'document' | 'video' | 'darkweb';
  onScan: (target: string, options?: Record<string, unknown>) => void;
  placeholder?: string;
  validateTarget?: (target: string) => boolean;
};

export function ScanLauncher({
  type,
  onScan,
  placeholder = 'Enter target...',
  validateTarget,
}: ScanLauncherProps) {
  const [target, setTarget] = useState('');
  const [isValid, setIsValid] = useState(true);

  const handleScan = () => {
    if (!target.trim()) return;
    if (validateTarget && !validateTarget(target)) {
      setIsValid(false);
      return;
    }
    setIsValid(true);
    onScan(target);
  };

  const typeLabels = {
    username: 'Username',
    email: 'Email Address',
    domain: 'Domain',
    ip: 'IP Address',
    phone: 'Phone Number',
    company: 'Company',
    image: 'Image',
    document: 'Document',
    video: 'Video',
    darkweb: 'Dark Web Query',
  };

  return (
    <GlassCard className="p-6">
      <div className="flex items-center gap-3 mb-4">
        <div className="p-3 rounded-xl bg-gradient-to-br from-accent-cyan to-accent-violet">
          <Search className="w-5 h-5 text-white" />
        </div>
        <div>
          <h3 className="font-semibold text-white">
            {typeLabels[type]} Intelligence Scan
          </h3>
          <p className="text-xs text-white/50">
            Enter a target to begin OSINT analysis
          </p>
        </div>
      </div>

      <div className="space-y-4">
        <div>
          <input
            type="text"
            value={target}
            onChange={(e) => {
              setTarget(e.target.value);
              setIsValid(true);
            }}
            onKeyDown={(e) => e.key === 'Enter' && handleScan()}
            placeholder={placeholder}
            className={cn(
              'w-full h-12 px-4 bg-glass-dark border rounded-lg',
              'text-white placeholder:text-white/40',
              'focus:outline-none focus:ring-2 transition-all',
              isValid
                ? 'border-glass-border focus:ring-accent-cyan/30'
                : 'border-red-500/50 focus:ring-red-500/30'
            )}
          />
          {!isValid && (
            <motion.p
              initial={{ opacity: 0, y: -5 }}
              animate={{ opacity: 1, y: 0 }}
              className="text-xs text-red-400 mt-1"
            >
              Please enter a valid {typeLabels[type].toLowerCase()}
            </motion.p>
          )}
        </div>

        <div className="flex gap-3">
          <AnimatedButton onClick={handleScan} glow className="flex-1">
            <Play className="w-4 h-4" />
            Start Scan
          </AnimatedButton>
          <AnimatedButton variant="secondary">
            <Settings className="w-4 h-4" />
            Options
          </AnimatedButton>
        </div>
      </div>
    </GlassCard>
  );
}

type ScanStatusProps = {
  target: string;
  status: 'queued' | 'running' | 'completed' | 'failed' | 'paused';
  progress: number;
  currentStep?: string;
  elapsed?: number;
  onPause?: () => void;
  onRestart?: () => void;
  onCancel?: () => void;
};

export function ScanStatus({
  target,
  status,
  progress,
  currentStep,
  elapsed,
  onPause,
  onRestart,
}: ScanStatusProps) {
  const statusConfig = {
    queued: { label: 'Queued', color: 'text-white/60', bg: 'bg-white/5' },
    running: { label: 'Running', color: 'text-accent-cyan', bg: 'bg-accent-cyan/10' },
    completed: { label: 'Completed', color: 'text-accent-emerald', bg: 'bg-accent-emerald/10' },
    failed: { label: 'Failed', color: 'text-accent-red', bg: 'bg-accent-red/10' },
    paused: { label: 'Paused', color: 'text-accent-amber', bg: 'bg-accent-amber/10' },
  };

  const config = statusConfig[status];

  return (
    <GlassCard className="p-4">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-3">
          <div className={cn('w-2 h-2 rounded-full animate-pulse', config.bg, status === 'running' && 'bg-accent-cyan')} />
          <span className={cn('text-sm font-medium', config.color)}>
            {config.label}
          </span>
        </div>
        {elapsed && (
          <span className="text-xs text-white/40">
            {Math.floor(elapsed / 60)}:{(elapsed % 60).toString().padStart(2, '0')}
          </span>
        )}
      </div>

      <div className="mb-3">
        <p className="text-sm text-white truncate">{target}</p>
        {currentStep && (
          <p className="text-xs text-white/50 mt-1">{currentStep}</p>
        )}
      </div>

      {/* Progress bar */}
      <div className="mb-3">
        <div className="h-2 bg-white/10 rounded-full overflow-hidden">
          <motion.div
            className="h-full bg-gradient-to-r from-accent-cyan to-accent-violet rounded-full"
            initial={{ width: 0 }}
            animate={{ width: `${progress}%` }}
            transition={{ duration: 0.5 }}
          />
        </div>
        <div className="flex justify-between mt-1">
          <span className="text-xs text-white/40">{progress}%</span>
          {status === 'running' && (
            <motion.span
              animate={{ opacity: [0.4, 1] }}
              transition={{ duration: 0.5, repeat: Infinity }}
              className="text-xs text-accent-cyan"
            >
              Processing...
            </motion.span>
          )}
        </div>
      </div>

      {/* Actions */}
      {status === 'running' && onPause && (
        <AnimatedButton variant="secondary" size="sm" onClick={onPause} className="w-full">
          <Pause className="w-4 h-4" />
          Pause
        </AnimatedButton>
      )}
      {(status === 'paused' || status === 'failed') && onRestart && (
        <AnimatedButton variant="secondary" size="sm" onClick={onRestart} className="w-full">
          <RotateCcw className="w-4 h-4" />
          Restart
        </AnimatedButton>
      )}
    </GlassCard>
  );
}

type ResultsHeaderProps = {
  title: string;
  target: string;
  riskScore: { level: string; score: number };
  timestamp: string;
  exportable?: boolean;
  onExport?: () => void;
};

export function ResultsHeader({
  title,
  target,
  riskScore,
  timestamp,
  onExport,
}: ResultsHeaderProps) {
  return (
    <GlassCard className="p-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex items-center gap-4">
          <ProgressRing
            progress={riskScore.score}
            size={60}
            strokeWidth={4}
            color={riskScore.level === 'critical' ? 'red' : riskScore.level === 'high' ? 'amber' : riskScore.level === 'medium' ? 'violet' : 'cyan'}
            showValue
            animate={false}
          />
          <div>
            <h2 className="text-xl font-bold text-white">{title}</h2>
            <p className="text-sm text-white/60">{target}</p>
            <p className="text-xs text-white/40 mt-1">
              Analyzed {new Date(timestamp).toLocaleString()}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <RiskBadge level={riskScore.level as any} size="lg" />
          {onExport && (
            <AnimatedButton variant="secondary" onClick={onExport}>
              Export Report
            </AnimatedButton>
          )}
        </div>
      </div>
    </GlassCard>
  );
}

type ResultSectionProps = {
  title: string;
  children: React.ReactNode;
  className?: string;
  collapsible?: boolean;
  defaultOpen?: boolean;
};

export function ResultSection({
  title,
  children,
  className,
  collapsible = true,
  defaultOpen = true,
}: ResultSectionProps) {
  const [isOpen, setIsOpen] = useState(defaultOpen);

  return (
    <GlassCard className={cn('overflow-hidden', className)}>
      <div
        className={cn(
          'flex items-center justify-between p-4 border-b border-white/10',
          collapsible && 'cursor-pointer hover:bg-white/5'
        )}
        onClick={() => collapsible && setIsOpen(!isOpen)}
      >
        <h3 className="font-medium text-white">{title}</h3>
        {collapsible && (
          <motion.span
            animate={{ rotate: isOpen ? 180 : 0 }}
            className="text-white/60 text-xs"
          >
            ▼
          </motion.span>
        )}
      </div>
      <motion.div
        initial={false}
        animate={{ height: isOpen ? 'auto' : 0, opacity: isOpen ? 1 : 0 }}
        transition={{ duration: 0.2 }}
        className="overflow-hidden"
      >
        <div className="p-4">{children}</div>
      </motion.div>
    </GlassCard>
  );
}

type FindingCardProps = {
  title: string;
  description: string;
  severity: 'safe' | 'low' | 'medium' | 'high' | 'critical';
  source?: string;
  timestamp?: string;
  action?: React.ReactNode;
};

export function FindingCard({
  title,
  description,
  severity,
  source,
  timestamp,
  action,
}: FindingCardProps) {
  return (
    <motion.div
      className={cn(
        'p-4 rounded-lg border transition-all',
        severity === 'critical' && 'border-accent-red/30 bg-accent-red/5',
        severity === 'high' && 'border-accent-amber/30 bg-accent-amber/5',
        severity === 'medium' && 'border-white/10 bg-white/5',
        severity === 'low' && 'border-white/5 bg-white/[0.02]',
        severity === 'safe' && 'border-accent-emerald/20 bg-accent-emerald/5'
      )}
      whileHover={{ scale: 1.01 }}
    >
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-1">
            <h4 className="font-medium text-white text-sm">{title}</h4>
            <RiskBadge level={severity} size="sm" />
          </div>
          <p className="text-xs text-white/60 line-clamp-2">{description}</p>
          {(source || timestamp) && (
            <div className="flex items-center gap-3 mt-2 text-xs text-white/40">
              {source && <Badge variant="default">{source}</Badge>}
              {timestamp && <span>{new Date(timestamp).toLocaleDateString()}</span>}
            </div>
          )}
        </div>
        {action && <div>{action}</div>}
      </div>
    </motion.div>
  );
}

import { ReactNode } from 'react';

type NoResultsProps = {
  icon?: ReactNode;
  message?: string;
  description?: string;
};

export function NoResults({
  icon,
  message = 'No results found',
  description = 'Try adjusting your search parameters',
}: NoResultsProps) {
  return (
    <motion.div
      className="flex flex-col items-center justify-center py-16 text-center"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
    >
      {icon && (
        <div className="mb-4 p-4 rounded-2xl bg-white/5 text-white/30">
          {icon}
        </div>
      )}
      <h3 className="text-lg font-medium text-white/80 mb-1">{message}</h3>
      <p className="text-sm text-white/50">{description}</p>
    </motion.div>
  );
}

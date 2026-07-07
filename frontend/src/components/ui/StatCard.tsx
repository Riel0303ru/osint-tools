import { motion } from 'framer-motion';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';
import { cn, formatNumber, formatPercentage } from '../../lib/utils';
import type { ReactNode } from 'react';

type StatCardProps = {
  title: string;
  value: number | string;
  subtitle?: string;
  icon?: ReactNode;
  change?: number;
  changeLabel?: string;
  trend?: 'up' | 'down' | 'neutral';
  color?: 'cyan' | 'violet' | 'emerald' | 'amber' | 'red';
  className?: string;
  delay?: number;
};

export function StatCard({
  title,
  value,
  subtitle,
  icon,
  change,
  changeLabel,
  trend,
  color = 'cyan',
  className,
  delay = 0,
}: StatCardProps) {
  const colors = {
    cyan: {
      bg: 'from-accent-cyan/20 to-transparent',
      glow: 'shadow-[0_0_20px_rgba(0,212,255,0.2)]',
      border: 'border-accent-cyan/20',
      text: 'text-accent-cyan',
    },
    violet: {
      bg: 'from-accent-violet/20 to-transparent',
      glow: 'shadow-[0_0_20px_rgba(139,92,246,0.2)]',
      border: 'border-accent-violet/20',
      text: 'text-accent-violet',
    },
    emerald: {
      bg: 'from-accent-emerald/20 to-transparent',
      glow: 'shadow-[0_0_20px_rgba(16,185,129,0.2)]',
      border: 'border-accent-emerald/20',
      text: 'text-accent-emerald',
    },
    amber: {
      bg: 'from-accent-amber/20 to-transparent',
      glow: 'shadow-[0_0_20px_rgba(245,158,11,0.2)]',
      border: 'border-accent-amber/20',
      text: 'text-accent-amber',
    },
    red: {
      bg: 'from-accent-red/20 to-transparent',
      glow: 'shadow-[0_0_20px_rgba(239,68,68,0.2)]',
      border: 'border-accent-red/20',
      text: 'text-accent-red',
    },
  };

  const trendIcons = {
    up: <TrendingUp className="w-4 h-4" />,
    down: <TrendingDown className="w-4 h-4" />,
    neutral: <Minus className="w-4 h-4" />,
  };

  const trendColors = {
    up: 'text-accent-emerald',
    down: 'text-accent-red',
    neutral: 'text-gray-400',
  };

  return (
    <motion.div
      className={cn(
        'relative overflow-hidden glass-panel rounded-xl p-5 border',
        colors[color].border,
        colors[color].glow,
        className
      )}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay }}
    >
      {/* Background gradient */}
      <div
        className={cn(
          'absolute inset-0 bg-gradient-to-br opacity-50',
          colors[color].bg
        )}
      />

      <div className="relative">
        {/* Header */}
        <div className="flex items-center justify-between mb-3">
          <span className="text-sm text-white/60">{title}</span>
          {icon && (
            <div className={cn('p-2 rounded-lg bg-white/5', colors[color].text)}>
              {icon}
            </div>
          )}
        </div>

        {/* Value */}
        <div className="mb-2">
          <span className="text-3xl font-bold text-white">
            {typeof value === 'number' ? formatNumber(value) : value}
          </span>
        </div>

        {/* Subtitle & Change */}
        <div className="flex items-center gap-2">
          {subtitle && (
            <span className="text-xs text-white/50">{subtitle}</span>
          )}
          {change !== undefined && trend && (
            <div
              className={cn(
                'flex items-center gap-1 text-xs',
                trendColors[trend]
              )}
            >
              {trendIcons[trend]}
              <span>{formatPercentage(Math.abs(change))}</span>
              {changeLabel && <span className="text-white/50">{changeLabel}</span>}
            </div>
          )}
        </div>
      </div>
    </motion.div>
  );
}

type MiniStatProps = {
  label: string;
  value: string | number;
  icon?: ReactNode;
  color?: 'cyan' | 'violet' | 'emerald' | 'amber' | 'red';
};

export function MiniStat({ label, value, icon, color = 'cyan' }: MiniStatProps) {
  const colors = {
    cyan: 'text-accent-cyan',
    violet: 'text-accent-violet',
    emerald: 'text-accent-emerald',
    amber: 'text-accent-amber',
    red: 'text-accent-red',
  };

  return (
    <div className="flex items-center gap-2">
      {icon && <span className={colors[color]}>{icon}</span>}
      <div className="flex flex-col">
        <span className="text-xs text-white/50">{label}</span>
        <span className="text-sm font-medium text-white">{value}</span>
      </div>
    </div>
  );
}

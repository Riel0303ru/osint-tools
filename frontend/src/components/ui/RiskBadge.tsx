import { motion } from 'framer-motion';
import { cn, getRiskLevelColor, getRiskLevelText } from '../../lib/utils';
import type { RiskLevel } from '../../types';

type RiskBadgeProps = {
  level: RiskLevel;
  score?: number;
  showScore?: boolean;
  size?: 'sm' | 'md' | 'lg';
  animated?: boolean;
  className?: string;
};

export function RiskBadge({
  level,
  score,
  showScore = false,
  size = 'md',
  animated = false,
  className,
}: RiskBadgeProps) {
  const sizes = {
    sm: 'px-2 py-0.5 text-xs',
    md: 'px-3 py-1 text-sm',
    lg: 'px-4 py-1.5 text-base',
  };

  const backgrounds = {
    safe: 'bg-intel-safe/20 text-intel-safe border-intel-safe/30',
    low: 'bg-intel-low/20 text-intel-low border-intel-low/30',
    medium: 'bg-intel-medium/20 text-intel-medium border-intel-medium/30',
    high: 'bg-intel-high/20 text-intel-high border-intel-high/30',
    critical: 'bg-intel-critical/20 text-intel-critical border-intel-critical/30',
    unknown: 'bg-gray-500/20 text-gray-400 border-gray-500/30',
  };

  const glowing = {
    safe: '',
    low: '',
    medium: 'shadow-[0_0_10px_rgba(245,158,11,0.3)]',
    high: 'shadow-[0_0_15px_rgba(249,115,22,0.4)]',
    critical: 'shadow-[0_0_20px_rgba(239,68,68,0.5)]',
    unknown: '',
  };

  return (
    <motion.div
      className={cn(
        'inline-flex items-center gap-1.5 rounded-full border font-medium',
        sizes[size],
        backgrounds[level],
        animated && glowing[level],
        animated && level === 'critical' && 'animate-pulse',
        className
      )}
      animate={
        animated && level === 'critical'
          ? {
              scale: [1, 1.02, 1],
            }
          : undefined
      }
      transition={{
        duration: 1,
        repeat: Infinity,
      }}
    >
      <span
        className="w-2 h-2 rounded-full"
        style={{ backgroundColor: getRiskLevelColor(level) }}
      />
      <span>{getRiskLevelText(level)}</span>
      {showScore && score !== undefined && (
        <span className="opacity-70">({score})</span>
      )}
    </motion.div>
  );
}

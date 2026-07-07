import { motion } from 'framer-motion';
import { cn } from '../../lib/utils';

type ProgressRingProps = {
  progress: number;
  size?: number;
  strokeWidth?: number;
  color?: 'cyan' | 'violet' | 'emerald' | 'amber' | 'red' | 'gradient';
  showValue?: boolean;
  className?: string;
  animate?: boolean;
};

export function ProgressRing({
  progress,
  size = 120,
  strokeWidth = 8,
  color = 'cyan',
  showValue = true,
  className,
  animate = true,
}: ProgressRingProps) {
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (progress / 100) * circumference;

  const colors = {
    cyan: '#00d4ff',
    violet: '#8b5cf6',
    emerald: '#10b981',
    amber: '#f59e0b',
    red: '#ef4444',
    gradient: 'url(#progressGradient)',
  };

  return (
    <div className={cn('relative inline-flex items-center justify-center', className)}>
      <svg
        width={size}
        height={size}
        className="transform -rotate-90"
      >
        <defs>
          <linearGradient
            id="progressGradient"
            x1="0%"
            y1="0%"
            x2="100%"
            y2="0%"
          >
            <stop offset="0%" stopColor="#00d4ff" />
            <stop offset="100%" stopColor="#8b5cf6" />
          </linearGradient>
        </defs>
        {/* Background circle */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke="rgba(255, 255, 255, 0.1)"
          strokeWidth={strokeWidth}
          fill="none"
        />
        {/* Progress circle */}
        <motion.circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke={colors[color]}
          strokeWidth={strokeWidth}
          fill="none"
          strokeLinecap="round"
          initial={animate ? { strokeDashoffset: circumference } : false}
          animate={{ strokeDashoffset: offset }}
          transition={{ duration: 1, ease: 'easeOut' }}
          style={{
            strokeDasharray: circumference,
          }}
        />
      </svg>
      {showValue && (
        <motion.div
          className="absolute inset-0 flex items-center justify-center"
          initial={animate ? { opacity: 0, scale: 0.8 } : false}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.5 }}
        >
          <span className="text-2xl font-bold text-white">
            {Math.round(progress)}
          </span>
          <span className="text-sm text-white/60">%</span>
        </motion.div>
      )}
    </div>
  );
}

type MiniProgressRingProps = {
  progress: number;
  size?: number;
  color?: 'cyan' | 'violet' | 'emerald' | 'amber' | 'red';
  className?: string;
};

export function MiniProgressRing({
  progress,
  size = 32,
  color = 'cyan',
  className,
}: MiniProgressRingProps) {
  const strokeWidth = 3;
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (progress / 100) * circumference;

  const colors = {
    cyan: '#00d4ff',
    violet: '#8b5cf6',
    emerald: '#10b981',
    amber: '#f59e0b',
    red: '#ef4444',
  };

  return (
    <div className={cn('relative inline-flex', className)}>
      <svg
        width={size}
        height={size}
        className="transform -rotate-90"
      >
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke="rgba(255, 255, 255, 0.1)"
          strokeWidth={strokeWidth}
          fill="none"
        />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke={colors[color]}
          strokeWidth={strokeWidth}
          fill="none"
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
        />
      </svg>
    </div>
  );
}

type ProgressBarProps = {
  progress: number;
  color?: 'cyan' | 'violet' | 'emerald' | 'amber' | 'red' | 'gradient';
  size?: 'sm' | 'md' | 'lg';
  showLabel?: boolean;
  animated?: boolean;
  className?: string;
};

export function ProgressBar({
  progress,
  color = 'cyan',
  size = 'md',
  showLabel = false,
  animated = true,
  className,
}: ProgressBarProps) {
  const sizes = {
    sm: 'h-1',
    md: 'h-2',
    lg: 'h-3',
  };

  const backgrounds = {
    cyan: 'bg-accent-cyan',
    violet: 'bg-accent-violet',
    emerald: 'bg-accent-emerald',
    amber: 'bg-accent-amber',
    red: 'bg-accent-red',
    gradient: 'bg-gradient-to-r from-accent-cyan to-accent-violet',
  };

  return (
    <div className={cn('w-full', className)}>
      <div
        className={cn(
          'w-full bg-white/10 rounded-full overflow-hidden',
          sizes[size]
        )}
      >
        <motion.div
          className={cn('h-full rounded-full', backgrounds[color])}
          initial={animated ? { width: 0 } : false}
          animate={{ width: `${progress}%` }}
          transition={{ duration: 0.8, ease: 'easeOut' }}
        />
      </div>
      {showLabel && (
        <div className="flex justify-between mt-1 text-xs text-white/60">
          <span>Progress</span>
          <span>{Math.round(progress)}%</span>
        </div>
      )}
    </div>
  );
}

type LoadingBarProps = {
  className?: string;
};

export function LoadingBar({ className }: LoadingBarProps) {
  return (
    <div className={cn('h-0.5 w-full overflow-hidden bg-white/5', className)}>
      <motion.div
        className="h-full bg-gradient-to-r from-transparent via-accent-cyan to-transparent"
        animate={{
          x: ['-100%', '100%'],
        }}
        transition={{
          duration: 1.5,
          repeat: Infinity,
          ease: 'linear',
        }}
        style={{ width: '50%' }}
      />
    </div>
  );
}

import { motion } from 'framer-motion';
import { cn } from '../../lib/utils';

type SkeletonProps = {
  className?: string;
  variant?: 'text' | 'circular' | 'rectangular' | 'rounded';
  width?: string | number;
  height?: string | number;
  animate?: boolean;
};

export function Skeleton({
  className,
  variant = 'text',
  width,
  height,
  animate = true,
}: SkeletonProps) {
  const variants = {
    text: 'rounded',
    circular: 'rounded-full',
    rectangular: 'rounded-none',
    rounded: 'rounded-lg',
  };

  return (
    <motion.div
      className={cn(
        'bg-white/10',
        variants[variant],
        animate && 'animate-pulse',
        className
      )}
      style={{
        width: width,
        height: height || (variant === 'text' ? '1em' : undefined),
      }}
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
    />
  );
}

type SkeletonCardProps = {
  className?: string;
  lines?: number;
};

export function SkeletonCard({ className, lines = 3 }: SkeletonCardProps) {
  return (
    <div
      className={cn(
        'glass-panel rounded-xl p-4 space-y-3 animate-pulse',
        className
      )}
    >
      <Skeleton variant="rectangular" height={120} className="rounded-lg" />
      <Skeleton width="60%" />
      <div className="space-y-2">
        {Array.from({ length: lines }).map((_, i) => (
          <Skeleton key={i} width={`${100 - i * 15}%`} />
        ))}
      </div>
    </div>
  );
}

type SkeletonTableProps = {
  rows?: number;
  columns?: number;
  className?: string;
};

export function SkeletonTable({
  rows = 5,
  columns = 4,
  className,
}: SkeletonTableProps) {
  return (
    <div className={cn('space-y-2', className)}>
      {/* Header */}
      <div className="flex gap-4 p-3 glass-panel rounded-lg">
        {Array.from({ length: columns }).map((_, i) => (
          <Skeleton key={i} width={100} />
        ))}
      </div>
      {/* Rows */}
      {Array.from({ length: rows }).map((_, rowIndex) => (
        <div key={rowIndex} className="flex gap-4 p-3 glass-panel-light rounded-lg">
          {Array.from({ length: columns }).map((_, colIndex) => (
            <Skeleton key={colIndex} width={80 + Math.random() * 40} />
          ))}
        </div>
      ))}
    </div>
  );
}

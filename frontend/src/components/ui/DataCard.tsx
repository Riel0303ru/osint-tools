import { motion, AnimatePresence } from 'framer-motion';
import { X, ExternalLink, Copy, Check } from 'lucide-react';
import { cn } from '../../lib/utils';
import { useState, type ReactNode } from 'react';

type DataCardProps = {
  title: string;
  subtitle?: string;
  children: ReactNode;
  className?: string;
  collapsible?: boolean;
  defaultExpanded?: boolean;
  exportable?: boolean;
  onExport?: () => void;
};

export function DataCard({
  title,
  subtitle,
  children,
  className,
  collapsible = false,
  defaultExpanded = true,
  exportable = false,
  onExport,
}: DataCardProps) {
  const [expanded, setExpanded] = useState(defaultExpanded);

  return (
    <motion.div
      className={cn(
        'glass-panel rounded-xl overflow-hidden',
        className
      )}
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      {/* Header */}
      <div
        className={cn(
          'px-4 py-3 border-b border-white/10',
          collapsible && 'cursor-pointer hover:bg-white/5'
        )}
        onClick={() => collapsible && setExpanded(!expanded)}
      >
        <div className="flex items-center justify-between">
          <div>
            <h3 className="font-medium text-white">{title}</h3>
            {subtitle && (
              <p className="text-sm text-white/50 mt-0.5">{subtitle}</p>
            )}
          </div>
          <div className="flex items-center gap-2">
            {exportable && (
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  onExport?.();
                }}
                className="p-1.5 rounded hover:bg-white/10 text-white/60 hover:text-white transition-colors"
              >
                <ExternalLink className="w-4 h-4" />
              </button>
            )}
            {collapsible && (
              <motion.span
                animate={{ rotate: expanded ? 180 : 0 }}
                className="text-white/60"
              >
                ▼
              </motion.span>
            )}
          </div>
        </div>
      </div>

      {/* Content */}
      <AnimatePresence initial={false}>
        {expanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
          >
            <div className="p-4">{children}</div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}

type KeyValueItemProps = {
  label: string;
  value?: string | number | ReactNode;
  copyable?: boolean;
  className?: string;
  highlight?: boolean;
};

export function KeyValueItem({
  label,
  value,
  copyable = false,
  className,
  highlight = false,
}: KeyValueItemProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    if (typeof value === 'string' || typeof value === 'number') {
      await navigator.clipboard.writeText(String(value));
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <div
      className={cn(
        'flex items-center justify-between py-2 px-3 rounded-lg',
        highlight && 'bg-accent-cyan/10 border border-accent-cyan/20',
        className
      )}
    >
      <span className="text-sm text-white/50">{label}</span>
      <div className="flex items-center gap-2">
        <span
          className={cn(
            'text-sm font-medium',
            highlight ? 'text-accent-cyan' : 'text-white'
          )}
        >
          {value ?? '-'}
        </span>
        {copyable && value && (
          <button
            onClick={handleCopy}
            className="p-1 rounded hover:bg-white/10 text-white/40 hover:text-white transition-colors"
          >
            {copied ? (
              <Check className="w-3.5 h-3.5 text-accent-emerald" />
            ) : (
              <Copy className="w-3.5 h-3.5" />
            )}
          </button>
        )}
      </div>
    </div>
  );
}

type DataListProps = {
  items: Array<{ label: string; value: ReactNode; icon?: ReactNode }>;
  className?: string;
};

export function DataList({ items, className }: DataListProps) {
  return (
    <div className={cn('space-y-1', className)}>
      {items.map((item, index) => (
        <motion.div
          key={index}
          className="flex items-center justify-between py-2 px-3 rounded-lg hover:bg-white/5 transition-colors"
          initial={{ opacity: 0, x: -10 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.2, delay: index * 0.05 }}
        >
          <div className="flex items-center gap-2">
            {item.icon && (
              <span className="text-white/40">{item.icon}</span>
            )}
            <span className="text-sm text-white/50">{item.label}</span>
          </div>
          <span className="text-sm font-medium text-white">{item.value}</span>
        </motion.div>
      ))}
    </div>
  );
}

type EmptyStateProps = {
  icon?: ReactNode;
  title: string;
  description?: string;
  action?: ReactNode;
  className?: string;
};

export function EmptyState({
  icon,
  title,
  description,
  action,
  className,
}: EmptyStateProps) {
  return (
    <motion.div
      className={cn(
        'flex flex-col items-center justify-center py-12 px-4 text-center',
        className
      )}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
    >
      {icon && (
        <div className="mb-4 p-4 rounded-2xl bg-white/5 text-white/40">
          {icon}
        </div>
      )}
      <h3 className="text-lg font-medium text-white mb-1">{title}</h3>
      {description && (
        <p className="text-sm text-white/50 max-w-sm">{description}</p>
      )}
      {action && <div className="mt-4">{action}</div>}
    </motion.div>
  );
}

type StatusIndicatorProps = {
  status: 'online' | 'offline' | 'warning' | 'error' | 'loading';
  label?: string;
  pulse?: boolean;
  className?: string;
};

export function StatusIndicator({
  status,
  label,
  pulse = false,
  className,
}: StatusIndicatorProps) {
  const colors = {
    online: 'bg-accent-emerald',
    offline: 'bg-gray-400',
    warning: 'bg-accent-amber',
    error: 'bg-accent-red',
    loading: 'bg-accent-cyan',
  };

  return (
    <div className={cn('flex items-center gap-2', className)}>
      <div className="relative">
        <div className={cn('w-2 h-2 rounded-full', colors[status])} />
        {pulse && status === 'online' && (
          <div
            className={cn(
              'absolute inset-0 w-2 h-2 rounded-full animate-ping',
              colors[status]
            )}
          />
        )}
      </div>
      {label && <span className="text-sm text-white/70">{label}</span>}
    </div>
  );
}

type BadgeProps = {
  children: ReactNode;
  variant?: 'default' | 'success' | 'warning' | 'error' | 'info';
  className?: string;
};

export function Badge({ children, variant = 'default', className }: BadgeProps) {
  const variants = {
    default: 'bg-white/10 text-white border-white/20',
    success: 'bg-accent-emerald/20 text-accent-emerald border-accent-emerald/30',
    warning: 'bg-accent-amber/20 text-accent-amber border-accent-amber/30',
    error: 'bg-accent-red/20 text-accent-red border-accent-red/30',
    info: 'bg-accent-cyan/20 text-accent-cyan border-accent-cyan/30',
  };

  return (
    <span
      className={cn(
        'inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium border',
        variants[variant],
        className
      )}
    >
      {children}
    </span>
  );
}

export function Divider({ className }: { className?: string }) {
  return (
    <div className={cn('h-px bg-white/10 my-4', className)} />
  );
}

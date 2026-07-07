import { motion, type HTMLMotionProps } from 'framer-motion';
import { forwardRef } from 'react';
import { cn } from '../../lib/utils';

type GlassCardProps = HTMLMotionProps<'div'> & {
  variant?: 'default' | 'light' | 'dark' | 'bordered';
  glow?: boolean;
  glowColor?: 'cyan' | 'violet' | 'emerald' | 'none';
  hover?: boolean;
  interactive?: boolean;
};

export const GlassCard = forwardRef<HTMLDivElement, GlassCardProps>(
  (
    {
      className,
      variant = 'default',
      glow = false,
      glowColor = 'cyan',
      hover = true,
      interactive = false,
      children,
      ...props
    },
    ref
  ) => {
    const variants = {
      default: 'bg-[var(--glass-bg)] border-[var(--glass-border)]',
      light: 'bg-white/5 border-white/10',
      dark: 'bg-black/20 border-white/5',
      bordered: 'bg-[var(--glass-bg)] border-[var(--glass-border)] border-2',
    };

    const glowStyles = {
      cyan: 'hover:shadow-[0_0_30px_rgba(0,212,255,0.3)]',
      violet: 'hover:shadow-[0_0_30px_rgba(139,92,246,0.3)]',
      emerald: 'hover:shadow-[0_0_30px_rgba(16,185,129,0.3)]',
      none: '',
    };

    return (
      <motion.div
        ref={ref}
        className={cn(
          'rounded-xl backdrop-blur-xl shadow-lg border transition-all duration-300',
          variants[variant],
          glow && glowStyles[glowColor],
          hover && 'hover:shadow-xl hover:-translate-y-0.5',
          interactive && 'cursor-pointer',
          className
        )}
        whileHover={interactive ? { scale: 1.02 } : undefined}
        whileTap={interactive ? { scale: 0.98 } : undefined}
        {...props}
      >
        {children}
      </motion.div>
    );
  }
);

GlassCard.displayName = 'GlassCard';

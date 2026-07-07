import { motion } from 'framer-motion';
import { cn } from '../../lib/utils';

type GlowTextProps = {
  children: React.ReactNode;
  className?: string;
  color?: 'cyan' | 'violet' | 'emerald' | 'gradient';
  as?: keyof JSX.IntrinsicElements;
  animate?: boolean;
};

export function GlowText({
  children,
  className,
  color = 'cyan',
  as: Element = 'span',
  animate = false,
}: GlowTextProps) {
  const colors = {
    cyan: {
      text: 'text-accent-cyan',
      glow: 'text-shadow-[0_0_10px_rgba(0,212,255,0.5),0_0_20px_rgba(0,212,255,0.3)]',
    },
    violet: {
      text: 'text-accent-violet',
      glow: 'text-shadow-[0_0_10px_rgba(139,92,246,0.5),0_0_20px_rgba(139,92,246,0.3)]',
    },
    emerald: {
      text: 'text-accent-emerald',
      glow: 'text-shadow-[0_0_10px_rgba(16,185,129,0.5),0_0_20px_rgba(16,185,129,0.3)]',
    },
    gradient: {
      text: 'text-gradient-primary',
      glow: '',
    },
  };

  if (animate) {
    return (
      <motion.span
        className={cn(colors[color].text, colors[color].glow, className)}
        animate={{
          opacity: [1, 0.8, 1],
        }}
        transition={{
          duration: 2,
          repeat: Infinity,
          ease: 'easeInOut',
        }}
      >
        {children}
      </motion.span>
    );
  }

  return (
    <Element className={cn(colors[color].text, colors[color].glow, className)}>
      {children}
    </Element>
  );
}

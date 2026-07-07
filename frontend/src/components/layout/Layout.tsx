import { motion } from 'framer-motion';
import { Outlet } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { Header } from './Header';
import { AIAssistantPanel } from './AIAssistantPanel';
import { AnimatedBackground } from '../ui/ParticleBackground';
import { useSidebarStore, useThemeStore } from '../../store/appStore';
import { cn } from '../../lib/utils';

export function Layout() {
  const { collapsed } = useSidebarStore();
  const { mode } = useThemeStore();

  return (
    <div
      className={cn(
        'min-h-screen',
        mode === 'light' && 'light-theme'
      )}
    >
      {/* Animated background */}
      <AnimatedBackground
        showParticles={true}
        showGrid={true}
        showOrbs={true}
      />

      {/* Sidebar */}
      <Sidebar />

      {/* Main content */}
      <motion.div
        className="relative min-h-screen transition-all duration-300"
        animate={{
          marginLeft: collapsed ? 72 : 280,
        }}
        transition={{ duration: 0.3, ease: [0.4, 0, 0.2, 1] }}
        style={{
          marginLeft: 280,
        }}
      >
        {/* Mobile styles */}
        <div className="md:hidden ml-0" />

        {/* Header */}
        <Header />

        {/* Page content */}
        <main className="relative z-10 p-4 md:p-6">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <Outlet />
          </motion.div>
        </main>
      </motion.div>

      {/* AI Assistant Panel */}
      <AIAssistantPanel />
    </div>
  );
}

import { ReactNode } from 'react';

type PageHeaderProps = {
  title: string;
  subtitle?: string;
  action?: ReactNode;
  className?: string;
};

export function PageHeader({
  title,
  subtitle,
  action,
  className,
}: PageHeaderProps) {
  return (
    <motion.div
      className={cn('mb-6', className)}
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl md:text-3xl font-bold text-white">
            {title}
          </h1>
          {subtitle && (
            <p className="text-white/50 mt-1">{subtitle}</p>
          )}
        </div>
        {action && <div>{action}</div>}
      </div>
    </motion.div>
  );
}

type PageContainerProps = {
  children: ReactNode;
  className?: string;
};

export function PageContainer({ children, className }: PageContainerProps) {
  return (
    <div className={cn('max-w-7xl mx-auto', className)}>{children}</div>
  );
}

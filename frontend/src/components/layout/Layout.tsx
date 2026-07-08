import { motion } from 'framer-motion';
import { Outlet, useLocation } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { Header } from './Header';
import { AIAssistantPanel } from './AIAssistantPanel';
import { AnimatedBackground } from '../ui/ParticleBackground';
import { useSidebarStore, useThemeStore, useUIStore } from '../../store/appStore';
import { cn } from '../../lib/utils';
import { useEffect } from 'react';
import { AlertTriangle, X } from 'lucide-react';

export function Layout() {
  const { collapsed } = useSidebarStore();
  const { mode } = useThemeStore();
  const { warningToast, hideWarningToast, activeAbortController, setActiveAbortController, setLoading } = useUIStore();
  const location = useLocation();

  // 1. Abort active scan request on route change
  useEffect(() => {
    if (activeAbortController) {
      console.log("[INFO] Route changed. Aborting active scan request.");
      activeAbortController.abort();
      setActiveAbortController(null);
      setLoading(false); // Hide any global loading states
    }
  }, [location.pathname]);

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

      {/* Warning Modal Overlay */}
      {warningToast?.show && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 z-[9999] flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm"
        >
          <motion.div
            initial={{ scale: 0.9, opacity: 0, y: 20 }}
            animate={{ scale: 1, opacity: 1, y: 0 }}
            exit={{ scale: 0.9, opacity: 0, y: 20 }}
            transition={{ type: 'spring', duration: 0.4 }}
            className="relative max-w-md w-full bg-slate-950/95 border border-amber-500/40 rounded-xl shadow-2xl p-6 flex flex-col items-center text-center gap-4"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Warning Icon Container */}
            <div className="w-12 h-12 rounded-full bg-amber-500/20 flex items-center justify-center text-amber-500 animate-pulse">
              <AlertTriangle className="w-6 h-6" />
            </div>

            <div className="space-y-2">
              <h3 className="text-lg font-bold text-white">Pemindaian Sedang Berlangsung</h3>
              <p className="text-sm text-white/70 leading-relaxed">
                {warningToast.message}
              </p>
            </div>

            {/* Cancel Button */}
            <button
              onClick={() => {
                if (activeAbortController) {
                  activeAbortController.abort();
                }
                hideWarningToast();
              }}
              className="mt-2 px-5 py-2 bg-rose-600 hover:bg-rose-500 border border-rose-500/50 text-white text-xs font-semibold rounded-lg shadow-lg hover:shadow-rose-600/20 transition-all duration-200"
            >
              Batalkan Pemindaian
            </button>
          </motion.div>
        </motion.div>
      )}
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

import { motion, AnimatePresence } from 'framer-motion';
import {
  LayoutDashboard,
  User,
  Mail,
  Globe,
  Server,
  Phone,
  Building2,
  Image,
  FileText,
  Video,
  Skull,
  Network,
  GitBranch,
  Brain,
  FileBarChart,
  Settings,
  ChevronLeft,
  ChevronRight,
  Menu,
  X,
} from 'lucide-react';
import { cn } from '../../lib/utils';
import { useSidebarStore } from '../../store/appStore';
import { Link, useLocation } from 'react-router-dom';
import { useState } from 'react';

type NavItem = {
  id: string;
  label: string;
  icon: React.ReactNode;
  path: string;
  badge?: number;
};

const navItems: NavItem[] = [
  { id: 'dashboard', label: 'Dashboard', icon: <LayoutDashboard className="w-5 h-5" />, path: '/' },
  { id: 'username', label: 'Username Intelligence', icon: <User className="w-5 h-5" />, path: '/username' },
  { id: 'email', label: 'Email Intelligence', icon: <Mail className="w-5 h-5" />, path: '/email' },
  { id: 'domain', label: 'Domain Intelligence', icon: <Globe className="w-5 h-5" />, path: '/domain' },
  { id: 'ip', label: 'IP Intelligence', icon: <Server className="w-5 h-5" />, path: '/ip' },
  { id: 'phone', label: 'Phone Intelligence', icon: <Phone className="w-5 h-5" />, path: '/phone' },
  { id: 'company', label: 'Company Intelligence', icon: <Building2 className="w-5 h-5" />, path: '/company' },
  { id: 'image', label: 'Image Intelligence', icon: <Image className="w-5 h-5" />, path: '/image' },
  { id: 'document', label: 'Document Intelligence', icon: <FileText className="w-5 h-5" />, path: '/document' },
  { id: 'video', label: 'Video Intelligence', icon: <Video className="w-5 h-5" />, path: '/video' },
  { id: 'darkweb', label: 'Dark Web Intelligence', icon: <Skull className="w-5 h-5" />, path: '/darkweb' },
  { id: 'correlation', label: 'Correlation Engine', icon: <Network className="w-5 h-5" />, path: '/correlation' },
  { id: 'graph', label: 'Graph Analysis', icon: <GitBranch className="w-5 h-5" />, path: '/graph' },
  { id: 'ai', label: 'AI Analysis', icon: <Brain className="w-5 h-5" />, path: '/ai' },
  { id: 'reports', label: 'Reports', icon: <FileBarChart className="w-5 h-5" />, path: '/reports' },
  { id: 'settings', label: 'Settings', icon: <Settings className="w-5 h-5" />, path: '/settings' },
];

function NavItemComponent({
  item,
  collapsed,
  active,
}: {
  item: NavItem;
  collapsed: boolean;
  active: boolean;
}) {
  return (
    <Link to={item.path}>
      <motion.div
        className={cn(
          'relative flex items-center gap-3 px-3 py-2.5 rounded-lg cursor-pointer',
          'transition-all duration-200',
          active
            ? 'bg-accent-cyan/10 text-accent-cyan'
            : 'text-white/60 hover:text-white hover:bg-white/5'
        )}
        whileHover={{ x: collapsed ? 0 : 4 }}
        whileTap={{ scale: 0.98 }}
      >
        {/* Active indicator */}
        {active && (
          <motion.div
            className="absolute left-0 top-1/2 -translate-y-1/2 w-0.5 h-6 bg-accent-cyan rounded-r-full shadow-[0_0_10px_rgba(0,212,255,0.5)]"
            layoutId="activeIndicator"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ type: 'spring', stiffness: 300, damping: 30 }}
          />
        )}

        {/* Icon */}
        <div className={cn('flex-shrink-0', active && 'text-accent-cyan')}>
          {item.icon}
        </div>

        {/* Label */}
        <AnimatePresence>
          {!collapsed && (
            <motion.div
              className="flex-1 flex items-center justify-between overflow-hidden"
              initial={{ opacity: 0, width: 0 }}
              animate={{ opacity: 1, width: 'auto' }}
              exit={{ opacity: 0, width: 0 }}
              transition={{ duration: 0.2 }}
            >
              <span className="text-sm font-medium whitespace-nowrap">
                {item.label}
              </span>
              {item.badge && (
                <span className="px-1.5 py-0.5 text-xs bg-accent-cyan/20 text-accent-cyan rounded-full">
                  {item.badge}
                </span>
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>
    </Link>
  );
}

export function Sidebar() {
  const { collapsed, toggleCollapsed, mobileOpen, toggleMobile } =
    useSidebarStore();
  const location = useLocation();

  return (
    <>
      {/* Mobile menu button */}
      <button
        onClick={toggleMobile}
        className="fixed top-4 left-4 z-50 p-2 rounded-lg glass-panel md:hidden"
      >
        {mobileOpen ? (
          <X className="w-6 h-6 text-white" />
        ) : (
          <Menu className="w-6 h-6 text-white" />
        )}
      </button>

      {/* Mobile overlay */}
      <AnimatePresence>
        {mobileOpen && (
          <motion.div
            className="fixed inset-0 bg-black/50 z-40 md:hidden"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={toggleMobile}
          />
        )}
      </AnimatePresence>

      {/* Sidebar */}
      <motion.aside
        className={cn(
          'fixed left-0 top-0 h-full z-40',
          'glass-panel border-r border-white/10',
          'flex flex-col',
          // Desktop styles
          'hidden md:flex',
          // Mobile styles
          mobileOpen && 'flex'
        )}
        animate={{
          width: collapsed ? 72 : 280,
        }}
        transition={{ duration: 0.3, ease: [0.4, 0, 0.2, 1] }}
        style={{
          // Mobile positioning
          transform: mobileOpen ? 'translateX(0)' : undefined,
        }}
      >
        {/* Logo section */}
        <div className="flex items-center justify-between px-4 py-5 border-b border-white/10">
          <Link to="/" className="flex items-center gap-3">
            <motion.div
              className="w-10 h-10 rounded-xl bg-gradient-to-br from-accent-cyan to-accent-violet flex items-center justify-center shadow-[0_0_20px_rgba(0,212,255,0.3)]"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <span className="text-white font-bold text-lg">OF</span>
            </motion.div>
            <AnimatePresence>
              {!collapsed && (
                <motion.div
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -10 }}
                  transition={{ duration: 0.2 }}
                >
                  <h1 className="text-lg font-bold text-white">
                    OSINT Fusion
                  </h1>
                  <p className="text-xs text-white/50">
                    Intelligence Platform
                  </p>
                </motion.div>
              )}
            </AnimatePresence>
          </Link>

          {/* Collapse button (desktop only) */}
          <button
            onClick={toggleCollapsed}
            className="hidden md:flex p-2 rounded-lg hover:bg-white/10 text-white/60 hover:text-white transition-colors"
          >
            {collapsed ? (
              <ChevronRight className="w-4 h-4" />
            ) : (
              <ChevronLeft className="w-4 h-4" />
            )}
          </button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 overflow-y-auto py-4 px-3 scrollbar-hide">
          <div className="space-y-1">
            {navItems.map((item) => (
              <NavItemComponent
                key={item.id}
                item={item}
                collapsed={collapsed}
                active={location.pathname === item.path}
              />
            ))}
          </div>
        </nav>

        {/* User section */}
        <div className="border-t border-white/10 p-4">
          <motion.div
            className="flex items-center gap-3"
            whileHover={{ scale: collapsed ? 1 : 1.02 }}
          >
            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-accent-violet to-accent-cyan flex items-center justify-center">
              <span className="text-sm font-bold text-white">AI</span>
            </div>
            <AnimatePresence>
              {!collapsed && (
                <motion.div
                  className="flex-1 overflow-hidden"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                >
                  <p className="text-sm font-medium text-white truncate">
                    Intelligence Unit
                  </p>
                  <p className="text-xs text-white/50">Active Session</p>
                </motion.div>
              )}
            </AnimatePresence>
          </motion.div>
        </div>
      </motion.aside>
    </>
  );
}

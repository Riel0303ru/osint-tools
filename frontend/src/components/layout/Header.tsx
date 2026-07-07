import { motion, AnimatePresence } from 'framer-motion';
import {
  Bell,
  Search,
  Sun,
  Moon,
  Command,
  Sparkles,
  X,
  Check,
  AlertTriangle,
  Info,
  AlertCircle,
} from 'lucide-react';
import { cn } from '../../lib/utils';
import { useThemeStore, useNotificationStore, useUIStore } from '../../store/appStore';
import { useState } from 'react';
import type { Notification } from '../../types';

function NotificationItem({
  notification,
  onMarkRead,
  onRemove,
}: {
  notification: Notification;
  onMarkRead: () => void;
  onRemove: () => void;
}) {
  const icons = {
    info: <Info className="w-4 h-4 text-accent-cyan" />,
    success: <Check className="w-4 h-4 text-accent-emerald" />,
    warning: <AlertTriangle className="w-4 h-4 text-accent-amber" />,
    error: <AlertCircle className="w-4 h-4 text-accent-red" />,
    alert: <AlertCircle className="w-4 h-4 text-accent-red animate-pulse" />,
  };

  const backgrounds = {
    info: 'bg-accent-cyan/10',
    success: 'bg-accent-emerald/10',
    warning: 'bg-accent-amber/10',
    error: 'bg-accent-red/10',
    alert: 'bg-accent-red/10',
  };

  return (
    <motion.div
      className={cn(
        'relative p-3 rounded-lg border border-white/10 transition-colors',
        notification.read ? 'opacity-60' : '',
        backgrounds[notification.type]
      )}
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: notification.read ? 0.6 : 1, y: 0 }}
      exit={{ opacity: 0, x: 100 }}
      whileHover={{ backgroundColor: 'rgba(255,255,255,0.05)' }}
    >
      <div className="flex gap-3">
        <div className="flex-shrink-0 mt-0.5">{icons[notification.type]}</div>
        <div className="flex-1 min-w-0">
          <p className="text-sm font-medium text-white">{notification.title}</p>
          <p className="text-xs text-white/60 mt-0.5 line-clamp-2">
            {notification.message}
          </p>
        </div>
        <div className="flex-shrink-0 flex items-start gap-1">
          {!notification.read && (
            <button
              onClick={onMarkRead}
              className="p-1 rounded hover:bg-white/10 text-white/40 hover:text-white transition-colors"
            >
              <Check className="w-3.5 h-3.5" />
            </button>
          )}
          <button
            onClick={onRemove}
            className="p-1 rounded hover:bg-white/10 text-white/40 hover:text-white transition-colors"
          >
            <X className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>
    </motion.div>
  );
}

export function Header() {
  const { mode, toggleTheme } = useThemeStore();
  const {
    notifications,
    unreadCount,
    markAsRead,
    removeNotification,
    markAllAsRead,
  } = useNotificationStore();
  const { setAIPanelOpen } = useUIStore();
  const [showNotifications, setShowNotifications] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  return (
    <header className="sticky top-0 z-30 glass-panel border-b border-white/10">
      <div className="flex items-center justify-between h-16 px-4 md:px-6">
        {/* Search */}
        <div className="relative flex-1 max-w-xl ml-12 md:ml-0">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-white/40" />
          <input
            type="text"
            placeholder="Search intelligence data..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className={cn(
              'w-full h-10 pl-10 pr-4',
              'bg-glass-dark border border-glass-border rounded-lg',
              'text-sm text-white placeholder:text-white/40',
              'focus:outline-none focus:ring-2 focus:ring-accent-cyan/30 focus:border-accent-cyan/50',
              'transition-all'
            )}
          />
          <div className="absolute right-3 top-1/2 -translate-y-1/2 hidden md:flex items-center gap-1 text-white/40">
            <Command className="w-3 h-3" />
            <span className="text-xs">K</span>
          </div>
        </div>

        {/* Actions */}
        <div className="flex items-center gap-2 md:gap-3">
          {/* AI Assistant Button */}
          <motion.button
            onClick={() => setAIPanelOpen(true)}
            className={cn(
              'hidden md:flex items-center gap-2 px-4 py-2 rounded-lg',
              'bg-gradient-to-r from-accent-violet/20 to-accent-cyan/20',
              'border border-accent-cyan/30 text-white',
              'hover:from-accent-violet/30 hover:to-accent-cyan/30 transition-all'
            )}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            <Sparkles className="w-4 h-4 text-accent-cyan" />
            <span className="text-sm font-medium">AI Assistant</span>
          </motion.button>

          {/* Notifications */}
          <div className="relative">
            <motion.button
              onClick={() => setShowNotifications(!showNotifications)}
              className="relative p-2 rounded-lg hover:bg-white/10 text-white/70 hover:text-white transition-colors"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <Bell className="w-5 h-5" />
              {unreadCount > 0 && (
                <span className="absolute -top-0.5 -right-0.5 w-4 h-4 bg-accent-red rounded-full flex items-center justify-center text-xs text-white font-bold animate-pulse">
                  {unreadCount > 9 ? '9+' : unreadCount}
                </span>
              )}
            </motion.button>

            {/* Notifications dropdown */}
            <AnimatePresence>
              {showNotifications && (
                <>
                  <div
                    className="fixed inset-0 z-40"
                    onClick={() => setShowNotifications(false)}
                  />
                  <motion.div
                    className="absolute right-0 top-full mt-2 w-80 sm:w-96 glass-panel rounded-xl border border-white/10 overflow-hidden z-50"
                    initial={{ opacity: 0, y: -10, scale: 0.95 }}
                    animate={{ opacity: 1, y: 0, scale: 1 }}
                    exit={{ opacity: 0, y: -10, scale: 0.95 }}
                    transition={{ duration: 0.2 }}
                  >
                    {/* Header */}
                    <div className="flex items-center justify-between p-4 border-b border-white/10">
                      <h3 className="font-medium text-white">Notifications</h3>
                      {notifications.length > 0 && (
                        <button
                          onClick={markAllAsRead}
                          className="text-xs text-accent-cyan hover:text-accent-cyanLight transition-colors"
                        >
                          Mark all read
                        </button>
                      )}
                    </div>

                    {/* Notifications list */}
                    <div className="max-h-96 overflow-y-auto">
                      {notifications.length === 0 ? (
                        <div className="p-8 text-center text-white/50">
                          <Bell className="w-8 h-8 mx-auto mb-2 opacity-50" />
                          <p className="text-sm">No notifications</p>
                        </div>
                      ) : (
                        <div className="p-2 space-y-2">
                          {notifications.slice(0, 10).map((notification) => (
                            <NotificationItem
                              key={notification.id}
                              notification={notification}
                              onMarkRead={() => markAsRead(notification.id)}
                              onRemove={() => removeNotification(notification.id)}
                            />
                          ))}
                        </div>
                      )}
                    </div>
                  </motion.div>
                </>
              )}
            </AnimatePresence>
          </div>

          {/* Theme toggle */}
          <motion.button
            onClick={toggleTheme}
            className="p-2 rounded-lg hover:bg-white/10 text-white/70 hover:text-white transition-colors"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            {mode === 'dark' ? (
              <Sun className="w-5 h-5" />
            ) : (
              <Moon className="w-5 h-5" />
            )}
          </motion.button>
        </div>
      </div>
    </header>
  );
}

import { motion } from 'framer-motion';
import { Settings, Palette, Globe, Shield, Bell, Database, Key } from 'lucide-react';
import { PageHeader, PageContainer } from '../components/layout';
import { GlassCard, AnimatedButton } from '../components/ui';
import { useThemeStore } from '../store/appStore';

const settingsSections = [
  {
    title: 'Appearance',
    icon: Palette,
    items: [
      { label: 'Theme', type: 'select', options: ['dark', 'light'] },
      { label: 'Accent Color', type: 'select', options: ['Cyan', 'Violet', 'Emerald', 'Amber'] },
      { label: 'Reduce Animations', type: 'toggle' },
    ],
  },
  {
    title: 'General',
    icon: Globe,
    items: [
      { label: 'Language', type: 'select', options: ['English', 'Spanish', 'French', 'German'] },
      { label: 'Timezone', type: 'select', options: ['UTC', 'PST', 'EST', 'GMT'] },
      { label: 'Date Format', type: 'select', options: ['MM/DD/YYYY', 'DD/MM/YYYY', 'YYYY-MM-DD'] },
    ],
  },
  {
    title: 'Security',
    icon: Shield,
    items: [
      { label: 'Two-Factor Authentication', type: 'toggle' },
      { label: 'Session Timeout', type: 'select', options: ['15 min', '30 min', '1 hour', 'Never'] },
      { label: 'Export Restrictions', type: 'toggle' },
    ],
  },
  {
    title: 'Notifications',
    icon: Bell,
    items: [
      { label: 'Scan Complete Notifications', type: 'toggle' },
      { label: 'Threat Alerts', type: 'toggle' },
      { label: 'Email Notifications', type: 'toggle' },
      { label: 'Sound Effects', type: 'toggle' },
    ],
  },
];

export default function SettingsPage() {
  const { mode, toggleTheme } = useThemeStore();

  return (
    <PageContainer>
      <PageHeader title="Settings" subtitle="Configure your OSINT Fusion preferences" />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1">
          <GlassCard className="p-4">
            <h3 className="font-medium text-white mb-4 flex items-center gap-2">
              <Database className="w-4 h-4" />
              Quick Actions
            </h3>
            <div className="space-y-2">
              <AnimatedButton variant="secondary" className="w-full justify-start">
                <Key className="w-4 h-4" />
                API Keys
              </AnimatedButton>
              <AnimatedButton variant="secondary" className="w-full justify-start">
                <Database className="w-4 h-4" />
                Data Management
              </AnimatedButton>
              <AnimatedButton variant="secondary" className="w-full justify-start">
                <Shield className="w-4 h-4" />
                Privacy Settings
              </AnimatedButton>
            </div>
          </GlassCard>
        </div>

        <div className="lg:col-span-2 space-y-6">
          {settingsSections.map((section, sectionIndex) => (
            <motion.div
              key={section.title}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: sectionIndex * 0.1 }}
            >
              <GlassCard className="p-6">
                <h3 className="font-medium text-white mb-4 flex items-center gap-2">
                  <section.icon className="w-4 h-4 text-accent-cyan" />
                  {section.title}
                </h3>
                <div className="space-y-4">
                  {section.items.map((item, itemIndex) => (
                    <div key={item.label} className="flex items-center justify-between">
                      <span className="text-sm text-white/70">{item.label}</span>
                      {item.type === 'toggle' ? (
                        <button
                          className={`w-12 h-6 rounded-full transition-colors relative ${
                            item.label.includes('Two-Factor') ? 'bg-accent-cyan' :
                            item.label.includes('Notifications') ? 'bg-accent-cyan' :
                            'bg-white/20'
                          }`}
                          onClick={() => {}}
                        >
                          <div
                            className={`absolute top-1 w-4 h-4 bg-white rounded-full transition-transform ${
                              item.label.includes('Two-Factor') || item.label.includes('Notifications') ? 'translate-x-7' : 'translate-x-1'
                            }`}
                          />
                        </button>
                      ) : (
                        <select
                          className="bg-glass-dark border border-glass-border rounded-lg px-3 py-1.5 text-sm text-white focus:outline-none focus:ring-2 focus:ring-accent-cyan/30"
                          onChange={(e) => {
                            if (item.label === 'Theme') {
                              if (e.target.value !== mode) toggleTheme();
                            }
                          }}
                          defaultValue={
                            item.label === 'Theme' ? mode :
                            item.options ? item.options[0] : ''
                          }
                        >
                          {item.options?.map((option) => (
                            <option key={option} value={option}>
                              {option}
                            </option>
                          ))}
                        </select>
                      )}
                    </div>
                  ))}
                </div>
              </GlassCard>
            </motion.div>
          ))}
        </div>
      </div>
    </PageContainer>
  );
}

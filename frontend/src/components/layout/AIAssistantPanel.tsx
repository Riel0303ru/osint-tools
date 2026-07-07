import { motion, AnimatePresence } from 'framer-motion';
import { X, Send, Sparkles, Loader, Bot, User } from 'lucide-react';
import { cn } from '../../lib/utils';
import { useUIStore } from '../../store/appStore';
import { useState, useRef, useEffect } from 'react';

type Message = {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
};

export function AIAssistantPanel() {
  const { aiPanelOpen, setAIPanelOpen } = useUIStore();
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      role: 'assistant',
      content:
        'Hello! I am your OSINT Intelligence Assistant. I can help you analyze data, suggest investigation strategies, and provide insights on your intelligence queries. How can I assist you today?',
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input.trim(),
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsTyping(true);

    // Simulate AI response
    setTimeout(() => {
      const responses = [
        "Based on the intelligence data, I recommend starting with a domain reconnaissance to map the target's infrastructure. This will help identify subdomains, SSL certificates, and potential entry points for further investigation.",
        "I've analyzed the correlation patterns. There's a 78% confidence link between the username 'john_doe' and the email 'j.doe@company.com' based on shared platform registrations and timeline patterns.",
        "The image analysis suggests potential EXIF data manipulation. The GPS coordinates were likely stripped, but I can detect the original camera model (iPhone 14 Pro) from the remaining metadata signatures.",
        "For this type of investigation, I suggest using the Correlation Engine to map relationships between the discovered entities. This will help visualize the connections and identify hidden patterns.",
      ];

      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: responses[Math.floor(Math.random() * responses.length)],
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, aiMessage]);
      setIsTyping(false);
    }, 1500);
  };

  return (
    <AnimatePresence>
      {aiPanelOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            className="fixed inset-0 bg-black/50 z-40"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setAIPanelOpen(false)}
          />

          {/* Panel */}
          <motion.div
            className="fixed right-0 top-0 h-full w-full max-w-md z-50 glass-panel border-l border-white/10 flex flex-col"
            initial={{ x: '100%' }}
            animate={{ x: 0 }}
            exit={{ x: '100%' }}
            transition={{ type: 'spring', damping: 25, stiffness: 300 }}
          >
            {/* Header */}
            <div className="flex items-center justify-between p-4 border-b border-white/10">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-accent-violet to-accent-cyan flex items-center justify-center">
                  <Sparkles className="w-5 h-5 text-white" />
                </div>
                <div>
                  <h3 className="font-medium text-white">AI Assistant</h3>
                  <p className="text-xs text-white/50">Intelligence Copilot</p>
                </div>
              </div>
              <button
                onClick={() => setAIPanelOpen(false)}
                className="p-2 rounded-lg hover:bg-white/10 text-white/60 hover:text-white transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4 scrollbar-hide">
              {messages.map((message) => (
                <motion.div
                  key={message.id}
                  className={cn(
                    'flex gap-3',
                    message.role === 'user' && 'flex-row-reverse'
                  )}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.3 }}
                >
                  <div
                    className={cn(
                      'flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center',
                      message.role === 'assistant'
                        ? 'bg-gradient-to-br from-accent-violet to-accent-cyan'
                        : 'bg-white/10'
                    )}
                  >
                    {message.role === 'assistant' ? (
                      <Bot className="w-4 h-4 text-white" />
                    ) : (
                      <User className="w-4 h-4 text-white/70" />
                    )}
                  </div>
                  <div
                    className={cn(
                      'flex-1 max-w-[80%] p-3 rounded-xl',
                      message.role === 'assistant'
                        ? 'bg-white/5 border border-white/10'
                        : 'bg-accent-cyan/10 border border-accent-cyan/20'
                    )}
                  >
                    <p className="text-sm text-white leading-relaxed">
                      {message.content}
                    </p>
                    <p className="text-xs text-white/40 mt-1">
                      {message.timestamp.toLocaleTimeString()}
                    </p>
                  </div>
                </motion.div>
              ))}

              {/* Typing indicator */}
              {isTyping && (
                <motion.div
                  className="flex gap-3"
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                >
                  <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-accent-violet to-accent-cyan flex items-center justify-center">
                    <Bot className="w-4 h-4 text-white" />
                  </div>
                  <div className="bg-white/5 border border-white/10 p-3 rounded-xl">
                    <div className="flex gap-1">
                      {[0, 1, 2].map((i) => (
                        <motion.div
                          key={i}
                          className="w-2 h-2 bg-white/40 rounded-full"
                          animate={{ opacity: [0.4, 1, 0.4] }}
                          transition={{
                            duration: 1,
                            repeat: Infinity,
                            delay: i * 0.2,
                          }}
                        />
                      ))}
                    </div>
                  </div>
                </motion.div>
              )}

              <div ref={messagesEndRef} />
            </div>

            {/* Input */}
            <div className="p-4 border-t border-white/10">
              <div className="flex gap-2">
                <input
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                  placeholder="Ask for intelligence insights..."
                  className="flex-1 h-10 px-4 bg-glass-dark border border-glass-border rounded-lg text-sm text-white placeholder:text-white/40 focus:outline-none focus:ring-2 focus:ring-accent-cyan/30"
                />
                <motion.button
                  onClick={handleSend}
                  disabled={!input.trim() || isTyping}
                  className={cn(
                    'h-10 w-10 rounded-lg flex items-center justify-center',
                    'bg-gradient-to-r from-accent-violet to-accent-cyan',
                    'disabled:opacity-50 disabled:cursor-not-allowed'
                  )}
                  whileHover={{ scale: input.trim() ? 1.05 : 1 }}
                  whileTap={{ scale: input.trim() ? 0.95 : 1 }}
                >
                  {isTyping ? (
                    <Loader className="w-4 h-4 text-white animate-spin" />
                  ) : (
                    <Send className="w-4 h-4 text-white" />
                  )}
                </motion.button>
              </div>

              {/* Quick actions */}
              <div className="flex gap-2 mt-3 overflow-x-auto scrollbar-hide">
                {[
                  'Analyze correlations',
                  'Suggest next steps',
                  'Risk assessment',
                  'Generate report',
                ].map((action) => (
                  <button
                    key={action}
                    onClick={() => setInput(action)}
                    className="flex-shrink-0 px-3 py-1.5 text-xs rounded-full bg-white/5 border border-white/10 text-white/60 hover:text-white hover:bg-white/10 transition-colors"
                  >
                    {action}
                  </button>
                ))}
              </div>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}

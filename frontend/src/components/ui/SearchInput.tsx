import { motion } from 'framer-motion';
import { Search, X } from 'lucide-react';
import { cn } from '../../lib/utils';
import { type ReactNode, forwardRef } from 'react';

type SearchInputProps = {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  icon?: ReactNode;
  rightIcon?: ReactNode;
  loading?: boolean;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
  autoFocus?: boolean;
};

export const SearchInput = forwardRef<HTMLInputElement, SearchInputProps>(
  (
    {
      value,
      onChange,
      placeholder = 'Search...',
      icon,
      rightIcon,
      loading = false,
      size = 'md',
      className,
      autoFocus,
    },
    ref
  ) => {
    const sizes = {
      sm: 'h-9 text-sm',
      md: 'h-11 text-sm',
      lg: 'h-14 text-base',
    };

    const iconSizes = {
      sm: 'w-4 h-4',
      md: 'w-5 h-5',
      lg: 'w-5 h-5',
    };

    return (
      <div className={cn('relative', className)}>
        <div className="absolute left-4 top-1/2 -translate-y-1/2 text-white/40">
          {loading ? (
            <motion.div
              className={cn(iconSizes[size])}
              animate={{ rotate: 360 }}
              transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
            >
              <div className="w-full h-full border-2 border-accent-cyan/30 border-t-accent-cyan rounded-full" />
            </motion.div>
          ) : icon ? (
            <span className={iconSizes[size]}>{icon}</span>
          ) : (
            <Search className={iconSizes[size]} />
          )}
        </div>
        <input
          ref={ref}
          type="text"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder={placeholder}
          autoFocus={autoFocus}
          className={cn(
            'w-full bg-glass-dark border border-glass-border rounded-xl',
            'pl-12 pr-4 text-white placeholder:text-white/40',
            'focus:outline-none focus:ring-2 focus:ring-accent-cyan/30 focus:border-accent-cyan/50',
            'transition-all duration-200',
            sizes[size]
          )}
        />
        {rightIcon && (
          <div className="absolute right-4 top-1/2 -translate-y-1/2">
            {rightIcon}
          </div>
        )}
        {value && !rightIcon && (
          <button
            onClick={() => onChange('')}
            className="absolute right-4 top-1/2 -translate-y-1/2 text-white/40 hover:text-white/60 transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        )}
      </div>
    );
  }
);

SearchInput.displayName = 'SearchInput';

type FormInputProps = {
  label?: string;
  error?: string;
  icon?: ReactNode;
} & React.InputHTMLAttributes<HTMLInputElement>;

export const FormInput = forwardRef<HTMLInputElement, FormInputProps>(
  ({ label, error, icon, className, ...props }, ref) => {
    return (
      <div className="space-y-2">
        {label && (
          <label className="block text-sm font-medium text-white/70">
            {label}
          </label>
        )}
        <div className="relative">
          {icon && (
            <div className="absolute left-3 top-1/2 -translate-y-1/2 text-white/40">
              {icon}
            </div>
          )}
          <input
            ref={ref}
            className={cn(
              'w-full bg-glass-dark border border-glass-border rounded-lg',
              'px-4 py-2.5 text-white placeholder:text-white/40',
              'focus:outline-none focus:ring-2 focus:ring-accent-cyan/30 focus:border-accent-cyan/50',
              'transition-all duration-200',
              icon && 'pl-10',
              error && 'border-red-500/50 focus:ring-red-500/30',
              className
            )}
            {...props}
          />
        </div>
        {error && (
          <motion.p
            initial={{ opacity: 0, y: -5 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-xs text-red-400"
          >
            {error}
          </motion.p>
        )}
      </div>
    );
  }
);

FormInput.displayName = 'FormInput';

type FormTextareaProps = {
  label?: string;
  error?: string;
} & React.TextareaHTMLAttributes<HTMLTextAreaElement>;

export const FormTextarea = forwardRef<HTMLTextAreaElement, FormTextareaProps>(
  ({ label, error, className, ...props }, ref) => {
    return (
      <div className="space-y-2">
        {label && (
          <label className="block text-sm font-medium text-white/70">
            {label}
          </label>
        )}
        <textarea
          ref={ref}
          className={cn(
            'w-full bg-glass-dark border border-glass-border rounded-lg',
            'px-4 py-2.5 text-white placeholder:text-white/40',
            'focus:outline-none focus:ring-2 focus:ring-accent-cyan/30 focus:border-accent-cyan/50',
            'transition-all duration-200 resize-none',
            error && 'border-red-500/50 focus:ring-red-500/30',
            className
          )}
          {...props}
        />
        {error && (
          <motion.p
            initial={{ opacity: 0, y: -5 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-xs text-red-400"
          >
            {error}
          </motion.p>
        )}
      </div>
    );
  }
);

FormTextarea.displayName = 'FormTextarea';

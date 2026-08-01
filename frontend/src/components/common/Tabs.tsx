import React from 'react';
import { motion } from 'framer-motion';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export interface TabItem {
  id: string;
  label: string;
  badge?: string | number;
  icon?: React.ReactNode;
}

export interface TabsProps {
  tabs: TabItem[];
  activeTab: string;
  onChange: (id: string) => void;
  className?: string;
  size?: 'sm' | 'md' | 'lg';
}

export const Tabs: React.FC<TabsProps> = ({
  tabs,
  activeTab,
  onChange,
  className,
  size = 'md',
}) => {
  const sizes = {
    sm: 'text-xs px-2.5 py-1 gap-1.5',
    md: 'text-xs px-3.5 py-1.5 gap-2 font-medium',
    lg: 'text-sm px-4 py-2 gap-2 font-medium',
  };

  return (
    <div
      className={twMerge(
        clsx(
          'inline-flex items-center rounded-xl bg-slate-950/80 p-1 border border-slate-800/80 backdrop-blur-md',
          className
        )
      )}
    >
      {tabs.map((tab) => {
        const isActive = activeTab === tab.id;

        return (
          <button
            key={tab.id}
            onClick={() => onChange(tab.id)}
            className={clsx(
              'relative flex items-center rounded-lg transition-colors select-none cursor-pointer',
              sizes[size],
              isActive ? 'text-cyan-300 font-semibold' : 'text-slate-400 hover:text-slate-200'
            )}
          >
            {isActive && (
              <motion.div
                layoutId="activeTabPill"
                className="absolute inset-0 rounded-lg bg-slate-800/90 border border-slate-700/80 shadow-md shadow-slate-950/50"
                transition={{ type: 'spring', bounce: 0.15, duration: 0.3 }}
              />
            )}
            <span className="relative z-10 flex items-center gap-1.5">
              {tab.icon && <span>{tab.icon}</span>}
              <span>{tab.label}</span>
              {tab.badge !== undefined && (
                <span
                  className={clsx(
                    'rounded-full px-1.5 py-0.5 text-[10px] font-mono leading-none',
                    isActive ? 'bg-cyan-950 text-cyan-300 border border-cyan-800/60' : 'bg-slate-800 text-slate-400'
                  )}
                >
                  {tab.badge}
                </span>
              )}
            </span>
          </button>
        );
      })}
    </div>
  );
};

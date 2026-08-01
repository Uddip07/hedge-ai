import React from 'react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'glass' | 'bordered' | 'gradient';
  glow?: 'none' | 'emerald' | 'rose' | 'cyan';
}

export const Card: React.FC<CardProps> = ({
  variant = 'default',
  glow = 'none',
  className,
  children,
  ...props
}) => {
  const baseStyles = 'rounded-xl transition-all duration-200 overflow-hidden';

  const variants = {
    default: 'bg-slate-900/90 border border-slate-800/80 shadow-xl shadow-slate-950/50',
    glass: 'bg-slate-900/60 backdrop-blur-md border border-slate-800/60 shadow-xl shadow-slate-950/60',
    bordered: 'bg-slate-950 border border-slate-800 shadow-md',
    gradient: 'bg-gradient-to-br from-slate-900/90 via-slate-900/60 to-slate-950 border border-slate-800/80 shadow-xl',
  };

  const glows = {
    none: '',
    emerald: 'hover:border-emerald-500/50 hover:shadow-emerald-950/30',
    rose: 'hover:border-rose-500/50 hover:shadow-rose-950/30',
    cyan: 'hover:border-cyan-500/50 hover:shadow-cyan-950/30',
  };

  return (
    <div className={twMerge(clsx(baseStyles, variants[variant], glows[glow], className))} {...props}>
      {children}
    </div>
  );
};

export const CardHeader: React.FC<React.HTMLAttributes<HTMLDivElement>> = ({
  className,
  children,
  ...props
}) => (
  <div className={twMerge(clsx('flex flex-col space-y-1.5 p-5 border-b border-slate-800/60', className))} {...props}>
    {children}
  </div>
);

export const CardTitle: React.FC<React.HTMLAttributes<HTMLHeadingElement>> = ({
  className,
  children,
  ...props
}) => (
  <h3 className={twMerge(clsx('text-base font-semibold text-slate-100 tracking-tight flex items-center gap-2', className))} {...props}>
    {children}
  </h3>
);

export const CardDescription: React.FC<React.HTMLAttributes<HTMLParagraphElement>> = ({
  className,
  children,
  ...props
}) => (
  <p className={twMerge(clsx('text-xs text-slate-400 font-normal leading-relaxed', className))} {...props}>
    {children}
  </p>
);

export const CardContent: React.FC<React.HTMLAttributes<HTMLDivElement>> = ({
  className,
  children,
  ...props
}) => (
  <div className={twMerge(clsx('p-5', className))} {...props}>
    {children}
  </div>
);

export const CardFooter: React.FC<React.HTMLAttributes<HTMLDivElement>> = ({
  className,
  children,
  ...props
}) => (
  <div className={twMerge(clsx('flex items-center p-4 border-t border-slate-800/60 bg-slate-950/40 text-xs text-slate-400', className))} {...props}>
    {children}
  </div>
);

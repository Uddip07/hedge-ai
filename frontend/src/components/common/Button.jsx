import React from 'react';
import { Loader2 } from 'lucide-react';

export const Button = ({
  children,
  variant = 'primary',
  size = 'md',
  isLoading = false,
  disabled = false,
  leftIcon,
  rightIcon,
  className = '',
  type = 'button',
  onClick,
  ...props
}) => {
  const baseStyles =
    'inline-flex items-center justify-center font-mono font-semibold rounded-xl transition-all duration-150 select-none focus:outline-none focus:ring-2 focus:ring-cyan-500/50 disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer';

  const sizeStyles = {
    xs: 'px-2 py-1 text-[11px] gap-1',
    sm: 'px-3 py-1.5 text-xs gap-1.5',
    md: 'px-4 py-2 text-xs gap-2',
    lg: 'px-5 py-2.5 text-sm gap-2.5',
  };

  const variantStyles = {
    primary:
      'bg-cyan-500 hover:bg-cyan-400 text-slate-950 shadow-md shadow-cyan-950/50 border border-cyan-400 active:scale-[0.98]',
    secondary:
      'bg-slate-800 hover:bg-slate-700 text-slate-100 border border-slate-700 active:scale-[0.98]',
    outline:
      'bg-transparent hover:bg-white/5 text-slate-300 border border-[#1E293B] hover:border-slate-600 active:scale-[0.98]',
    ghost:
      'bg-transparent hover:bg-white/5 text-slate-400 hover:text-slate-200 border border-transparent',
    destructive:
      'bg-rose-950/80 hover:bg-rose-900 text-rose-300 border border-rose-800/60 active:scale-[0.98]',
    emerald:
      'bg-emerald-600 hover:bg-emerald-500 text-slate-950 shadow-md shadow-emerald-950/50 border border-emerald-400 active:scale-[0.98]',
  };

  return (
    <button
      type={type}
      disabled={disabled || isLoading}
      onClick={onClick}
      className={`${baseStyles} ${sizeStyles[size] || sizeStyles.md} ${
        variantStyles[variant] || variantStyles.primary
      } ${className}`}
      {...props}
    >
      {isLoading ? (
        <Loader2 className="h-3.5 w-3.5 animate-spin" />
      ) : (
        leftIcon && <span className="shrink-0">{leftIcon}</span>
      )}
      <span>{children}</span>
      {!isLoading && rightIcon && <span className="shrink-0">{rightIcon}</span>}
    </button>
  );
};

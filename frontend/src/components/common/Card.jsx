import React from 'react';

export const Card = ({
  children,
  title,
  subtitle,
  icon: Icon,
  action,
  className = '',
  headerClassName = '',
  bodyClassName = '',
  ...props
}) => {
  return (
    <div
      className={`rounded-xl border border-[#162235] bg-[#0d1524] p-5 shadow-lg relative min-w-0 ${className}`}
      {...props}
    >
      {(title || action || Icon) && (
        <div className={`flex items-center justify-between pb-3 border-b border-[#162235] mb-4 ${headerClassName}`}>
          <div className="flex items-center gap-2.5 min-w-0">
            {Icon && (
              <div className="p-1.5 rounded-lg bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 shrink-0">
                <Icon className="h-4 w-4" />
              </div>
            )}
            <div className="min-w-0">
              {title && <h3 className="font-mono font-bold text-sm text-slate-100 truncate">{title}</h3>}
              {subtitle && <p className="text-[11px] font-mono text-slate-400 truncate mt-0.5">{subtitle}</p>}
            </div>
          </div>
          {action && <div className="shrink-0">{action}</div>}
        </div>
      )}
      <div className={bodyClassName}>{children}</div>
    </div>
  );
};

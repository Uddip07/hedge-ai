import React from 'react';

interface LoadingSpinnerProps {
  message?: string;
}

export const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({ message = 'Executing backend pipeline...' }) => {
  return (
    <div className="flex flex-col items-center justify-center p-8 text-center text-slate-400">
      <div className="h-8 w-8 animate-spin rounded-full border-2 border-cyan-500 border-t-transparent" />
      <p className="mt-3 text-sm font-mono text-slate-300">{message}</p>
    </div>
  );
};

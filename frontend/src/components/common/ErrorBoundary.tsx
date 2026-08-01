import { Component, ErrorInfo, ReactNode } from 'react';
import { AlertTriangle, RefreshCw } from 'lucide-react';

interface Props {
  children: ReactNode;
  fallbackTitle?: string;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null,
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
    console.error('[ErrorBoundary] Uncaught component error:', error, errorInfo);
  }

  private handleReset = (): void => {
    this.setState({ hasError: false, error: null });
  };

  public render(): ReactNode {
    if (this.state.hasError) {
      return (
        <div className="flex flex-col items-center justify-center min-h-[220px] p-6 bg-[#121826] border border-[#1E293B] rounded-lg text-center my-2">
          <div className="p-3 bg-red-950/60 border border-red-800/40 rounded-full text-red-400 mb-3">
            <AlertTriangle className="w-6 h-6" />
          </div>
          <h3 className="text-base font-semibold text-slate-100 mb-1">
            {this.props.fallbackTitle || 'Widget Failed to Render'}
          </h3>
          <p className="text-xs text-slate-400 max-w-md mb-4 font-mono">
            {this.state.error?.message || 'An unexpected error occurred in this module.'}
          </p>
          <button
            onClick={this.handleReset}
            className="inline-flex items-center gap-2 px-3 py-1.5 text-xs font-medium text-slate-200 bg-[#1E293B] hover:bg-slate-800 border border-slate-700 rounded transition-colors"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            Reload Module
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}

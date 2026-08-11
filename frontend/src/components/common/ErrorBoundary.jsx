import React, { Component } from 'react';
import { AlertTriangle, RefreshCw } from 'lucide-react';
import { Button } from './Button';

export class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('[ErrorBoundary caught an error]:', error, errorInfo);
  }

  handleReset = () => {
    this.setState({ hasError: false, error: null });
  };

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      return (
        <div className="rounded-xl border border-rose-800/80 bg-rose-950/40 p-5 font-mono text-xs text-rose-200 space-y-3">
          <div className="flex items-center gap-2 font-bold text-sm text-rose-300">
            <AlertTriangle className="h-5 w-5 text-rose-400" />
            <span>{this.props.fallbackTitle || 'Component Error'}</span>
          </div>
          <p className="text-[11px] text-rose-300/80 leading-relaxed">
            {this.state.error?.message || 'An unexpected rendering error occurred in this module.'}
          </p>
          <Button
            variant="destructive"
            size="xs"
            onClick={this.handleReset}
            leftIcon={<RefreshCw className="h-3.5 w-3.5" />}
          >
            Reset Component
          </Button>
        </div>
      );
    }

    return this.props.children;
  }
}

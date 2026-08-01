import React, { useState } from 'react';
import { Outlet } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { Header } from './Header';
import { CommandPaletteModal } from './CommandPaletteModal';
import { ToastContainer } from '../common/Toast';
import { OfflineBanner } from '../common/OfflineBanner';
import { ErrorBoundary } from '../common/ErrorBoundary';

export const Layout: React.FC = () => {
  const [collapsed, setCollapsed] = useState(false);
  const [isCommandPaletteOpen, setIsCommandPaletteOpen] = useState(false);

  return (
    <div className="min-h-screen bg-[#090D16] text-slate-100 flex overflow-x-hidden max-w-full">
      {/* Offline Banner */}
      <div className="fixed top-0 left-0 right-0 z-50">
        <OfflineBanner />
      </div>

      {/* Sidebar */}
      <Sidebar collapsed={collapsed} onToggle={() => setCollapsed(!collapsed)} />

      {/* Main Adaptive Area */}
      <div
        className={`flex-1 flex flex-col min-w-0 overflow-x-hidden transition-all duration-300 ${
          collapsed ? 'ml-16' : 'ml-64'
        }`}
      >
        <Header onOpenCommandPalette={() => setIsCommandPaletteOpen(true)} />

        <main className="flex-1 p-4 md:p-6 min-w-0 overflow-x-hidden">
          <ErrorBoundary fallbackTitle="Page Load Error">
            <Outlet />
          </ErrorBoundary>
        </main>
      </div>

      {/* Toast Stack */}
      <ToastContainer />

      {/* Command Palette Modal */}
      <CommandPaletteModal
        isOpen={isCommandPaletteOpen}
        onClose={() => setIsCommandPaletteOpen(false)}
      />
    </div>
  );
};

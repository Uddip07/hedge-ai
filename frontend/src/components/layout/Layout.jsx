import React, { useState } from 'react';
import { Outlet } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { Header } from './Header';
import { Toast } from '../common/Toast';
import { OfflineBanner } from '../common/OfflineBanner';
import { CommandPaletteModal } from './CommandPaletteModal';

export const Layout = () => {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [commandPaletteOpen, setCommandPaletteOpen] = useState(false);

  return (
    <div className="min-h-screen bg-[#06080e] text-slate-100 flex flex-col font-sans selection:bg-cyan-500/30 selection:text-cyan-200">
      <OfflineBanner />

      {/* Main App Container */}
      <div className="flex flex-1 relative">
        <Sidebar
          collapsed={sidebarCollapsed}
          onToggle={() => setSidebarCollapsed(!sidebarCollapsed)}
        />

        {/* Content Viewport */}
        <div
          className={`flex-1 flex flex-col transition-all duration-300 min-w-0 ${
            sidebarCollapsed ? 'pl-16' : 'pl-64'
          }`}
        >
          <Header onOpenCommandPalette={() => setCommandPaletteOpen(true)} />

          <main className="flex-1 p-4 md:p-6 w-full max-w-full min-w-0 overflow-x-hidden">
            <Outlet />
          </main>
        </div>
      </div>

      <Toast />
      <CommandPaletteModal
        isOpen={commandPaletteOpen}
        onClose={() => setCommandPaletteOpen(false)}
      />
    </div>
  );
};

import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Layout } from './components/layout/Layout';
import { DashboardPage } from './pages/DashboardPage';
import { LiveMarketPage } from './pages/LiveMarketPage';
import { PortfolioPage } from './pages/PortfolioPage';
import { CompanyAnalysisPage } from './pages/CompanyAnalysisPage';
import { CommitteePage } from './pages/CommitteePage';
import { NewsPage } from './pages/NewsPage';
import { BacktestingPage } from './pages/BacktestingPage';
import { ResearchPage } from './pages/ResearchPage';
import { WatchlistPage } from './pages/WatchlistPage';
import { ApiExplorerPage } from './pages/ApiExplorerPage';
import { SystemHealthPage } from './pages/SystemHealthPage';
import { SettingsPage } from './pages/SettingsPage';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
      staleTime: 3000,
    },
  },
});

export const App = () => {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Layout />}>
            <Route index element={<DashboardPage />} />
            <Route path="markets" element={<LiveMarketPage />} />
            <Route path="portfolio" element={<PortfolioPage />} />
            <Route path="company" element={<CompanyAnalysisPage />} />
            <Route path="company/:symbol" element={<CompanyAnalysisPage />} />
            <Route path="committee" element={<CommitteePage />} />
            <Route path="news" element={<NewsPage />} />
            <Route path="backtesting" element={<BacktestingPage />} />
            <Route path="research" element={<ResearchPage />} />
            <Route path="watchlist" element={<WatchlistPage />} />
            <Route path="api-explorer" element={<ApiExplorerPage />} />
            <Route path="system-health" element={<SystemHealthPage />} />
            <Route path="settings" element={<SettingsPage />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
};

export default App;

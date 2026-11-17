import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Navbar } from './components/layout/Navbar';
import { Sidebar } from './components/layout/Sidebar';
import { Footer } from './components/layout/Footer';
import { Dashboard } from './pages/Dashboard';
import { BuildDetails } from './pages/BuildDetails';
import { UpgradeDetails } from './pages/UpgradeDetails';
import { WorkflowCanvas } from './pages/WorkflowCanvas';
import { MyBuilds } from './pages/MyBuilds';
import { MyUpgrades } from './pages/MyUpgrades';
import { History } from './pages/History';
import { Settings } from './pages/Settings';

export const App: React.FC = () => {
  return (
    <Router>
      <div className="flex flex-col h-screen w-screen bg-canvas-bg overflow-hidden text-slate-100">
        <Navbar />
        <div className="flex flex-1 overflow-hidden">
          <Sidebar />
          <div className="flex-1 flex flex-col overflow-hidden min-w-0">
            <main className="flex-1 flex overflow-hidden">
              <Routes>
                <Route path="/" element={<Dashboard />} />
                <Route path="/build" element={<BuildDetails />} />
                <Route path="/upgrade" element={<UpgradeDetails />} />
                <Route path="/workflow/:id" element={<WorkflowCanvas />} />
                <Route path="/my-builds" element={<MyBuilds />} />
                <Route path="/my-upgrades" element={<MyUpgrades />} />
                <Route path="/history" element={<History />} />
                <Route path="/settings" element={<Settings />} />
                <Route path="*" element={<Dashboard />} />
              </Routes>
            </main>
            <Footer />
          </div>
        </div>
      </div>
    </Router>
  );
};

export default App;

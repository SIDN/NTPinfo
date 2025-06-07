import React, { useState } from 'react';
import Sidebar from './components/Sidebar';
import Hero from './components/Hero';
import HomeTab from './tabs/HomeTab';
import CompareTab from './tabs/CompareTab';
import HistoricalDataTab from './tabs/HistoricalDataTab';
import AboutTab from './tabs/AboutTab';
import { NTPData } from './utils/types';
import './App.css';

function App() {
  const [selectedTab, setSelectedTab] = useState(1);
  const [visualizationData, setVisualizationData] = useState<Map<string, NTPData[]> | null>(null);

  return (
    <div className="app-layout">
      <Sidebar selectedTab={selectedTab} setSelectedTab={setSelectedTab} />
      <main className="app-content">
        {/* <Hero /> */}
        {selectedTab === 1 && <HomeTab onVisualizationDataChange={setVisualizationData} />}
        {selectedTab === 2 && <HistoricalDataTab data={visualizationData} />}
        {selectedTab === 3 && <CompareTab />}
        {selectedTab === 4 && <AboutTab />}
      </main>
    </div>
  );
}

export default App;

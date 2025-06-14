import React, { useState } from 'react';
import Sidebar from './components/Sidebar';
import Hero from './components/Hero';
import HomeTab from './tabs/HomeTab';
import CompareTab from './tabs/CompareTab';
import HistoricalDataTab from './tabs/HistoricalDataTab';
import AboutTab from './tabs/AboutTab';
// import { NTPData } from './utils/types';
import { NTPData, HomeCacheState } from './utils/types';
import './App.css';

function App() {
  const [selectedTab, setSelectedTab] = useState(1);
  const [visualizationData, setVisualizationData] = useState<Map<string, NTPData[]> | null>(null);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  /* ------------------   NEW: cache that outlives HomeTab   ------------------ */
  const initialCache: HomeCacheState = {
    ntpData: null,
    chartData: null,
    measured: false,
    selMeasurement: 'offset',
    measurementId: null,
    vantagePointIp: null,
    allNtpMeasurements: null,
    ripeMeasurementResp: null,          // map
    ripeMeasurementStatus: null,        // map
  };
  const [homeCache, setHomeCache] = useState<HomeCacheState>(initialCache);

  return (
    <div className="app-layout">
      <Sidebar selectedTab={selectedTab} setSelectedTab={setSelectedTab} open={sidebarOpen} setOpen={setSidebarOpen} />
      <main className={`app-content${!sidebarOpen ? ' with-sidebar-collapsed' : ''}`}>
        {/* <Hero /> */}
        {/* {selectedTab === 1 && <HomeTab onVisualizationDataChange={setVisualizationData} />} */}
        {selectedTab === 1 && (
          <HomeTab
            cache={homeCache}
            setCache={setHomeCache}
            onVisualizationDataChange={setVisualizationData}
          />
        )}
        {selectedTab === 2 && <HistoricalDataTab data={visualizationData} />}
        {selectedTab === 3 && <CompareTab />}
        {selectedTab === 4 && <AboutTab />}
      </main>
    </div>
  );
}

export default App

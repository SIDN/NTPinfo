import React, { useState } from 'react';
import Sidebar from './components/Sidebar';
import Hero from './components/Hero';
import HomeTab from './tabs/HomeTab';
import CompareTab from './tabs/CompareTab';
import './App.css';

function App() {
  const [selectedTab, setSelectedTab] = useState(1);

  return (
    <div className="app-layout">
      <Sidebar selectedTab={selectedTab} setSelectedTab={setSelectedTab} />
      <main className="app-content">
        <Hero />
        {selectedTab === 1 && <HomeTab />}
        {selectedTab === 2 && <CompareTab />}
      </main>
    </div>
  );
}

export default App;

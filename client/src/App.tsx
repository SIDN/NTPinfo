import { useState } from 'react'

import './App.css'
import Hero from './components/Hero'
import 'leaflet/dist/leaflet.css'
import HomeTab from './tabs/HomeTab.tsx'
import CompareTab from './tabs/CompareTab.tsx'



function App() {
  
  //TODO
  // for now the switching system is not implemented, will be added later
  const [selectedTab, setSelectedTab] = useState<number>(2)

  //
  //The actual app component
  //
  return (
    <div className="app-container">
      <Hero />

      {(selectedTab == 1 && (<HomeTab />)) || 
       (selectedTab == 2 && (<CompareTab />))}
    </div>
     )
}

export default App

import { useState } from 'react'

import './App.css'
import Hero from './components/Hero'
import VisualizationPopup from './components/Visualization'
function App() {  
  const [popupOpen, setPopupOpen] = useState(false);
  const [selOption1, setOption1] = useState("Last Hour");
  const [selOption2, setOption2] = useState("Hours");

  const dropdown = [
    {
      label: "Time period",
      options: ["Last Hour", "Last Day", "Last Week"],
      selectedValue: selOption1,
      onSelect: setOption1,
      className: "time-dropdown"
    },
    {
      label: "Time Option",
      options: ["Hours", "Days"],
      selectedValue: selOption2,
      onSelect: setOption2,
      className: "custom-time-dropdown"
    }
  ];

  return (
    <div>
      <button className="open-popup-btn" onClick={() => setPopupOpen(true)}>View Historical Data</button>
      <VisualizationPopup 
      isOpen={popupOpen} 
      onClose={() => setPopupOpen(false)}
      dropdowns={dropdown}/>
    </div>
  )
}

export default App

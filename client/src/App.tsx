import { useState } from 'react'

import './App.css'
import Hero from './components/Hero'
import VisualizationPopup from './components/Visualization'
// import DownloadButton from './components/DownloadButton'

// we use this as a dummy data type for the NTP measurements, this will be changed and improved once the API 
// is finished
type NTPData = {
  offset: number;
  delay: number;
  stratum: number;
  jitter: number;
  reachability: number;
  passing: boolean;
}

type InputData = {
  data: NTPData[]
}
function downloadJSON(data : InputData) {
    //parse to json string and make an object with the corresponding data
    var json = JSON.stringify(data)
    var blob = new Blob([json], { type: 'application/json' })
    //create a temporary download link for the data
    var downloadLink = document.createElement('a')
    downloadLink.href = window.URL.createObjectURL(blob)
    downloadLink.download = "data.json"
    downloadLink.click()
    window.URL.revokeObjectURL(downloadLink.href)
    
}

function downloadCSV(data : InputData) {

  var json = JSON.parse(JSON.stringify(data))
  //get headers of csv 
  const headers = Object.keys(json.data[0])
  const values = json.data.map((row : NTPData) => 
    headers.map((key) => JSON.stringify((row as any)[key])).join(','))

  const csvData = [headers.join(','), ...values].join('\n')
  var blob = new Blob([csvData], { type: 'text/csv' })
  //create a temporary download link for the data
  var downloadLink = document.createElement('a')
  downloadLink.href = window.URL.createObjectURL(blob)
  downloadLink.download = "data.csv"
  downloadLink.click()
  window.URL.revokeObjectURL(downloadLink.href)

}


function App() {
  // const [measured, setMeasured] = useState("measure")
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
  //the dummy data will be used for the buttons, uncomment when the buttons actually get added to the page (if needed)
 /* const dummyData : InputData = {
    data : [{
      offset: 0.3,
      delay: 0.3,
      stratum: 1,
      jitter: 1.8,
      reachability: 1,
      passing: true
    }]*/
   return (
    <>
      <Hero />
      {/*These are commented for now, will be added later to avoid conflicts in the current version
      <div className="download-buttons">
       
      <DownloadButton name="Download JSON" onclick={() => downloadJSON(dummyData)} />
      <DownloadButton name="Download CSV" onclick={() => downloadCSV(dummyData)} />
      </div>
      */}
      <div>
        <button className="open-popup-btn" onClick={() => setPopupOpen(true)}>View Historical Data</button>
        <VisualizationPopup 
        isOpen={popupOpen} 
        onClose={() => setPopupOpen(false)}
        dropdowns={dropdown}/>
      </div>
    </>
   )
}

export default App

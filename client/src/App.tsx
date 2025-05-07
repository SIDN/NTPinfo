import { useState } from 'react'

import './App.css'
import Hero from './components/Hero'
import SearchBar from './components/SearchBar'
import ResultSummary from './components/ResultSummary'
//import Graphs from './components/Graphs'
import DownloadButton from './components/DownloadButton'
import VisualizationPopup from './components/Visualization'
import LineChart from './components/LineGraph'
import { ntpMap} from './utils/tempData.ts'

import { NTPData } from './types'

type InputData = {
  data: NTPData[]
}

type Measurement = 'delay' | 'offset';

/**
 * Downloads the measurement data in a JSON format.
 * @param data array of measurements to be downloaded
 */
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
/**
 * Downloads the measurement data in a CSV format.
 * @param data array of measurements to be downloaded
 */
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
  //
  // states we need to define 
  //
  const [ntpData, setNtpData] = useState<NTPData | null>(null)
  const [loaded, setLoaded] = useState(false) //will be deleted when adding API communication
  const [measured, setMeasured] = useState(false) // will be deleted when adding API communication
  const [popupOpen, setPopupOpen] = useState(false)
  const [selOption1, setOption1] = useState("Last Hour")
  const [selOption2, setOption2] = useState("Hours")
  const [selMeasurement, setSelMeasurement] = useState<Measurement>("delay")

  //dropdown format
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
  ]
  //dummy data for chart.js, will be deleted once we properly integrate it
  const chartData = [{offset: 0.3,delay: 0.3,stratum: 1,jitter: 1.8,reachability: 1,status: 'PASSING',time: Date.now()},{offset: 1.2,delay: 13.4,stratum: 2,jitter: 0.5,reachability: 1,status: 'PASSING',time: Date.now() - 40000},
  {offset: 0.8,delay: 4.8,stratum: 2,jitter: 0.6,reachability: 1,status: 'PASSING',time: Date.now() - 20000}]
  
  //
  //functions for handling state changes
  //
  
  const handleSearch = async (query: string) => {
    if (query.length == 0)
      return
    setLoaded(false) 
    setMeasured(true)
    const data = ntpMap.get(query)
    setNtpData(data ?? null)
    await new Promise(resolve => setTimeout(resolve, 2000))
    setLoaded(true)
  }

  const handleMeasurementChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setSelMeasurement(event.target.value as Measurement);
  }
  
  //
  //The actual app component
  //
  return (
    <div className="app-container">
      <Hero />
      <div className="search-wrapper">
        <SearchBar onSearch={handleSearch} />
      </div>
        <div className="result-text">
          {(loaded && measured && (<p>Results</p>)) || (measured && <p>Loading...</p>)}
        </div>
      {(ntpData && loaded && (<div className="results-and-graph">
        <ResultSummary data={ntpData}/>
       
        <div className="graphs">
          <div className='graph-box'>
            <label>
              <input
                type="radio"
                name="measurement"
                value="offset"
                checked={selMeasurement === 'offset'}
                onChange={handleMeasurementChange}
              />
              Jitter
            </label>
            <label>
              <input
                type="radio"
                name="measurement"
                value="delay"
                checked={selMeasurement === 'delay'}
                onChange={handleMeasurementChange}
              />
              Jitter
            </label>
            <LineChart data = {chartData} selectedMeasurement={selMeasurement}/>
          </div>
        </div>
      </div>)) || (!ntpData && loaded && <ResultSummary data={ntpData}/>)}
      {ntpData && loaded && (<div className="download-buttons">
     
        <DownloadButton name="Download JSON" onclick={() => downloadJSON({data : [ntpData]})} />
        <DownloadButton name="Download CSV" onclick={() => downloadCSV({data : [ntpData]})} />
        <div>
          <button className="open-popup-btn" onClick={() => setPopupOpen(true)}>View Historical Data</button>
          <VisualizationPopup
          isOpen={popupOpen}
          onClose={() => setPopupOpen(false)}
          dropdowns={dropdown}
          data = {dummyData.data}/>
        </div>
      </div>)}
    </div>
     )
}

export default App

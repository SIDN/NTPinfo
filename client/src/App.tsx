import { useState } from 'react'

import './App.css'
import Hero from './components/Hero'
import SearchBar from './components/SearchBar'
import ResultSummary from './components/ResultSummary'
import Graphs from './components/Graphs'
import DownloadButton from './components/DownloadButton'
import VisualizationPopup from './components/Visualization'
import LineChart from './components/LineGraph'
// import DownloadButton from './components/DownloadButton'
import { NTPData } from './types'

// we use this as a dummy data type for the NTP measurements, this will be changed and improved once the API
// is finished
//NTPData

type InputData = {
  data: NTPData[]
}

type Measurement = 'delay' | 'offset';

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

  const handleSearch = (query: string) => {
    console.log("Search query:", query)

  }
  const [popupOpen, setPopupOpen] = useState(false);
  const [selOption1, setOption1] = useState("Last Hour");
  const [selOption2, setOption2] = useState("Hours");
  const [selMeasurement, setSelMeasurement] = useState<Measurement>("delay");

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

  const handleMeasurementChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setSelMeasurement(event.target.value as Measurement);
  };
  //the dummy data will be used for the buttons, uncomment when the buttons actually get added to the page (if needed)
  const dummyData : InputData = {
    data : [{
      offset: 0.3,
      delay: 0.3,
      stratum: 1,
      jitter: 1.8,
      reachability: 1,
      passing: true,
      time: Date.now() - 20000
      },
      {
        offset: 1.2,
        delay: 13.4,
        stratum: 2,
        jitter: 0.5,
        reachability: 1,
        passing: true,
        time: Date.now() - 40000
      },
      {
        offset: 0.8,
        delay: 4.8,
        stratum: 2,
        jitter: 0.6,
        reachability: 1,
        passing: true,
        time: Date.now() - 20000
      }
     ]}
  //this will be merged with dummyData, temporary solution
  const chartData = [{offset: 0.3,delay: 0.3,stratum: 1,jitter: 1.8,reachability: 1,passing: true,time: Date.now()},{offset: 1.2,delay: 13.4,stratum: 2,jitter: 0.5,reachability: 1,passing: true,time: Date.now() - 40000},
  {offset: 0.8,delay: 4.8,stratum: 2,jitter: 0.6,reachability: 1,passing: true,time: Date.now() - 20000}];
   return (
    // <>
    //   <Hero />
    //   <div>
    //     <SearchBar onSearch={handleSearch} />
    //   </div>
    //   <ResultSummary />
    // </>

//     <div className="app-container">
// +      <Hero />
// +      <main className="main-content">
// +        <SearchBar onSearch={handleSearch} />
// +        <ResultSummary />
// +      </main>
// +    </div>

    <div className="app-container">
      <Hero />
      <div className="search-wrapper">
        <SearchBar onSearch={handleSearch} />
      </div>
        <div className="result-text">
          <p>Results</p>
        </div>
      <div className="results-and-graph">
        <ResultSummary />
        {/* <Graphs /> */}
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
      </div>
      {/* These are commented for now, will be added later to avoid conflicts in the current version */}

      <div className="download-buttons">

        <DownloadButton name="Download JSON" onclick={() => downloadJSON(dummyData)} />
        <DownloadButton name="Download CSV" onclick={() => downloadCSV(dummyData)} />
        <div>
          <button className="open-popup-btn" onClick={() => setPopupOpen(true)}>View Historical Data</button>
          <VisualizationPopup
          isOpen={popupOpen}
          onClose={() => setPopupOpen(false)}
          dropdowns={dropdown}/>
        </div>
      </div>

      {/* <div>
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
      </div> */}


    </div>
     )
}

export default App

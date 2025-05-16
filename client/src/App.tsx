import { useState } from 'react'

import './App.css'
import Hero from './components/Hero'
import SearchBar from './components/SearchBar'
import ResultSummary from './components/ResultSummary'
import DownloadButton from './components/DownloadButton'
import VisualizationPopup from './components/Visualization'
import LineChart from './components/LineGraph'
import { useFetchIPData } from './hooks/useFetchIPData.ts'
import { useFetchHistoricalIPData } from './hooks/useFetchHistoricalIPData.ts'
import { dateFormatConversion } from './dateFormatConversion.ts'

import { NTPData } from './types'
import { Measurement } from './types'

type InputData = {
  data: NTPData[]
}

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
  const [chartData, setChartData] = useState<NTPData[] | null>(null)
  const [measured, setMeasured] = useState(false)
  const [popupOpen, setPopupOpen] = useState(false)
  const [selOption1, setOption1] = useState("Last Hour")
  const [selOption2, setOption2] = useState("Hours")
  const [selMeasurement, setSelMeasurement] = useState<Measurement>("RTT")

  //Varaibles to log and use API hooks
  const {fetchData: fetchMeasurementData, loading: apiDataLoading, error: apiErrorLoading} = useFetchIPData()
  const {fetchData: fetchHistoricalData, loading: apiHistoricalLoading, error: apiHistoricalError} = useFetchHistoricalIPData()

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
  
  //
  //functions for handling state changes
  //
  
  //main function called when measuring by pressing the button
  const handleSearch = async (query: string) => {
    if (query.length == 0)
      return
    
    const payload = {
      server: query,
      jitter_flag: false,
      measurements_no: 0
    }

    // Get the response from the measurement data API
    const fullurlMeasurementData = `http://localhost:8000/measurements/`
    const apiMeasurementResp = await fetchMeasurementData(fullurlMeasurementData, payload)

    //Get data from past day from historical data API to chart in the graph
    const startDate = dateFormatConversion(Date.now()-86400000)
    const endDate = dateFormatConversion(Date.now())
    const fullurlHistoricalData = `http://localhost:8000/measurements/history/?server=${query}&start=${startDate}&end=${endDate}`
    const apiHistoricalResp = await fetchHistoricalData(fullurlHistoricalData)
    
    //update data stored and show the data again
    setMeasured(true)
    const data = apiMeasurementResp
    const chartData = apiHistoricalResp
    setNtpData(data ?? null)
    setChartData(chartData ?? null)
  }

  //function to determine what value to use on the y axis of the graph
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
          {(!apiDataLoading && measured && (<p>Results</p>)) || (apiDataLoading && <p>Loading...</p>)}
        </div>
      {(ntpData && !apiDataLoading && (<div className="results-and-graph">
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
              Offset
            </label>
            <label>
              <input
                type="radio"
                name="measurement"
                value="RTT"
                checked={selMeasurement === 'RTT'}
                onChange={handleMeasurementChange}
              />
              Round-trip time
            </label>
            <LineChart data = {chartData} selectedMeasurement={selMeasurement}/>
          </div>
        </div>
      </div>)) || (!ntpData && !apiDataLoading && measured && <ResultSummary data={ntpData}/>)}
      {ntpData && !apiDataLoading && (<div className="download-buttons">
     
        <DownloadButton name="Download JSON" onclick={() => downloadJSON({data : [ntpData]})} />
        <DownloadButton name="Download CSV" onclick={() => downloadCSV({data : [ntpData]})} />
        <div>
          <button className="open-popup-btn" onClick={() => setPopupOpen(true)}>View Historical Data</button>
          <VisualizationPopup
          isOpen={popupOpen}
          onClose={() => setPopupOpen(false)}
          dropdowns={dropdown}
          data = {chartData}/>
        </div>
      </div>)}
    </div>
     )
}

export default App

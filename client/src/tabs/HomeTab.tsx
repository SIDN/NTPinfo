import { useState } from 'react'

import '../styles/HomeTab.css'
import InputSection from '../components/InputSection.tsx'
import ResultSummary from '../components/ResultSummary'
import DownloadButton from '../components/DownloadButton'
import VisualizationPopup from '../components/Visualization'
import LineChart from '../components/LineGraph'
import { useFetchIPData } from '../hooks/useFetchIPData.ts'
import { useFetchHistoricalIPData } from '../hooks/useFetchHistoricalIPData.ts'
import { useFetchRIPEData } from '../hooks/useFetchRipeData.ts'
import { dateFormatConversion } from '../utils/dateFormatConversion.ts'
import {downloadJSON, downloadCSV} from '../utils/downloadFormats.ts'
import WorldMap from '../components/WorldMap.tsx'

import { NTPData, RIPEData } from '../utils/types.ts'
import { Measurement } from '../utils/types.ts'
import { LatLngTuple } from 'leaflet'

import 'leaflet/dist/leaflet.css'

function HomeTab() {
  //
  // states we need to define 
  //
  const [ntpData, setNtpData] = useState<NTPData | null>(null)
  const [chartData, setChartData] = useState<NTPData[] | null>(null)
  const [ripeData, setRIPEData] = useState<RIPEData[] | null>(null)
  const [measured, setMeasured] = useState(false)
  const [popupOpen, setPopupOpen] = useState(false)
  const [selOption1, setOption1] = useState("Last Hour")
  const [selOption2, setOption2] = useState("Hours")
  const [selMeasurement, setSelMeasurement] = useState<Measurement>("offset")

  //Varaibles to log and use API hooks
  const {fetchData: fetchMeasurementData, loading: apiDataLoading, error: apiErrorLoading, httpStatus: respStatus} = useFetchIPData()
  const {fetchData: fetchHistoricalData, loading: apiHistoricalLoading, error: apiHistoricalError} = useFetchHistoricalIPData()
  //const {fetchData: fetchRIPEData, loading: apiRIPELoading, error: apiRIPEError} = useFetchRIPEData()


const ripeDatas: RIPEData[] = [
  { measurementData: { offset: 12, RTT: 24, stratum: 2, jitter: 1.5, precision: -20, status: "OK", time: 1717050000, ip: "192.0.2.1", ip_list: ["192.0.2.1", "192.0.2.2"], server_name: "ntp1.example.com", ref_ip: "198.51.100.1", ref_name: "ref1.example.com", root_delay: 0.25 }, probe_id: 101, probe_country: "US", probe_location: [37.7749, -122.4194], got_results: true }, // San Francisco
  { measurementData: { offset: 8, RTT: 15, stratum: 1, jitter: 0.9, precision: -18, status: "OK", time: 1717051000, ip: "192.0.2.3", ip_list: ["192.0.2.3"], server_name: "ntp2.example.com", ref_ip: "198.51.100.2", ref_name: "ref2.example.com", root_delay: 0.18 }, probe_id: 102, probe_country: "US", probe_location: [40.7128, -74.0060], got_results: true }, // New York
  { measurementData: { offset: 5, RTT: 10, stratum: 3, jitter: null, precision: -19, status: "OK", time: 1717052000, ip: "192.0.2.4", ip_list: ["192.0.2.4", "192.0.2.5"], server_name: "ntp3.example.com", ref_ip: "198.51.100.3", ref_name: "ref3.example.com", root_delay: 0.22 }, probe_id: 103, probe_country: "US", probe_location: [41.8781, -87.6298], got_results: true }, // Chicago
  { measurementData: { offset: -1, RTT: -1, stratum: 0, jitter: null, precision: 0, status: "ERROR", time: 1717053000, ip: "0.0.0.0", ip_list: [], server_name: "", ref_ip: "", ref_name: "", root_delay: 0 }, probe_id: 104, probe_country: "US", probe_location: [29.7604, -95.3698], got_results: false }, // Houston
  { measurementData: { offset: 3, RTT: 7, stratum: 2, jitter: 0.7, precision: -21, status: "OK", time: 1717054000, ip: "192.0.2.6", ip_list: ["192.0.2.6"], server_name: "ntp4.example.com", ref_ip: "198.51.100.4", ref_name: "ref4.example.com", root_delay: 0.17 }, probe_id: 105, probe_country: "US", probe_location: [34.0522, -118.2437], got_results: true } // Los Angeles
]
const ntpServer: LatLngTuple = [41.509985, -103.181674];

  //dropdown format
  // second one will removed after custom time intervals are added
  const dropdown = [
    {
      label: "Time period",
      options: ["Last Hour", "Last Day", "Last Week", "Custom"],
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
  const handleSearch = async (query: string, jitter_flag: boolean, measurements_no: number) => {
    if (query.length == 0)
      return
    
    const payload = {
      server: query,
      jitter_flag: jitter_flag,
      measurements_no: jitter_flag ? measurements_no : 0
    }

    const ripePayload = {
      server: query
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

    const fullUrlRipeData = `http://locallocalhost:8000/measurements/ripe`
    //const apiRIPEResp = await fetchRIPEData(fullUrlRipeData, ripePayload)
    //const ripeData = apiRIPEResp
    setRIPEData(ripeData ?? null)
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
      <div className="search-wrapper">
        <InputSection onSearch={handleSearch} />
      </div>
        <div className="result-text">
          {(!apiDataLoading && measured && (<p>Results</p>)) || (apiDataLoading && <p>Loading...</p>)}
        </div>
      {(ntpData && !apiDataLoading && (<div className="results-and-graph">
        <ResultSummary data={ntpData} err={apiErrorLoading} httpStatus={respStatus}/>
       
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
            <LineChart data = {chartData} selectedMeasurement={selMeasurement} selectedOption="Last Day"/>
          </div>
        </div>
        {/* TO ADD WHEN API IS DONE: REPLACE TRUE WITH apiRIPELoading AND err WITH apiRIPEError */}
        {true && (
        <div className='map-box'>
          <WorldMap probes={ripeDatas} ntpServer={ntpServer} err = {null} />
        </div>
        )}
      </div>)) || (!ntpData && !apiDataLoading && measured && <ResultSummary data={ntpData} err={apiErrorLoading} httpStatus={respStatus}/>)}
      
      {/*Only shown when a domain name is queried. Users can download IP addresses corresponding to that domain name*/}
      {ntpData && !apiDataLoading && ntpData.server_name && ntpData.ip_list.length && (() => {

                const downloadContent = `Server name: ${ntpData.server_name}\n\n${ntpData.ip_list.join('\n')}`
                const blob = new Blob([downloadContent], { type: 'text/plain' })
                const downloadUrl = URL.createObjectURL(blob)
               return (<p className="ip-list">You can download more IP addresses corresponding to this domain name  
               <span> <a href={downloadUrl} download="ip-list.txt">here</a></span>
                </p>)
            })()}
      
      {/*Buttons to download results in JSON and CSV format as well as open a popup displaying historical data*/}
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

export default HomeTab
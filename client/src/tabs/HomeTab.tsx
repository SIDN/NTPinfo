import { useState } from 'react'
import '../styles/HomeTab.css'
import InputSection from '../components/InputSection.tsx'
import ResultSummary from '../components/ResultSummary'
import DownloadButton from '../components/DownloadButton'
import VisualizationPopup from '../components/Visualization'
import LoadingSpinner from '../components/LoadingSpinner'
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
import { triggerRipeMeasurement } from '../hooks/triggerRipeMeasurement.ts'

function HomeTab() {
  //
  // states we need to define
  //
  const [ntpData, setNtpData] = useState<NTPData | null>(null)
  const [chartData, setChartData] = useState<Map<string, NTPData[]> | null>(null)
  const [measured, setMeasured] = useState(false)
  const [popupOpen, setPopupOpen] = useState(false)
  const [selOption, setOption] = useState("Last Hour")
  const [selMeasurement, setSelMeasurement] = useState<Measurement>("offset")
  const [measurementId, setMeasurementId] = useState<string | null>(null)

  //Varaibles to log and use API hooks
  const {fetchData: fetchMeasurementData, loading: apiDataLoading, error: apiErrorLoading, httpStatus: respStatus} = useFetchIPData()
  const {fetchData: fetchHistoricalData, loading: apiHistoricalLoading, error: apiHistoricalError} = useFetchHistoricalIPData()
  const {triggerMeasurement, error: triggerRipeError} = triggerRipeMeasurement()
  const {result: ripeMeasurementResp, status: ripeMeasurementStatus} = useFetchRIPEData(measurementId)

  //dropdown format
  const dropdown = {
      options: ["Last Hour", "Last Day", "Last Week", "Custom"],
      selectedValue: selOption,
      onSelect: setOption,
    }
  

  //
  //functions for handling state changes
  //

  /**
   * Function called on the press of the search button.
   * Performs a normal measurement call, a historical measurement call for the graph, and a RIPE measurement call for the map.
   * @param query The input given by the user
   */
  const handleInput = async (query: string) => {
    if (query.length == 0)
      return

    //Reset the hook
    setMeasurementId(null)
    setMeasured(false)
    setNtpData(null)
    setChartData(null)

    /**
     * The payload for the measurement call, containing the server,
     * if the jitter should be calculated and the number of measurements to be done.
     */
    const payload = {
      server: query
    }

    /**
     * Get the response from the measurement data endpoint
     */
    const fullurlMeasurementData = `${import.meta.env.VITE_SERVER_HOST_ADDRESS}/measurements/`
    const apiMeasurementResp = await fetchMeasurementData(fullurlMeasurementData, payload)

    /**
     * Get data from past day from historical data endpoint to chart in the graph.
     */
    const startDate = dateFormatConversion(Date.now()-86400000)
    const endDate = dateFormatConversion(Date.now())
    const fullurlHistoricalData = `${import.meta.env.VITE_SERVER_HOST_ADDRESS}/measurements/history/?server=${query}&start=${startDate}&end=${endDate}`
    const apiHistoricalResp = await fetchHistoricalData(fullurlHistoricalData)

    /**
     * Update the stored data and show it again
     */
    setMeasured(true)
    const data = apiMeasurementResp
    const chartData = new Map<string, NTPData[]>()
    chartData.set(payload.server, apiHistoricalResp)
    setNtpData(data ?? null)
    setChartData(chartData ?? null)

    /**
     * Payload for the RIPE measurement call, containing only the ip of the server to be measured.
     */
    const ripePayload = {
      server: data === null ? query : data.ip,
      random_probes: false
    }

    /**
     * Get the data from the RIPE measurement endpoint and update it.
     */
    const ripeTriggerResp = await triggerMeasurement(ripePayload)
    setMeasurementId(ripeTriggerResp === null ? null : ripeTriggerResp.parsedData.measurementId)
  }

  /**
   * Function to determine what value of Measreuemnt to use on the y axis of the visualization graph
   */
  const handleMeasurementChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setSelMeasurement(event.target.value as Measurement);
  }

  return (
    <div className="app-container">
      <div className="input-wrapper">
        <InputSection onClick={handleInput} loading={apiDataLoading} />
      </div>
      <h3 id="disclaimer">DISCLAIMER: Your IP may be used to get a RIPE probe close to you for the most accurate data.</h3>
        <div className="result-text">
          {(!apiDataLoading && measured && (<p>Results</p>)) || 
                    (apiDataLoading && <div className="loading-div">
                        <p>Loading...</p>
                        <LoadingSpinner size="small"/>
                    </div>  
                        )}
        </div>
        {/* The main page shown after the main measurement is done */}
      {(ntpData && !apiDataLoading && (<div className="results-and-graph">
        <ResultSummary data={ntpData} ripeData={ripeMeasurementResp?ripeMeasurementResp[0]:null} err={apiErrorLoading} httpStatus={respStatus}/>

        {/* Div for the visualization graph, and the radios for setting the what measurement to show */}
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
        {(ripeMeasurementStatus === "complete" || ripeMeasurementStatus === "polling") && (
        <div className='map-box'>
          <WorldMap probes={ripeMeasurementResp} status = {ripeMeasurementStatus} />
        </div>
        )}
      </div>)) || (!ntpData && !apiDataLoading && measured && <ResultSummary data={ntpData} err={apiErrorLoading} httpStatus={respStatus} ripeData={ripeMeasurementResp?ripeMeasurementResp[0]:null}/>)}

      {/*Buttons to download results in JSON and CSV format as well as open a popup displaying historical data*/}
      {ntpData && !apiDataLoading && (<div className="download-buttons">

        <DownloadButton name="Download JSON" onclick={() => downloadJSON({data : [ntpData]})} />
        <DownloadButton name="Download CSV" onclick={() => downloadCSV({data : [ntpData]})} />
        <div>
          <button className="open-popup-btn" onClick={() => setPopupOpen(true)}>View Historical Data</button>
          <VisualizationPopup
          isOpen={popupOpen}
          onClose={() => setPopupOpen(false)}
          dropdown={dropdown}
          data = {chartData}/>
        </div>
      </div>)}
    </div>
     )
}

export default HomeTab
import { useState} from 'react'
import '../styles/CompareTab.css'
import { dateFormatConversion } from '../utils/dateFormatConversion'
import { useFetchHistoricalIPData } from '../hooks/useFetchHistoricalIPData'
import { TimeInput } from '../components/TimeInput'
import LoadingSpinner from '../components/LoadingSpinner'
import { NTPData, Measurement } from '../utils/types'
import LineChart from '../components/LineGraph'
import Hero from '../components/Hero';
function CompareTab() {

    const [servers, setServers] = useState<string[]>(["", ""])
    const [loading, setLoading] = useState(false)
    const [showData, setShowData] = useState(false)
    const [selOption, setSelOption] = useState("Last Day")
    const [selMeasurement, setSelMeasurement] = useState<Measurement>("offset")
    const [data, setData] = useState<Map<string, NTPData[]>>(new Map())
    // “from” & “to” values for custom range
    const [customFrom, setCustomFrom] = useState<string>("")
    const [customTo,   setCustomTo]   = useState<string>("")

    const [errMessage, setErrMessage] = useState<string | null>(null)
    const {fetchData: fetchHistoricalData, loading: apiHistoricalLoading, error: apiHistoricalError} = useFetchHistoricalIPData()

    const handleCompare = async (servers: string[]) => {
        setErrMessage(null)
        
        for (const sv of servers)
            if (sv.trim().length == 0) {
                setErrMessage("Please fill in all servers")
                return
            }
                
        const trimmed = servers.map(s => s.trim())
        const serverSet = [...new Set(trimmed)];
        setLoading(true)
        setShowData(false)
        
        const startDate = dateFormatConversion(Date.now() - 86400000);
        const endDate = dateFormatConversion(Date.now());
        const map = new Map<string, NTPData[]>();
        for (const server of serverSet) {
            const historicalDataUrl = `http://localhost:8000/measurements/history/?server=${server}&start=${startDate}&end=${endDate}`;
            const historicalData = await fetchHistoricalData(historicalDataUrl);
            map.set(server, historicalData);
            console.log(`called ${historicalDataUrl}`);
        }

        setLoading(false)
        setShowData(true)
        setData(map);
    }

    const addServerInput = () => setServers([...servers, ""]);
    const removeServerInput = (index: number) => {
        if (servers.length <= 2) return;
            const updated = [...servers];
            updated.splice(index, 1);
            setServers(updated);
    }
    
    const handleMeasurementChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        setSelMeasurement(event.target.value as Measurement);
    }

    const handleInputChange = (index: number, value: string) => {
        const updated = [...servers];
        updated[index] = value;
        setServers(updated);
    }

    return (
        <div>
            <Hero />
        <div className="compare-tab">
            {/* <Hero /> */}
            <div className="compare-input">
                <p>Enter the domain names or IP adresses of the servers </p>
            <form className="compare-form" onSubmit={(e) => {
                e.preventDefault(); // Prevent page reload
                handleCompare(servers);
            }}>
            {servers.map((server, index) => (
            <div className="label-and-input" key={index}>
                <label htmlFor={`server-${index}`}>Server {index + 1}</label>
                <div className="input-and-btn">
                    <input
                        name={`server-${index}`}
                        type="text"
                        value={server}
                        onChange={(e) => handleInputChange(index, e.target.value)}
                        placeholder={`(ex. time.google.com)`}
                    />
                    {servers.length > 2 && (
                        <button type="button" className="add-rm-btn" onClick={() => removeServerInput(index)}>-</button>
                    )}
                </div>
            </div>
        ))}
        <button className="add-rm-btn" type="button" onClick={addServerInput}>
            + 
        </button>

        <TimeInput
            options={["Last Hour", "Last Day", "Last Week", "Custom"]}
            selectedOption={selOption}
            onSelectionChange={setSelOption}
            customFrom={customFrom}
            customTo={customTo}
            onFromChange={setCustomFrom}
            onToChange={setCustomTo}
        />
            <button type="submit"
                    className='submit-btn'
                    disabled={apiHistoricalLoading}>
                        {loading ? "Comparing..." : "Compare"}
            </button>
            {errMessage && (<p className='error'>{errMessage}</p>)}
           </form>
           </div>
            {(!loading && showData &&
           (<div className='graph-container'>
                        <div className="radio-group">
                        {/*Radio for showing offset data*/}
                        <label className="radio-measurement-label">
                            <input
                                type="radio"
                                name="measurement-popup"
                                value="offset"
                                checked={selMeasurement === "offset"}
                                onChange={handleMeasurementChange}
                            />
                            Offset
                        </label>
                        {/*Radio for showing delay data*/}
                        <label className="radio-measurement-label">
                            <input
                                type="radio"
                                name="measurement-popup"
                                value="RTT"
                                checked={selMeasurement === "RTT"}
                                onChange={handleMeasurementChange}
                            />
                            Round-trip time
                        </label>
                    </div>


                 <div className="chart-wrapper">
                <LineChart data = {data} selectedMeasurement={selMeasurement} selectedOption={selOption}/>
                </div>

            </div>)) ||
            (loading && (<div className="loading-div">
                            <p>Loading...</p>
                            <LoadingSpinner size="large"/>
                        </div>)) ||
            (
                <div className='graph-container'>
                    <div className="placeholder-text-compare">
                    <p className="chart-emoji">📈</p>
                    <p className="text-compare">Compare the accuracy of two NTP servers.</p>
                    <p className="text-compare">Their historical data will be shown here as a graph.</p>
                    </div>

                </div>
            )}



        </div>
        </div>
    )
}

export default CompareTab
import { useState} from 'react'
import '../styles/CompareTab.css'
import { dateFormatConversion } from '../utils/dateFormatConversion'
import { useFetchHistoricalIPData } from '../hooks/useFetchHistoricalIPData'
import { TimeInput } from '../components/TimeInput'
import LoadingSpinner from '../components/LoadingSpinner'
import { NTPData, Measurement } from '../utils/types'
import LineChart from '../components/LineGraph'
import Hero from '../components/Hero';
import scaleUnbalancedIcon from '../assets/scale-unbalanced-svgrepo-com.png'

function CompareTab() {

    const [first, setFirst] = useState<string>('')
    const [second, setSecond] = useState<string>('')
    const [selectedInput, setSelectedInput] = useState<number>(1)
    const [loading, setLoading] = useState(false)
    const [showData, setShowData] = useState(false)
    const [selOption, setSelOption] = useState("Last Day")
    const [selMeasurement, setSelMeasurement] = useState<Measurement>("offset")
    const [data, setData] = useState<Map<string, NTPData[]>>(new Map())
    // "from" & "to" values for custom range
    const [customFrom, setCustomFrom] = useState<string>("")
    const [customTo,   setCustomTo]   = useState<string>("")

    const [errMessage, setErrMessage] = useState<string | null>(null)
    const {fetchData: fetchHistoricalData, loading: apiHistoricalLoading, error: apiHistoricalError} = useFetchHistoricalIPData()

    const handleCompare = async (first: string, second: string) => {

        first = first.trim()
        second = second.trim()
        setErrMessage(null)
        if (first.length == 0 || second.length == 0) {
            setErrMessage("Please fill in both servers")
            return
        }


        if (first === second) {
            setErrMessage("The servers must be different")
            return
        }
        setLoading(true)
        setShowData(false)

        //Get data from past day from historical data API to chart in the graph
        const startDate = dateFormatConversion(Date.now()-86400000)
        const endDate = dateFormatConversion(Date.now())
        const urlHistoricalData1 = `http://localhost:8000/measurements/history/?server=${first}&start=${startDate}&end=${endDate}`
        const apiHistoricalResp1 = await fetchHistoricalData(urlHistoricalData1)

        const urlHistoricalData2 = `http://localhost:8000/measurements/history/?server=${second}&start=${startDate}&end=${endDate}`
        const apiHistoricalResp2 = await fetchHistoricalData(urlHistoricalData2)
        console.log(`called ${urlHistoricalData1}`)
        console.log(`called ${urlHistoricalData2}`)
        //update data stored and show the data again
        const chartData1 = apiHistoricalResp1
        const chartData2 = apiHistoricalResp2
        console.log(chartData1)
        console.log(chartData2)

        const map = new Map<string, NTPData[]>()
        map.set(first, chartData1)
        map.set(second, chartData2)
        setData(map)
        setShowData(true)
        setLoading(false)

    }

    const handleMeasurementChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        setSelMeasurement(event.target.value as Measurement);
    }

    const handleInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
            if (selectedInput == 1)
                setFirst(event.target.value)
            if (selectedInput == 2)
                setSecond(event.target.value)
    };
    return (
        <div>
            <Hero />
        <div className="compare-tab">
            {/* <Hero /> */}
            <div className="compare-input">
                <p>Enter the domain names or IP adresses of the servers </p>
            <form className="compare-form" onSubmit={(e) => {
                e.preventDefault(); // Prevent page reload
                handleCompare(first, second);
            }}>
            <div className="label-and-input">
                <label htmlFor="first">First server</label>
                <input
                    name="first"
                    type="text"
                    value={first}
                    onFocus={() => setSelectedInput(1)}
                    onChange={handleInputChange}
                    placeholder="Server 1 (ex. time.google.com)"
                />
            </div>
            <div className="label-and-input">
                <label htmlFor="second">Second server</label>
                <input
                    name="second"
                    type="text"
                    value={second}
                    onFocus={() => setSelectedInput(2)}
                    onChange={handleInputChange}
                    placeholder="Server 2 (ex. time.google.com)"
                />
            </div>
            <TimeInput
                options={["Last Hour", "Last Day", "Last Week", "Custom"]}
                selectedOption={selOption}
                onSelectionChange={setSelOption}
                customFrom={customFrom}
                customTo={customTo}
                onFromChange={setCustomFrom}
                onToChange={setCustomTo}
            />
            {errMessage && (<p className='error'>{errMessage}</p>)}
            <button type="submit"
                    className='submit-btn'
                    disabled={!first.trim() || !second.trim() || loading}>
                        {loading ? "Comparing..." : "Compare"}
            </button>
           </form>
           </div>
            {(!loading && showData &&
           (<div className='graph-container'>
                <div className="radio-toggle">
                    <input
                        type="radio"
                        id="offset"
                        name="measurement"
                        value="offset"
                        checked={selMeasurement === 'offset'}
                        onChange={handleMeasurementChange}
                    />
                    <label htmlFor="offset">Offset</label>

                    <input
                        type="radio"
                        id="rtt"
                        name="measurement"
                        value="RTT"
                        checked={selMeasurement === 'RTT'}
                        onChange={handleMeasurementChange}
                    />
                    <label htmlFor="rtt">Round-trip time</label>
                </div>


                 <div className="chart-wrapper">
                <LineChart data = {data} selectedMeasurement={selMeasurement} selectedOption={selOption} legendDisplay={true}/>
                </div>

            </div>)) ||
            (loading && (<div className="loading-div">
                            <p>Loading...</p>
                            <LoadingSpinner size="large"/>
                        </div>)) ||
            (
                <div className='graph-container'>
                    <div className="placeholder-text-compare">
                    <img src={scaleUnbalancedIcon} alt="Compare Icon" className="chart-emoji" />
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
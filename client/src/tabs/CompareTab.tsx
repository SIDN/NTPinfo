import { useState} from 'react'
import '../styles/CompareTab.css'
import { dateFormatConversion } from '../utils/dateFormatConversion'
import { useFetchHistoricalIPData } from '../hooks/useFetchHistoricalIPData'
import { TimeInput } from '../components/TimeInput'
function CompareTab() {

    const [first, setFirst] = useState<string>('')
    const [second, setSecond] = useState<string>('')
    const [selectedInput, setSelectedInput] = useState<number>(1)
    const [loading, setLoading] = useState(false)
    const [showData, setShowData] = useState(false)
    const [selOption, setSelOption] = useState("Last Day")

    // “from” & “to” values for custom range
    const [customFrom, setCustomFrom] = useState<string>("")
    const [customTo,   setCustomTo]   = useState<string>("")

    const [errMessage, setErrMessage] = useState<string | null>(null)
    const {fetchData: fetchHistoricalData, loading: apiHistoricalLoading, error: apiHistoricalError} = useFetchHistoricalIPData()

    const handleCompare = async (first: string, second: string) => {

        setErrMessage(null)
        if (first.trim().length == 0 || second.trim().length == 0) {
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


        setShowData(true)
        setLoading(false)
        
    }

     const handleInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
            if (selectedInput == 1)
                setFirst(event.target.value)
            if (selectedInput == 2)
                setSecond(event.target.value)
        };
    return (
        <div className="compare-tab">
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
            
            
        </div>
    )
}

export default CompareTab
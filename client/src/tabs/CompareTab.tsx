import { useState} from 'react'
import '../styles/CompareTab.css'
import { Measurement } from '../utils/types'
import Header from '../components/Header';
import scaleUnbalancedIcon from '../assets/scale-unbalanced-svgrepo-com.png'
import DynamicGraph from '../components/DynamicGraph.tsx';

function CompareTab() {

    const [servers, setServers] = useState<string[]>(["", ""])
    const [showData, setShowData] = useState(false)
    const [selMeasurement, setSelMeasurement] = useState<Measurement>("offset")

    const handleCompare = async (servers: string[]) => {
        for (const sv of servers)
            if (sv.trim().length == 0) {
                return
            }

        setShowData(true)
    }

    const addServerInput = () => setServers([...servers, ""]);
    const removeServerInput = (index: number) => {
        if (servers.length <= 2) return;
            const updated = [...servers];
            updated.splice(index, 1);
            setServers(updated);
    }

    const handleInputChange = (index: number, value: string) => {
        const updated = [...servers];
        updated[index] = value;
        setServers(updated);
    }

    return (
        <div>
            <Header />
        <div className="compare-tab">
            <div className="compare-input">
                <p>Enter the names or IPs of the NTP servers you want to compare.</p>
                <p>This only compares historical data. No new measurements are done.</p>
                <p>Click the "+" button to add more.</p>
            <form className="compare-form" onSubmit={(e) => {
                e.preventDefault(); // Prevent page reload
                handleCompare(servers);
            }}>
            <div className="server-inputs">
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
                        <button type="button" className="add-rm-btn rm" onClick={() => removeServerInput(index)}>-</button>
                    )}
                </div>
            </div>
            ))}
            </div>

        <button className="add-rm-btn add" type="button" onClick={addServerInput}>+</button>

            <button type="submit"
                    className='submit-btn'
                    disabled={servers.some(s => s.trim() === "")}>
                        Compare
            </button>
           </form>
           </div>
            {(!showData &&
            (
                <div className='graph-container'>
                    <div className="placeholder-text-compare">
                    <img src={scaleUnbalancedIcon} alt="Compare Icon" className="chart-emoji" />
                    <p className="text-compare">Compare the accuracy of two NTP servers.</p>
                    <p className="text-compare">Their historical data will be shown here as a graph.</p>
                    </div>
                </div>
            )) ||
            (showData && (
                <div className='graph-container'>
                    <DynamicGraph
                        servers={servers.filter(s => s.trim())}
                        selectedMeasurement={selMeasurement}
                        onMeasurementChange={setSelMeasurement}
                        legendDisplay={true}
                        showTimeInput={true}
                    />
                </div>
            ))
            }
        </div>
        </div>
    )
}

export default CompareTab
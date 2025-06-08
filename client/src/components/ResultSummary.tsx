
import '../styles/ResultSummary.css'
import { NTPData } from '../utils/types.ts'
import { calculateStatus } from '../utils/calculateStatus.ts'
import { useState, useEffect } from 'react'
function ResultSummary({data, err, httpStatus} : {data : NTPData | null, err : Error | null, httpStatus: number}) {

    const [statusMessage, setStatusMessage] = useState<string>("")
    useEffect(() => {
    if (data == null) {
        if (httpStatus === 429)
            setStatusMessage("Too many requests in a short amount of time")
        else if (httpStatus === 404)
            setStatusMessage("Domain name or IP address not found")
        else if (err)
            setStatusMessage("Unknown error occurred")
        }
    }, [data, httpStatus, err])

    if (data == null)
        return <h2 id="not-found">{err ? `Error ${httpStatus}: ${statusMessage}` : `Unknown error occurred`}</h2>


    const status = calculateStatus(data)
    return (
        <>
            <div className="results-section">
                <div className="result-box" id="main-details">
                    <div className="metric"><span title='The difference between the time reported by the like an NTP server and your local clock'>Offset</span><span>{data.offset ? `${(data.offset*1000).toFixed(3)} ms` : 'N/A'}</span></div>
                    <div className="metric"><span title='The total time taken for a request to travel from the client to the server and back.'>Round-trip time</span><span>{data.RTT ? `${(data.RTT*1000).toFixed(3)} ms` : 'N/A'}</span></div>
                    <div className="metric"><span title='The variability in delay times between successive NTP messages, calculated as std. dev. of offsets'>Jitter</span><span>{data.jitter ? `${(data.jitter*1000).toFixed(3)} ms` : 'N/A'}</span></div>
                    <div className="metric"><span title='The smallest time unit that the NTP server can measure or represent'>Precision</span><span>2<sup>{data.precision}</sup></span></div>
                    <div className="metric"><span title='A hierarchical level number indicating the distance from the reference clock'>Stratum</span><span>{data.stratum}</span></div>

                    <div className="status-line">
                        <span className="status-label">STATUS:&nbsp;</span>
                        <span className={`status-value ${status.toLowerCase()}`}>{status}</span>
                    </div>
                </div>
                <div className="result-box" id="extra-details">
                    <div className="metric"><span>IP address</span><span>{data.ip}</span></div>
                    <div className="metric"><span>Server name</span><span>{data.server_name ?? "Unknown"}</span></div>
                    <div className="metric"><span>Reference ID</span><span>{data.ref_ip ?? (data.ref_name ?? "Unknown")}</span></div>
                    <div className="metric"><span>Root Delay</span><span>{data.root_delay}</span></div>
                </div>
            </div>



        </>

    )
}

export default ResultSummary
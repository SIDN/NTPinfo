
import '../styles/ResultSummary.css'
import { NTPData, RIPEData } from '../utils/types.ts'
import { calculateStatus } from '../utils/calculateStatus.ts'
import { useState, useEffect } from 'react'
function ResultSummary({data, ripeData, err, httpStatus} : {data : NTPData | null, ripeData: RIPEData | null, err : Error | null, httpStatus: number}) {

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


    const status = data ? calculateStatus(data) : null
    return (
        <>
            <div className="results-section">
                <div className="result-and-title">
                    <div className="res-label">From Our NTP Client (Netherlands)
                        <div className="tooltip-container">
                        <span className="tooltip-icon">?</span>
                        <div className="tooltip-text">
                           Our NTP Client is based in the Netherlands
                        </div>
                        </div>
                    </div>
                    <div className="result-box" id="main-details">
                        <div className="metric"><span title='The difference between the time reported by the like an NTP server and your local clock'>Offset</span><span>{data?.offset ? `${(data.offset*1000).toFixed(3)} ms` : 'N/A'}</span></div>
                        <div className="metric"><span title='The total time taken for a request to travel from the client to the server and back.'>Round-trip time</span><span>{data?.RTT ? `${(data.RTT*1000).toFixed(3)} ms` : 'N/A'}</span></div>
                        <div className="metric"><span title='The variability in delay times between successive NTP messages, calculated as std. dev. of offsets'>Jitter</span><span>{data?.jitter ? `${(data.jitter*1000).toFixed(3)} ms` : 'N/A'}</span></div>
                        <div className="metric"><span title='The smallest time unit that the NTP server can measure or represent'>Precision</span><span>2<sup>{data?.precision}</sup></span></div>
                        <div className="metric"><span title='A hierarchical level number indicating the distance from the reference clock'>Stratum</span><span>{data?.stratum}</span></div>
                        <div className="metric"><span>IP address</span><span>{data?.ip}</span></div>
                        <div className="metric"><span>Vantage point IP</span><span>{data?.vantage_point_ip}</span></div>
                        <div className="status-line">
                            <span className="status-label">STATUS:&nbsp;</span>
                            <span className={`status-value ${status?.toLowerCase()}`}>{status}</span>
                        </div>
                    </div>
                </div>
                <div className="result-and-title">
                    <div className="res-label">From the RIPE Atlas probe (Close to you)
                        <div className="tooltip-container">
    <span className="tooltip-icon">?</span>
    <div className="tooltip-text">
       RIPE Atlas tries to choose a probe near the user to perform more accurate measurements.
    </div>
  </div>
                    </div>
                    <div className="result-box" id="ripe-details">
                        <div className="metric"><span title='The difference between the time reported by the like an NTP server and your local clock'>Offset</span><span>{ripeData?.measurementData.offset ? `${(ripeData.measurementData.offset*1000).toFixed(3)} ms` : 'N/A'}</span></div>
                        <div className="metric"><span title='The total time taken for a request to travel from the client to the server and back.'>Round-trip time</span><span>{ripeData?.measurementData.RTT ? `${(ripeData.measurementData.RTT*1000).toFixed(3)} ms` : 'N/A'}</span></div>
                        <div className="metric"><span title='The variability in delay times between successive NTP messages, calculated as std. dev. of offsets'>Jitter</span><span>{ripeData?.measurementData.jitter ? `${(ripeData.measurementData.jitter*1000).toFixed(3)} ms` : 'N/A'}</span></div>
                        <div className="metric"><span title='The smallest time unit that the NTP server can measure or represent'>Precision</span><span>2<sup>{ripeData?.measurementData.precision}</sup></span></div>
                        <div className="metric"><span title='A hierarchical level number indicating the distance from the reference clock'>Stratum</span><span>{ripeData?.measurementData.stratum}</span></div>
                        <div className="metric"><span>IP address</span><span>{ripeData?.measurementData.ip}</span></div>
                        <div className="metric"><span>Vantage point IP</span><span>{ripeData?.measurementData.vantage_point_ip}</span></div>
                        <div className="metric"><span>Measurement ID</span><span>{ripeData?.measurement_id}</span></div>
                    </div>
                </div>

            </div>



        </>

    )
}

export default ResultSummary;

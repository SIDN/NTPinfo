import '../styles/ResultSummary.css'
import { NTPData, RIPEData } from '../utils/types.ts'
import { calculateStatus } from '../utils/calculateStatus.ts'
import { useState, useEffect } from 'react'
import triangleGreen from '../assets/triangle-green-svgrepo-com.png'
import triangleRed from '../assets/triangle-red-svgrepo-com.png'
import linkIcon from '../assets/link-svgrepo-com.png'

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

    // Helper to determine which icon to show for a metric
    function getMetricIcons(ntpValue: number | undefined, ripeValue: number | undefined, lowerIsBetter = true) {
        if (ntpValue === undefined || ripeValue === undefined) return [null, null];
        if (ntpValue === ripeValue) return [triangleGreen, triangleGreen];
        if (lowerIsBetter) {
            return ntpValue < ripeValue ? [triangleGreen, triangleRed] : [triangleRed, triangleGreen];
        } else {
            return ntpValue > ripeValue ? [triangleGreen, triangleRed] : [triangleRed, triangleGreen];
        }
    }

    // Prepare values for comparison (in ms)
    const ntpOffset = data?.offset !== undefined ? data.offset * 1000 : undefined;
    const ripeOffset = ripeData?.measurementData.offset !== undefined ? ripeData.measurementData.offset * 1000 : undefined;
    const ntpRTT = data?.RTT !== undefined ? data.RTT * 1000 : undefined;
    const ripeRTT = ripeData?.measurementData.RTT !== undefined ? ripeData.measurementData.RTT * 1000 : undefined;

    // For offset, compare absolute values
    const [offsetIconNTP, offsetIconRIPE] = getMetricIcons(
        ntpOffset !== undefined ? Math.abs(ntpOffset) : undefined,
        ripeOffset !== undefined ? Math.abs(ripeOffset) : undefined,
        true
    );
    const [rttIconNTP, rttIconRIPE] = getMetricIcons(ntpRTT, ripeRTT, true);

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
                        <div className="metric"><span title='The difference between the time reported by the like an NTP server and your local clock'>Offset</span><span>{data?.offset ? `${(data.offset*1000).toFixed(3)} ms` : 'N/A'} {offsetIconNTP && <img src={offsetIconNTP} alt="offset performance" style={{width:'14px',verticalAlign:'middle'}}/>}</span></div>
                        <div className="metric"><span title='The total time taken for a request to travel from the client to the server and back.'>Round-trip time</span><span>{data?.RTT ? `${(data.RTT*1000).toFixed(3)} ms` : 'N/A'} {rttIconNTP && <img src={rttIconNTP} alt="rtt performance" style={{width:'14px',verticalAlign:'middle'}}/>}</span></div>
                        <div className="metric"><span title='The variability in delay times between successive NTP messages, calculated as std. dev. of offsets'>Jitter</span><span>{data?.jitter ? `${(data.jitter*1000).toFixed(3)} ms` : 'N/A'}</span></div>
                        <div className="metric"><span title='The smallest time unit that the NTP server can measure or represent'>Precision</span><span>2<sup>{data?.precision}</sup></span></div>
                        <div className="metric"><span title='A hierarchical level number indicating the distance from the reference clock'>Stratum</span><span>{data?.stratum}</span></div>
                        <div className="metric"><span title='The IP address of the NTP server'>IP address</span><span>{data?.ip}</span></div>
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
                        <div className="metric"><span title='The difference between the time reported by the like an NTP server and your local clock'>Offset</span><span>{ripeData?.measurementData.offset ? `${(ripeData.measurementData.offset*1000).toFixed(3)} ms` : 'N/A'} {offsetIconRIPE && <img src={offsetIconRIPE} alt="offset performance" style={{width:'14px',verticalAlign:'middle'}}/>}</span></div>
                        <div className="metric"><span title='The total time taken for a request to travel from the client to the server and back.'>Round-trip time</span><span>{ripeData?.measurementData.RTT ? `${(ripeData.measurementData.RTT*1000).toFixed(3)} ms` : 'N/A'} {rttIconRIPE && <img src={rttIconRIPE} alt="rtt performance" style={{width:'14px',verticalAlign:'middle'}}/>}</span></div>
                        <div className="metric"><span title='The variability in delay times between successive NTP messages, calculated as std. dev. of offsets'>Jitter</span><span>{ripeData?.measurementData.jitter ? `${(ripeData.measurementData.jitter*1000).toFixed(3)} ms` : 'N/A'}</span></div>
                        <div className="metric"><span title='The smallest time unit that the NTP server can measure or represent'>Precision</span><span>{ripeData?.measurementData.precision}</span></div>
                        <div className="metric"><span title='A hierarchical level number indicating the distance from the reference clock'>Stratum</span><span>{ripeData?.measurementData.stratum}</span></div>
                        <div className="metric"><span title='The IP address of the NTP server'>IP address</span><span>{ripeData?.measurementData.ip}</span></div>
                        <div className="metric"><span>Vantage point IP</span><span>{ripeData?.measurementData.vantage_point_ip}</span></div>
                        <div className="metric"><span>Measurement ID</span><span>
                            {ripeData?.measurement_id ? (
                                <a
                                    href={`https://atlas.ripe.net/measurements/${ripeData.measurement_id}/`}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="measurement-link"
                                >
                                    {ripeData.measurement_id}
                                    <img src={linkIcon} alt="external link" style={{width:'14px',verticalAlign:'middle',marginLeft:'4px'}} />
                                </a>
                            ) : 'N/A'}
                        </span></div>
                    </div>
                </div>

            </div>



        </>

    )
}

export default ResultSummary;

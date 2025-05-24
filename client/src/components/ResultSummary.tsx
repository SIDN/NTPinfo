
import '../styles/ResultSummary.css'
import { NTPData } from '../utils/types.ts'
import { calculateStatus } from '../utils/calculateStatus.ts'
function ResultSummary({data} : {data : NTPData | null}) {
    if (data == null)
        return <h2 id="not-found">Your search does not seem to match any server</h2>
    const status = calculateStatus(data)
    return (
        <>
            <div className="result-box">
                <div className="metric"><span>Offset</span><span>{data.offset !== null ? `${(data.offset*1000).toFixed(10)} ms` : 'N/A'}</span></div>
                <div className="metric"><span>Round-trip time</span><span>{data.RTT !== null ? `${(data.RTT*1000).toFixed(10)} ms` : 'N/A'}</span></div>
                <div className="metric"><span>Jitter</span><span>{data.jitter !== null ? `${(data.jitter*1000).toFixed(10)} ms` : 'N/A'}</span></div>
                <div className="metric"><span>Precision</span><span>2<sup>{data.precision}</sup></span></div>
                <div className="metric"><span>Stratum</span><span>{data.stratum}</span></div>
                <div className="metric"><span>IP address</span><span>{data.ip}</span></div>
                <div className="status-line">
                    <span className="status-label">STATUS:&nbsp;</span>
                    <span className={`status-value ${status.toLowerCase()}`}>{status}</span>
                </div>
            </div>
            
                
        </>

    )
}

export default ResultSummary;

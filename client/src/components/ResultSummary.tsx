
import '../styles/ResultSummary.css'
import { NTPData } from '../utils/types.ts'
import { calculateStatus } from '../utils/calculateStatus.ts'
function ResultSummary({data} : {data : NTPData | null}) {
    if (data == null)
        return <h2 id="not-found">Your search does not seem to match any server</h2>
    const status = calculateStatus(data)
    return (
        <>
            <div className="results-section">
                <div className="result-box" id="main-details">
                    <div className="metric"><span>Offset</span><span>{data.offset ? `${(data.offset*1000).toFixed(10)} ms` : 'N/A'}</span></div>
                    <div className="metric"><span>Round-trip time</span><span>{data.RTT ? `${(data.RTT*1000).toFixed(10)} ms` : 'N/A'}</span></div>
                    <div className="metric"><span>Jitter</span><span>{data.jitter ? `${(data.jitter*1000).toFixed(10)} ms` : 'N/A'}</span></div>
                    <div className="metric"><span>Precision</span><span>2<sup>{data.precision}</sup></span></div>
                    <div className="metric"><span>Stratum</span><span>{data.stratum}</span></div>
                    
                    <div className="status-line">
                        <span className="status-label">STATUS:&nbsp;</span>
                        <span className={`status-value ${status.toLowerCase()}`}>{status}</span>
                    </div>
                </div>
                <div className="result-box" id="extra-details">
                    <div className="metric"><span>IP address</span><span>{data.ip}</span></div>
                    <div className="metric"><span>Server name</span><span>{data.server_name ?? "Unknown"}</span></div>
                    <div className="metric"><span>Reference IP</span><span>{data.ref_ip ?? "Unknown"}</span></div>
                    <div className="metric"><span>Reference Name</span><span>{"Unknown"}</span></div>
                    <div className="metric"><span>Root Delay</span><span>{data.root_delay}</span></div>
                </div>
            </div>
            
            
                
        </>

    )
}

export default ResultSummary;

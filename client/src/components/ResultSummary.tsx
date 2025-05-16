
import '../styles/ResultSummary.css'
import { NTPData } from '../types'

function ResultSummary({data} : {data : NTPData | null}) {
    if (data == null)
        return <h2 id="not-found">Your search does not seem to match any server</h2>

    return (
        <>
            <div className="result-box">
                <div className="metric"><span>Offset</span><span>{data.offset} s</span></div>
                <div className="metric"><span>Round-trip time</span><span>{data.RTT} s</span></div>
                <div className="metric">
                <span>Jitter</span>
                <span>{data.jitter !== null ? `${data.jitter} s` : 'N/A'}</span>
                </div>
                <div className="metric"><span>Precision</span><span>2<sup>{data.precision}</sup></span></div>
                <div className="metric"><span>Stratum</span><span>{data.stratum}</span></div>
                <div className="status-line">
                    <span className="status-label">STATUS:&nbsp;</span>
                    <span className={`status-value ${data.status.toLowerCase()}`}>{data.status}</span>
                </div>
            </div>
        </>

    )
}

export default ResultSummary;

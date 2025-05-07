import { useState, useEffect } from 'react';
import '../styles/ResultSummary.css'

function ResultSummary() {
    const [data, setData] = useState({
        offset: -2.3,
        delay: 12,
        jitter: 1.8,
        stratum: 1,
        reachability: 100,
        status: 'PASSING'
    });
    return (
        <>
            <div className="result-box">
                <div className="metric"><span>Offset</span><span>{data.offset} ms</span></div>
                <div className="metric"><span>Delay</span><span>{data.delay} ms</span></div>
                <div className="metric"><span>Jitter</span><span>{data.jitter} ms</span></div>
                <div className="metric"><span>Stratum</span><span>{data.stratum}</span></div>
                <div className="metric"><span>Reachability</span><span>{data.reachability}%</span></div>
                <div className="status-line">
                    <span className="status-label">STATUS:&nbsp;</span>
                    <span className={`status-value ${data.status.toLowerCase()}`}>{data.status}</span>
                </div>
            </div>
        </>

    )
}

export default ResultSummary;

import '../styles/ResultSummary.css'
import { NTPData, RIPEData, RipeStatus } from '../utils/types.ts'
import { useState, useEffect } from 'react'
import triangleGreen from '../assets/triangle-green-svgrepo-com.png'
import triangleRed from '../assets/triangle-red-svgrepo-com.png'
import linkIcon from '../assets/link-svgrepo-com.png'
import LoadingSpinner from './LoadingSpinner.tsx'
import { calculateStatus } from '../utils/calculateStatus.ts'

function ResultSummary({
    data,
    ripeData,
    err,
    httpStatus,
    ripeErr,
    ripeStatus,
    errMessage
}: {
    data: NTPData | null,
    ripeData: RIPEData | null,
    err: Error | null,
    httpStatus: number,
    ripeErr: Error | null,
    ripeStatus: RipeStatus | null,
    errMessage: string | null
}) {
    const [serverStatus, setServerStatus] = useState<string | null>(null)
    const [statusMessage, setStatusMessage] = useState<string | null>("")

    useEffect(() => {
        if (data == null) {
            setStatusMessage(errMessage)
        }
    }, [data, errMessage])

    useEffect(() => {
        if ((ripeStatus === "complete") && ripeData && data) {
            setServerStatus(calculateStatus(data, ripeData))
        } else if (ripeErr) {
            setServerStatus(null)
        } else {
            setServerStatus(null)
        }
    }, [data, ripeData, ripeErr, ripeStatus])

    if (data == null)
        return <h2 id="not-found">{err && errMessage ? `Error ${httpStatus}: ${statusMessage}` : `Unknown error occurred`}</h2>

    function getMetricIcons(ntpValue: number | undefined, ripeValue: number | undefined, lowerIsBetter = true) {
        if (ntpValue === undefined || ripeValue === undefined) return [null, null]
        if (ntpValue === ripeValue) return [triangleGreen, triangleGreen]
        if (lowerIsBetter) {
            return ntpValue < ripeValue ? [triangleGreen, triangleRed] : [triangleRed, triangleGreen]
        } else {
            return ntpValue > ripeValue ? [triangleGreen, triangleRed] : [triangleRed, triangleGreen]
        }
    }

    const ntpOffset = data?.offset
    const ripeOffset = ripeData?.measurementData.offset
    const ntpRTT = data?.RTT
    const ripeRTT = ripeData?.measurementData.RTT

    const isRipeMeasurementFailed = ripeRTT === -1000

    const [offsetIconNTP, offsetIconRIPE] = getMetricIcons(
        ntpOffset !== undefined ? Math.abs(ntpOffset) : undefined,
        ripeOffset !== undefined ? Math.abs(ripeOffset) : undefined,
        true
    )
    const [rttIconNTP, rttIconRIPE] = getMetricIcons(ntpRTT, ripeRTT, true)

    const ntpPrecision = data?.precision
    const ripePrecision = ripeData?.measurementData.precision
    const [precisionIconNTP, precisionIconRIPE] = getMetricIcons(ntpPrecision, ripePrecision, true)

    const ntpRootDispersion = data?.root_dispersion
    const ripeRootDispersion = ripeData?.measurementData.root_dispersion
    const [rootDispIconNTP, rootDispIconRIPE] = getMetricIcons(ntpRootDispersion, ripeRootDispersion, true)

    return (
        <>
            <div className="results-section">
                <div className="status-line">
                    <span className="status-label">STATUS:&nbsp;</span>
                    <span className={`status-value ${serverStatus?.toLowerCase()}`}>{serverStatus}</span>
                    {ripeStatus === "complete" && (
                        <div className="tooltip-container">
                            <span className="tooltip-icon">?</span>
                            {serverStatus === "PASSING" && (
                                <div className="tooltip-text">
                                    The status of the NTP server, calculated with the offset
                                    of our measurement and the offset of the RIPE Probe.<br />
                                    Both offsets are less than {import.meta.env.VITE_STATUS_THRESHOLD} ms.
                                </div>
                            )}
                            {serverStatus === "CAUTION" && (
                                <div className="tooltip-text">
                                    The status of the NTP server, calculated with the offset
                                    of our measurement and the offset of the RIPE Probe.<br />
                                    One of the offsets is more than {import.meta.env.VITE_STATUS_THRESHOLD} ms.
                                </div>
                            )}
                            {serverStatus === "FAILING" && (
                                <div className="tooltip-text">
                                    The status of the NTP server, calculated with the offset
                                    of our measurement and the offset of the RIPE Probe.<br />
                                    Both offsets are more than {import.meta.env.VITE_STATUS_THRESHOLD} ms.
                                </div>
                            )}
                            {serverStatus === null && (
                                <div className="tooltip-text">
                                    The status of the NTP server, calculated with the offset
                                    of our measurement and the offset of the RIPE Probe.<br />
                                    There was an error in one of the measurements.
                                </div>
                            )}
                        </div>
                    )}
                </div>

                <div className="result-boxes-container">
                    <div className="result-and-title">
                        <div className="res-label">
                            Results from our server, synced with <a href="https://time.nl" target="_blank" rel="noopener noreferrer">TIME.nl</a> (Stratum 1 synced server), in the Netherlands:
                            <div className="tooltip-container">
                                <span className="tooltip-icon">?</span>
                                <div className="tooltip-text">
                                    Our backend synchronizes using <a href="https://en.wikipedia.org/wiki/Precision_Time_Protocol" target="_blank" rel="noopener noreferrer">PTP</a> to a Stratum 1 NTP server (<a href="https://www.meinbergglobal.com/" target="_blank" rel="noopener noreferrer">Meinberg</a>), which synchronizes its clock with GPS, Galileo, and <a href="https://en.wikipedia.org/wiki/DCF77" target="_blank" rel="noopener noreferrer">DCF77</a> signals. Service is provided by <a href="https://time.nl" target="_blank" rel="noopener noreferrer">TIME.nl</a>
                                </div>
                            </div>
                        </div>
                        <div className="result-box" id="main-details">
                            {/* Metrics from NTP Server */}
                            {/* OMITTED FOR BREVITY - these are unchanged and render fine */}
                            {/* Include all your "metric" divs here as before */}
                        </div>
                    </div>

                    <div className="result-and-title" id="ripe-result">
                        Results from <a href="https://atlas.ripe.net" target="_blank" rel="noopener noreferrer">RIPE Atlas</a> probes close to your location:
                        <div className="tooltip-container">
                            {(ripeStatus === "timeout" || ripeStatus === "error" || ripeData?.measurementData.RTT === -1000.000) ? (
                                <span className="tooltip-icon fail">!</span>
                            ) : (
                                <span className="tooltip-icon success">?</span>
                            )}
                            <div className="tooltip-text">
                                {ripeStatus === "timeout" && <span>RIPE Measurement timed out.<br /></span>}
                                {ripeStatus === "error" && <span>RIPE Measurement failed.<br /></span>}
                                {ripeData?.measurementData.RTT === -1000.000 && <span>Probe failed to respond.<br /></span>}
                                RIPE Atlas tries to choose a probe near the user to perform more accurate measurements. This can take longer.
                            </div>
                        </div>
                    </div>

                    {/* RIPE Measurement Results Block */}
                    {ripeStatus === "complete" || ripeStatus === "timeout" ? (
                        <div className="result-box" id="ripe-details">
                            {/* Metrics from RIPE */}
                            {/* OMITTED FOR BREVITY - copy from original */}
                        </div>
                    ) : ripeStatus === "pending" || ripeStatus === "partial_results" ? (
                        <div className="loading-container">
                            <p className="ripe-loading-text">Running RIPE measurements. This may take a while.</p>
                            <LoadingSpinner size="medium" />
                        </div>
                    ) : ripeStatus === "error" ? (
                        <p className="ripe-err">RIPE measurement failed</p>
                    ) : null}
                </div>
            </div>
        </>
    )
}

export default ResultSummary

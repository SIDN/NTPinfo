import {useEffect, useState, useRef} from "react"
import axios from "axios"
import { RIPEData, RipeStatus } from "../utils/types"
import { transformJSONDataToRIPEData } from "../utils/transformJSONDataToRIPEData"

/**
 * The endpoint to poll RIPE measurements from the backend
 * When a new measurement is started, it resets the state of the measurement to not show old data
 * It then performs a GET request every interval and updates the data that was fetched
 * When the status becomes "complete", "timeout" or "error", the call ends
 * If a new measurement is started, the old one gets cancelled and the new one begins
 * Due to the polling possibly starting before RIPE begins, in case a 405 HTTP error is reived, the polling will be retried after a few seconds
 * @param measurementId the ID of the RIPE measurement to be polled
 * @param intervalMs the interval at which data will be polled from the endpoint
 * @returns the current set of results, the status of the polling, and if an error has occured
 */
export const useFetchRIPEData = (measurementId: string | null, intervalMs = 3000) => {
    const [result, setResult] = useState<RIPEData[] | null>(null)
    const [status, setStatus] = useState<RipeStatus>("pending")
    const [error, setError] = useState<Error | null>(null)

    // @ts-ignore
    const intervalRef = useRef<NodeJS.Timeout | null>(null)
    // @ts-ignore
    const retryTimeoutRef = useRef<NodeJS.Timeout | null>(null)

    useEffect(() => {
        
        if (intervalRef.current) {
            clearInterval(intervalRef.current)
            intervalRef.current = null
        }
        if (retryTimeoutRef.current) {
            clearTimeout(retryTimeoutRef.current)
            retryTimeoutRef.current = null
        }

        if (!measurementId) {
            setResult(null)
            setStatus("pending")
            setError(null)
            return
        }

        setStatus("partial_results")
        setError(null)

        const controller = new AbortController()

        const fetchResult = async () => {
            try {
                const res = await axios.get(
                    `${import.meta.env.VITE_SERVER_HOST_ADDRESS}/measurements/ripe/${measurementId}`,
                    { signal: controller.signal }
                )
                if (res.data?.results) {
                    const transformedData = res.data.results.map((d: any) => transformJSONDataToRIPEData(d))
                    setResult(transformedData)
                }
                if (res.data.status === "complete" || res.data.status === "timeout") {
                    setStatus("complete")
                    if (intervalRef.current) clearInterval(intervalRef.current)
                } else if (res.data.status === "pending") {
                    setStatus("pending")
                } else if (res.data.status === "error") {
                    setError(new Error(res.data.message || "Unknown error"))
                    setStatus("error")
                    if (intervalRef.current) clearInterval(intervalRef.current)
                }
            } catch (err: any) {
                if (axios.isAxiosError(err) && err.response?.status === 405){
                    console.warn("Received 405, retrying in 2 seconds...")
                    retryTimeoutRef.current = setTimeout(() => {
                        fetchResult()
                    }, 5000)
                } else if (axios.isAxiosError(err) && err.response?.status === 504) {
                    setStatus("timeout")
                    if (intervalRef.current) clearInterval(intervalRef.current)
                } else {
                    setError(err)
                    setStatus("error")
                    if (intervalRef.current) clearInterval(intervalRef.current)
                }
            }
        }

        intervalRef.current = setInterval(fetchResult, intervalMs)
        fetchResult()
        
        return () => {
            if (intervalRef.current) clearInterval(intervalRef.current)
            if (retryTimeoutRef.current) clearTimeout(retryTimeoutRef.current)
            controller.abort()
        }
    }, [measurementId])

    return {result, status, error}
}
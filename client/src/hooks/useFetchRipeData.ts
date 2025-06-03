import {useEffect, useState, useRef} from "react"
import axios from "axios"
import { RIPEData } from "../utils/types"
import { transformJSONDataToRIPEData } from "../utils/transformJSONDataToRIPEData"

/**
 * The endpoint to poll RIPE measurements from the backend
 * When a new measurement is started, it resets the state of teh measurement to not show old data
 * It then performs a GET request every interval and updates the data that was fetched
 * When the status becomes "complete" or "error", the call ends
 * @param measurementId the ID of the RIPE measurement to be polled
 * @param intervalMs the interval at which data will be polled from the endpoint
 * @returns the current set of results, the status of the polling, and if an error has occured
 */
export const useFetchRIPEData = (measurementId: string | null, intervalMs = 400) => {
    const [result, setResult] = useState<RIPEData[] | null>(null)
    const [status, setStatus] = useState<"idle" | "polling" | "complete" | "error">("idle")
    const [error, setError] = useState<Error | null>(null)

    // @ts-ignore
    const intervalRef = useRef<NodeJS.Timeout | null>(null)

    useEffect(() => {
        if (!measurementId) {
            setResult(null)
            setStatus("idle")
            setError(null)
            return
        }

        setStatus("polling")
        setError(null)

        const fetchResult = async () => {
            try {
                const res = await axios.get(`${import.meta.env.VITE_SERVER_HOST_ADDRESS}/measurements/ripe/${measurementId}`)
                if (res.data?.results) {
                    const transformedData = res.data.results.map((d: any) => transformJSONDataToRIPEData(d))
                    setResult(transformedData)
                }
                if (res.data.status === "complete") {
                    setStatus("complete")
                    if (intervalRef.current) clearInterval(intervalRef.current)
                } else if (res.data.status === "pending") {
                    setStatus("polling")
                } else if (res.data.status === "error") {
                    setError(new Error(res.data.message || "Unknown error"))
                    setStatus("error")
                    if (intervalRef.current) clearInterval(intervalRef.current)
                }
            } catch (err: any) {
                setError(err)
                setStatus("error")
                if (intervalRef.current) clearInterval(intervalRef.current)
            }
        }

        intervalRef.current = setInterval(fetchResult, intervalMs)
        fetchResult()
        
        return () => {
            if (intervalRef.current) clearInterval(intervalRef.current)
        }
    }, [measurementId])

    return {result, status, error}
}
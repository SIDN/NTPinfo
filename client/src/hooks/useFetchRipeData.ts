import {useEffect, useState, useRef} from "react"
import axios from "axios"
import { RIPEData } from "../utils/types"
import { transformJSONDataToRIPEData } from "../utils/transformJSONDataToRIPEData"

export const useFetchRIPEData = (measurementId: string | null, intervalMs = 3000) => {
    const [result, setResult] = useState<RIPEData| null>(null)
    const [status, setStatus] = useState<"idle" | "polling" | "complete" | "error">("idle")
    const [error, setError] = useState<Error | null>(null)

    // @ts-ignore
    const intervalRef = useRef<NodeJS.Timeout | null>(null)

    useEffect(() => {
        if (!measurementId) return

        setStatus("polling")
        setError(null)

        const fetchResult = async () => {
            try {
                const res = await axios.get(`${import.meta.env.VITE_SERVER_HOST_ADDRESS}/measurements/ripe/${measurementId}`)
                const transformedData = transformJSONDataToRIPEData(res.data.results)
                setResult(transformedData)
                if (res.data.status === "complete") {
                    setStatus("complete")
                    if (intervalRef.current) clearInterval(intervalRef.current)
                }
            } catch (err: any) {
                setError(err)
                setStatus("error")
                if (intervalRef.current) clearInterval(intervalRef.current)
            }
        }

        intervalRef.current = setInterval(fetchResult, intervalMs)

        // Clean up on unmount
        return () => {
            if (intervalRef.current) clearInterval(intervalRef.current)
        }
    }, [measurementId])

    return {result, status, error}
}

// import { useState } from "react"
// import axios from "axios"
// import { RIPEData } from "../utils/types.ts"
// import { transformJSONDataToRIPEData } from "../utils/transformJSONDataToRIPEData.ts"

// export const useFetchRIPEData = () => {
//     const [data, setData] = useState<RIPEData[] | null>(null)
//     const [loading, setLoading] = useState(false)
//     const [error, setError] = useState<Error | null>(null)
//     const [httpStatus, setHttpStatus] = useState<number>(200)
//     /**
//      * send a poll request to the backend to get RIPE data measurements
//      * @param endpoint the endpoint to make the post call to
//      * @param payload the server that will be measured
//      * @returns the data received from the measurement as RIPEData, or null
//      */
//     const fetchData = async (endpoint: string, payload: {server: string}) => {
//         setLoading(true);
//         setError(null);
//         try {
//             const resp = await axios.post(endpoint,payload, {
//                     headers: {
//                         "Content-Type": "application/json"
//                     }
//                 }
//             )
//             const measurements = resp.data !== null ? resp.data : []
//             const transformedData = measurements.map((d: any) => transformJSONDataToRIPEData(d))
//             setData(transformedData)
//             setHttpStatus(resp.status)
//             return transformedData
//         } catch (err: any) {
//             setError(err)
//             setHttpStatus(err.response?.status)
//             return null
//         } finally {
//             setLoading(false)
//         }
//     };
    
//     return {data, loading, error, httpStatus, fetchData}
// }
import { useState } from "react"
import axios from "axios"
import { RIPEResp } from "../utils/types"

    /**
     * trigger the RIPE measurement for the backend by using a POST request
     * @param payload the same payload as the measurement API
     * @returns the data returned by the call as RIPEResp, which contains the measurement id and vantage point ip
     * the loading status of the trigger call, the error that was caught in case of a bug, and a function to call the trigger function directly
     */
export const useTriggerRipeMeasurement = () => {
    const [data, setData] = useState<RIPEResp | null>(null)
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState<Error | null>(null)
    
    const triggerMeasurement = async (payload: {server: string, ipv6_measurement: boolean}) => {
        setLoading(true)
        setError(null)
        try {
            const resp = await axios.post(`${import.meta.env.VITE_SERVER_HOST_ADDRESS}/measurements/ripe/trigger/`,payload, {
                    headers: {
                        "Content-Type": "application/json"
                    }
                }
            )
            const measurementId = resp.data?.measurement_id ?? null
            const vantage_point_ip = resp.data?.vantage_point_ip ?? null
            const coordinates = resp.data?.vantage_point_location?.coordinates ?? null
            const parsedData = {measurementId, vantage_point_ip, coordinates}
            setData(parsedData)
            return {parsedData}
        } catch (err: any) {
            setError(err)
            return null
        } finally {
            setLoading(false)
        }
    };
    
    return {data, loading, error, triggerMeasurement}
}
import { useState } from "react"
import axios from "axios"
import { RIPEResp } from "../utils/types"

export const triggerRipeMeasurement = () => {
    const [data, setData] = useState<RIPEResp | null>(null)
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState<Error | null>(null)
    /**
     * trigger the RIPE measurement for the backend
     * @param payload the same payload as the measurement API
     * @returns the data returned by the call as RIPEResp, which contains the measurement id and the list of IPs that could be chosen
     * the loading status of the trigger call, the error that was caught in case of a bug, and a function to call the trigger function directly
     */
    const triggerMeasurement = async (payload: {server: string}) => {
        setLoading(true)
        setError(null)
        try {
            const resp = await axios.post(`${import.meta.env.VITE_SERVER_HOST_ADDRESS}/measurements/ripe/trigger/`,payload, {
                    headers: {
                        "Content-Type": "application/json"
                    }
                }
            )
            const measurementId = resp.data?.measurement_id || null
            const ipList = resp.data?.ip_list || null
            const parsedData = {measurementId, ipList}
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
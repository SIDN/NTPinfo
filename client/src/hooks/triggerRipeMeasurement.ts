import { useState } from "react"
import axios from "axios"

export const triggerRipeMeasurement = () => {
    const [measurementId, setMeasurementId] = useState<string | null>(null)
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState<Error | null>(null)
    /**
     * send a post request to the back-end
     * @param endpoint the endpoint to make the post call to
     * @param payload the server that will be measured, as well as the choice of the user whether to calculate the jitter
     * @returns the data received from the measurement as NTPData, or null
     */
    const triggerMeasurement = async (payload: {server: string, jitter_flag : boolean, measurements_no : number | null}) => {
        setLoading(true)
        setError(null)
        try {
            const resp = await axios.post(`${import.meta.env.VITE_SERVER_HOST_ADDRESS}/measurements/ripe/trigger/`,payload, {
                    headers: {
                        "Content-Type": "application/json"
                    }
                }
            )
            if (resp.data?.measurement_id) {
                setMeasurementId(resp.data.measurement_id)
            }
            return resp.data.measurement_id
        } catch (err: any) {
            setError(err)
            return null
        } finally {
            setLoading(false)
        }
    };
    
    return {measurementId, loading, error, triggerMeasurement}
}
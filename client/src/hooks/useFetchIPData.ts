import { useState } from "react"
import axios from "axios"
import { NTPData } from "../types"
import { transformJSONData } from "../transformJSONData"

export const useFetchIPData = () => {
    const [data, setData] = useState<NTPData | null>(null)
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState<Error | null>(null)

    /**
     * send a post request to the back-end
     * @param endpoint the endpoint to make the post call to
     * @param payload the server that will be measured
     * @returns the data received from the measurement as NTPData, or null
     */
    const fetchData = async (endpoint: string, payload: {server: string}) => {
        setLoading(true);
        setError(null);
        try {
            const resp = await axios.post(endpoint,payload, {
                    headers: {
                        "Content-Type": "application/json"
                    }
                }
            )
            const transformedData = transformJSONData(resp.data.measurement)
            setData(transformedData)
            return transformedData
        } catch (err: any) {
            setError(err)
            return null
        } finally {
            setLoading(false)
        }
    };
    
    return {data, loading, error, fetchData}
}
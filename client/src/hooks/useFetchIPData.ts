import { useState } from "react"
import axios from "axios"
import { NTPData } from "../utils/types.ts"
import { transformJSONDataToNTPData } from "../utils/transformJSONDataToNTPData.ts"

export const useFetchIPData = () => {
    const [data, setData] = useState<NTPData | null>(null)
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState<Error | null>(null)
    const [httpStatus, setHttpStatus] = useState<number>(200)
    /**
     * send a post request to the back-end for receiving data from the NTP server
     * It receives an array of results, which is used to compare with the server used by RIPE
     * The measurement for each of them is converted to an NTPData point
     * @param endpoint the endpoint to make the post call to
     * @param payload the server that will be measured
     * @returns the data received from the measurement as NTPData, or null, the loading, error and HTTP status of the call, and a function to initiate the measurement
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
            const measurements = resp.data?.measurement || []
            const transformedData = measurements.map((d: any) => transformJSONDataToNTPData(d))
            setData(transformedData)
            setHttpStatus(resp.status)
            return transformedData
        } catch (err: any) {
            setError(err)
            setHttpStatus(err.response?.status)
            return null
        } finally {
            setLoading(false)
        }
    };
    
    return {data, loading, error, httpStatus, fetchData}
}
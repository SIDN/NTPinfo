import { useState } from "react"
import axios from "axios"
import { NTPData } from "../utils/types.ts"
import { transformJSONDataToNTPData } from "../utils/transformJSONDataToNTPData.ts"

/**
 * send a post request to the back-end for receiving data from the NTP server
 * It receives an array of results which are converted to NTPData data points
 * In the case of an error it catches both the message sent by the back-end, as well as the one sent by axios
 * @param endpoint the endpoint to make the post call to
 * @param payload the server that will be measured, and if the measurement should be done using IPv6
 * @returns the data received from the measurement as NTPData, or null, the loading, error and HTTP status of the call, the error message sent by the back-end, and a function to initiate the measurement
 */
export const useFetchIPData = () => {
    const [data, setData] = useState<NTPData[] | null>(null)
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState<Error | null>(null)
    const [errorMessage, setErrorMessage] = useState<string | null>(null)
    const [httpStatus, setHttpStatus] = useState<number>(200)
    const fetchData = async (endpoint: string, payload: {server: string, ipv6_measurement: boolean}) => {
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
            console.warn(err)
            setError(err)
            setErrorMessage(err.response?.data.detail)
            setHttpStatus(err.response?.status)
            return null
        } finally {
            setLoading(false)
        }
    }
    
    return {data, loading, error, errorMessage, httpStatus, fetchData}
}
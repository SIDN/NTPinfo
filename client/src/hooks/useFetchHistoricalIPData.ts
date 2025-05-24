import { useState } from "react"
import axios from "axios"
import { NTPData } from "../utils/types.ts"
import { transformJSONData } from "../utils/transformJSONData.ts"

export const useFetchHistoricalIPData = () => {
    const [data, setData] = useState<NTPData[] | null>(null)
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState<Error | null>(null)

    /**
     * Get the historical data for a specific server in between two chosen time stamps
     * @param endpoint the link to the endpoint that will provide the data: under the form 
     * /measurements/history/?server=${query}&start=${startDate}&end=${endDate}, where 
     * server is the one provided by the user
     * startDate the start time from when the measurements were taken
     * endDate the end time until when the measurements were taken
     * The dates should be provided in ISO 8601 format
     * @returns 
     */
    const fetchData = async (endpoint: string) => {
        setLoading(true)
        setError(null)
        try {
            const resp = await axios.get(endpoint);
            const measurements = resp.data?.measurements || []
            const transformedData = measurements.map((d: any) => transformJSONData(d))
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
};
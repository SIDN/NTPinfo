import { useState } from "react"
import axios from "axios"
import { NTPData } from "../types"
import { transformJSONData } from "../transformJSONData"

export const useFetchHistoricalIPData = () => {
    const [data, setData] = useState<NTPData[] | null>(null)
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState<Error | null>(null)

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
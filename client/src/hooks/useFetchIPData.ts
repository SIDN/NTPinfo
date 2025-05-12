import { useState } from "react"
import axios from "axios"
import { NTPData } from "../types"
import { transformJSONData } from "../transformJSONData"

export const useFetchIPData = () => {
    const [data, setData] = useState<NTPData | null>(null)
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState<Error | null>(null)

    const fetchData = async (endpoint: string) => {
        setLoading(true);
        setError(null);
        try {
            const resp = await axios.post(endpoint)
            const transformedData = transformJSONData(resp.data)
            setData(transformedData ? transformedData[0] : null)
            return transformedData ? transformedData[0] : null
        } catch (err: any) {
            setError(err)
            return null
        } finally {
            setLoading(false)
        }
    };
    
    return {data, loading, error, fetchData}
}
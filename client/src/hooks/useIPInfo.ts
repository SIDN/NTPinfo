import { useState } from "react"
import axios from "axios"

export interface IPInfoData {
    coordinates: [number,number]
    country_code: string
}

const transformIpData = (input: any): IPInfoData => ({
    coordinates: [input.lat, input.lon],
    country_code: input.countryCode
})

export const useIPInfo = () => {
    const [ipInfo,setIPInfo] = useState<IPInfoData | null>(null)
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState<Error | null>(null)

    const fetchIPInfo = async (ip: string) => {
        setLoading(true)
        setError(null)
        try{
            const res = await axios.get(`http://ip-api.com/json/${ip}`)
            const data = transformIpData(res.data)
            setIPInfo(data)
            return data
        } catch (err: any) {
            setError(err)
            return null
        } finally {
            setLoading(false)
        }
    }

    const clearIP = () => setIPInfo(null)

    return {ipInfo, fetchIPInfo, clearIP, loading, error}
}
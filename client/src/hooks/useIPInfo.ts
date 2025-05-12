import { useState } from "react";
import axios from "axios";

export interface IPInfoData {
    ip: string,
    loc?: string,
    country?: string,
    is_anycast?: boolean
}

const transformIpData = (input: any): IPInfoData => ({
    ip: input.ip,
    loc: input.loc,
    country: input.country,
    is_anycast: input.is_anycast
})

export const useIPInfo = () => {
    const [ipInfo,setIPInfo] = useState<IPInfoData | null>(null)
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState<Error | null>(null)

    const fetchIP = async (): Promise<IPInfoData | null> => {
        setLoading(true);
        setError(null);
        try{
            const res = await axios.get(`https://ipinfo.io/json?token=${import.meta.env.VITE_IPINFO_TOKEN}`)
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

    return {ipInfo, fetchIP, clearIP, loading, error}
}
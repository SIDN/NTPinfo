import { useState } from "react";
import axios from "axios";

export interface IPInfoData {
    ip: string,
    loc?: string,
    country?: string
}

export const useIPInfo = () => {
    const [ipInfo,setIPInfo] = useState<IPInfoData | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<Error | null>(null);

    const fetchIP = async () => {
        setLoading(true);
        setError(null);
        try{
            const res = await axios.get(`https://ipinfo.io/json?token=${import.meta.env.VITE_IPINFO_TOKEN}`);
            setIPInfo(res ? res.data : null);
        } catch (err: any) {
            setError(err);
        } finally {
            setLoading(false);
        }
    }

    const clearIP = () => setIPInfo(null);

    return {ipInfo, fetchIP, clearIP, loading, error};
}
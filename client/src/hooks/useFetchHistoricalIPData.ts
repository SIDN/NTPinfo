import { useState } from "react";
import axios from "axios";
import { NTPData } from "../types";
import { transformJSONData } from "../transformJSONData";

export const useFetchHistoricalIPData = () => {
    const [data, setData] = useState<NTPData[] | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<Error | null>(null);

    const fetchData = async (endpoint: string) => {
        setLoading(true);
        setError(null);
        try {
            const resp = await axios.get(endpoint);
            const transformedData = transformJSONData(resp.data);
            setData(transformedData ? transformedData : null);
        } catch (err: any) {
            setError(err);
        } finally {
            setLoading(false);
        }
    };
    
    return {data, loading, error, fetchData};
};
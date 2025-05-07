import { NTPData } from "./types";

export const transformJSONData = (fetchedData: any[]): NTPData[] | null => {
    if (!fetchedData || fetchedData.length == 0) 
        return null;
    
    return fetchedData.map(data => ({
        offset: data.offset,
        delay: data.delay,
        stratum: data.stratum,
        jitter: data.precision,
        reachability: data.reachability,
        passing: true,
        time: data.client_sent_time
    }));
};
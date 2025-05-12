import { NTPData } from "./types";

export const transformJSONData = (fetchedData: any): NTPData | null => {
    if (!fetchedData) 
        return null
    
    return {
        offset: fetchedData.offset,
        RTT: fetchedData.delay,
        stratum: fetchedData.stratum,
        jitter: fetchedData.precision,
        reachability: 1,
        status: fetchedData.reachability,
        time: fetchedData.client_sent_time.seconds
    }
};
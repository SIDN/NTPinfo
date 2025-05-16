import { NTPData } from "./types";

export const transformJSONData = (fetchedData: any): NTPData | null => {
    if (!fetchedData) 
        return null
    
    return {
        offset: fetchedData.offset.toFixed(10),
        RTT: fetchedData.delay.toFixed(10),
        stratum: fetchedData.stratum,
        jitter: fetchedData.jitter,
        precision: fetchedData.precision,
        status: fetchedData.reachability,
        time: fetchedData.client_sent_time.seconds
    }
};
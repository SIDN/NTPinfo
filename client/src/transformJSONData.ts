import { NTPData } from "./types";

export const transformJSONData = (fetchedData: any): NTPData | null => {
    if (!fetchedData) 
        return null
    
    return {
        offset: fetchedData.offset,
        RTT: fetchedData.delay,
        stratum: fetchedData.stratum,
        jitter: fetchedData.jitter,
        precision: fetchedData.precision,
        status: fetchedData.reachability,
        time: fetchedData.client_sent_time.seconds
    }
};
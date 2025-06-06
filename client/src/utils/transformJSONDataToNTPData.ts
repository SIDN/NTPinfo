import { NTPData } from "./types.ts"

/**
 * Function to convert the received measurement or single historical data JSON into an NTPData datapoint.
 * All values are extracted directly from the JSON file, with the exception of time.
 * Time is converted from the NTP Epoch to the UNIX Epoch before being stored.
 * @param fetchedData the JSON which will be received from the measurement or historical data endpoint.
 * @returns a single NTPData filled with information extracted from the JSON, or null if there is no JSON.
 */
export const transformJSONDataToNTPData = (fetchedData: any): NTPData | null => {
    if (!fetchedData) 
        return null
    
    return {
        offset: fetchedData.offset,
        RTT: fetchedData.rtt,
        stratum: fetchedData.stratum,
        jitter: fetchedData.jitter,
        precision: fetchedData.precision,
        status: fetchedData.reachability,
        time: (fetchedData.client_sent_time.seconds - 2208988800) * 1000,
        ip: fetchedData.ntp_server_ip,
        server_name: fetchedData.ntp_server_name,
        ref_ip: fetchedData.ntp_server_ref_parent_ip,
        ref_name: fetchedData.ref_name,
        root_delay: fetchedData.root_delay.seconds
    }
};
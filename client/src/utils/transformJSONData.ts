import { NTPData } from "./types.ts";

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
        time: (fetchedData.client_sent_time.seconds - 2208988800) * 1000,
        ip: fetchedData.ntp_server_ip,
        ip_list: fetchedData.other_server_ips,
        server_name: fetchedData.ntp_server_name
    }
};
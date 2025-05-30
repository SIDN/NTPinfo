import { NTPData } from "./types.ts"
import { RIPEData } from "./types.ts"

export const transformJSONDataToRIPEData = (fetchedData: any): RIPEData | null => {
    if(!fetchedData)
        return null

    const measurementData: NTPData = {
        offset: fetchedData.result.offset,
        RTT: fetchedData.result.rtt,
        stratum: fetchedData.stratum,
        jitter: null,
        precision: fetchedData.precision,
        status: "",
        time: (fetchedData.result.client_sent_time.seconds - 2208988800) * 1000,
        ip: fetchedData.ntp_server_ip,
        ip_list: [""],
        server_name: fetchedData.ntp_server_name,
        ref_ip: "",
        ref_name: fetchedData.ref_id,
        root_delay: fetchedData.root_delay.seconds
    }
    return{
        measurementData: measurementData,
        probe_id: fetchedData.probe_id,
        probe_country: fetchedData.probe_location.country_code,
        probe_location: fetchedData.probe_location.coordinates,
        got_results: fetchedData.result.rtt !== -1
    }
}
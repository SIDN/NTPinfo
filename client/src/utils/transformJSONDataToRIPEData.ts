import { NTPData } from "./types.ts"
import { RIPEData } from "./types.ts"

/**
 * A function to convert the received RIPE measurement JSON to a RIPEData datapoint.
 * All values are extracted directly from the JSON file, with a few exceptions.
 * Time is converted from the NTP Epoch to the UNIX Epoch before being stored.
 * status, ip_list and ref_ip are filled as empty due to them not being send in the JSON
 * got_results is filled as a boolean to indicate whether the probe sucessfully finished its measurement, as we could receive probes with no measurement values
 * by our set convention, -1 is the default value in the measurement fields, and it indicates that the measurement was not completed by the probe
 * @param fetchedData the JSON which will be received from the RIPE measurement endpoint.
 * @returns A single RIPEData datapoint filled with information extracted from the JSON, or null if there is no JSON
 */
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
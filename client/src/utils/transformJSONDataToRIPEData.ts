import { NTPData } from "./types.ts"
import { RIPEData } from "./types.ts"

/**
 * A function to convert the received RIPE measurement JSON to a RIPEData datapoint.
 * All values are extracted directly from the JSON file, with a few exceptions.
 * Time is converted from the NTP Epoch to the UNIX Epoch before being stored.
 * status, ip_list and ref_ip are filled as empty due to them not being send in the JSON.
 * offset and RTT are multiplied by 1000 since they are sent in seconds instead of ms.
 * got_results is filled as a boolean to indicate whether the probe sucessfully finished its measurement, as we could receive probes with no measurement values.
 * by our set convention, -1 is the default value in the measurement fields, and it indicates that the measurement was not completed by the probe.
 * The probe_types field is there to show the types of probes that were chosen for the measurement.
 * @param fetchedData the JSON which will be received from the RIPE measurement endpoint.
 * @returns A single RIPEData datapoint filled with information extracted from the JSON, or null if there is no JSON
 */
export const transformJSONDataToRIPEData = (fetchedData: any): RIPEData | null => {
    if (!fetchedData || !Array.isArray(fetchedData.result) || fetchedData.result.length === 0) {
        return null
    }

    const measurement = fetchedData.result[0]

    const measurementData: NTPData = {
        offset: Number((measurement.offset * 1000).toFixed(3)),
        RTT: Number((measurement.rtt * 1000).toFixed(3)),
        stratum: fetchedData.stratum,
        jitter: null,
        precision: fetchedData.precision,
        status: "",
        time: (measurement.client_sent_time.seconds - 2208988800) * 1000,
        ip: fetchedData.ntp_server_ip,
        server_name: fetchedData.ntp_server_name,
        ref_ip: "",
        ref_name: fetchedData.ref_id,
        root_delay: fetchedData.root_delay.seconds,
        vantage_point_ip: fetchedData.vantage_point_ip
    }
    return{
        measurementData: measurementData,
        probe_id: fetchedData.probe_id,
        probe_country: fetchedData.probe_location.country_code,
        probe_location: [fetchedData.probe_location.coordinates[1], fetchedData.probe_location.coordinates[0]],
        got_results: measurement.rtt !== -1,
        probe_types: [fetchedData.probe_count_per_type.asn, fetchedData.probe_count_per_type.prefix, fetchedData.probe_count_per_type.country, fetchedData.probe_count_per_type.area, fetchedData.probe_count_per_type.random]
    }
}
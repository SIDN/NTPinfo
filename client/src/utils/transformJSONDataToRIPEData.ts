import { NTPData } from "./types.ts"
import { RIPEData } from "./types.ts"

/**
 * A function to convert the received RIPE measurement JSON to a RIPEData datapoint.
 * All values are extracted directly from the JSON file, with a few exceptions.
 * Time is converted from the NTP Epoch to the UNIX Epoch before being stored.
 * status, ip_list and ref_ip are filled as empty due to them not being send in the JSON.
 * offset and RTT are multiplied by 1000 since they are sent in seconds instead of ms.
 * got_results is filled as a boolean to indicate whether the probe sucessfully finished its measurement, as we could receive probes with no measurement values.
 * By our set convention, -1 is the default value in the measurement fields, and it indicates that the measurement was not completed by the probe.
 * The measurement ID is stored here as well as in the trigger for showing it together will all the other results.
 * @param fetchedData the JSON which will be received from the RIPE measurement endpoint.
 * @returns A single RIPEData datapoint filled with information extracted from the JSON, or null if there is no JSON
 */
export const transformJSONDataToRIPEData = (fetchedData: any): RIPEData | null => {
    if (!fetchedData || !Array.isArray(fetchedData.result) || fetchedData.result.length === 0) {
        return null
    }

    //const measurement = fetchedData.result[0]

    const measurementData: NTPData = {
        ntp_version: fetchedData.ntp_verison, //
        vantage_point_ip: fetchedData.vantage_point_ip,//
        ip: fetchedData.ntp_server_ip,//
        server_name: fetchedData.ntp_server_name, //
        is_anycast: fetchedData.ntp_server_location.ip_is_anycast,//
        country_code: fetchedData.ntp_server_location.country_code,//
        coordinates: [fetchedData.ntp_server_location.coordinates[0],fetchedData.ntp_server_location.coordinates[1]],//
        ntp_server_ref_parent_ip: "", 
        ref_id: fetchedData.fetchedData.ref_id ?? null,//
        client_sent_time: [fetchedData.client_sent_time.seconds, fetchedData.client_sent_time.fraction],//
        server_recv_time: [fetchedData.server_recv_time.seconds, fetchedData.server_recv_time.fraction],//
        server_sent_time: [fetchedData.server_sent_time.seconds, fetchedData.server_sent_time.fraction],//
        client_recv_time: [fetchedData.client_recv_time.seconds, fetchedData.client_recv_time.fraction],//
        offset: Number((fetchedData.offset * 1000).toFixed(3)), //measurement
        RTT: Number((fetchedData.rtt * 1000).toFixed(3)), //measurement
        stratum: fetchedData.stratum,//
        precision: fetchedData.precision,//
        root_delay: fetchedData.root_delay,//
        poll: fetchedData.poll,//
        root_dispersion: fetchedData.root_dispersion,//
        ntp_last_sync_time: [-1, -1],
        leap: -1,
        jitter: -1,
        nr_measurements_jitter: -1,
        time: (fetchedData.client_sent_time.seconds - 2208988800) * 1000 //measurement
    }
    return{
        measurementData: measurementData,
        probe_addr_v4: fetchedData.probe_addr.ipv4,
        probe_addr_v6: fetchedData.probe_addr.ipv6,
        probe_id: fetchedData.probe_id,
        probe_country: fetchedData.probe_location.country_code,
        probe_location: [fetchedData.probe_location.coordinates[1], fetchedData.probe_location.coordinates[0]],
        time_to_result: fetchedData.time_to_result,
        got_results: fetchedData.rtt !== -1, //measurement
        measurement_id: fetchedData.ripe_measurement_id
    }
}
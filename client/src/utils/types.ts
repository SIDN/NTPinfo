import { LatLngTuple } from "leaflet"

/**
 * Data type used for manipulating and using NTP information
 */
export type NTPData = {
  offset: number
  RTT: number
  stratum: number
  jitter: number | null
  precision: number
  time: number
  ip: string
  server_name: string,
  ref_id: string,
  root_dispersion: number,
  root_delay: number,
  vantage_point_ip: string
}

/**
 * Data type used for determing measurement type in the visualization graphs
 */
export type Measurement = "RTT" | "offset"

/**
 * Data type used for manipulating and using RIPE information
 */
export type RIPEData = {
  measurementData : NTPData
  probe_id: number
  probe_country: string
  probe_location: LatLngTuple
  got_results: boolean
  measurement_id: number
  probe_types: number[]
}

/**
 * Data type for the RIPE measurement trigger response
 */
export type RIPEResp = {
  measurementId: number
  vantage_point_ip: string
}

/**
 * A single place to remember everything we want to preserve
 * when the user leaves and re-enters the Home tab.
 * (Feel free to add more fields later – e.g. `selOption` –
 * just keep the shape in sync everywhere you use it.)
 */
export interface HomeCacheState {
  ntpData: NTPData | null
  chartData: Map<string, NTPData[]> | null
  measured: boolean
  selMeasurement: Measurement          // 'offset' | 'RTT'
  measurementId: string | null
  vantagePointIp: string | null
  allNtpMeasurements: NTPData[] | null
  ripeMeasurementResp: RIPEData[] | null
  ripeMeasurementStatus: string | null     // 'loading' | 'complete' | ...
}
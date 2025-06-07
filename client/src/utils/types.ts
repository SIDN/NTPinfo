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
  status: string
  time: number
  ip: string
  server_name: string,
  ref_ip: string,
  ref_name: string,
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
  probe_types: number[]
}

/**
 * Data type for the RIPE measurement trigger response
 */
export type RIPEResp = {
  measurementId: number
  vantage_point_ip: string
}
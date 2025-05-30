import { LatLngTuple } from "leaflet"

export type NTPData = {
  offset: number
  RTT: number
  stratum: number
  jitter: number | null
  precision: number
  status: string
  time: number
  ip: string
  ip_list: string[]
  server_name: string,
  ref_ip: string,
  ref_name: string,
  root_delay: number
}

export type Measurement = "RTT" | "offset"

export type RIPEData = {
  measurementData : NTPData
  probe_id: number
  probe_country: string
  probe_location: LatLngTuple
  got_results: boolean
}
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
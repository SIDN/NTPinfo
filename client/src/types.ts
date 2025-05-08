export type NTPData = {
  offset: number
  RTT: number
  stratum: number
  jitter: number
  reachability: number
  status: string
  time: number
}

export type Measurement = 'RTT' | 'offset'
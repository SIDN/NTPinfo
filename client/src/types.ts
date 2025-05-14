export type NTPData = {
  offset: number
  RTT: number
  stratum: number
  jitter: number
  precision: number
  status: string
  time: number
}

export type Measurement = 'RTT' | 'offset'
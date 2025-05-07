import { NTPData } from "../types"  
export type Measurement = 'delay' | 'offset'
//this server map will only be kept temporarily as a placeholder for the actual API calls to get data from the NTP servers
export const ntpMap = new Map<string, NTPData>([
    ['time.google.com', {
      offset: -2.3,
      RTT: 12,
      stratum: 1,
      jitter: 1.8,
      reachability: 100,
      status: 'PASSING',
      time: Date.now() - 6000
    }],
    ['pool.ntp.org', {
      offset: 1.2,
      RTT: 15,
      stratum: 2,
      jitter: 2.5,
      reachability: 90,
      status: 'PASSING',
      time: Date.now() - 4000
    }], 
    ['time.apple.com', {
        offset: .72,
        RTT: 1.5,
        stratum: 2,
        jitter: .25,
        reachability: 80,
        status: 'FAILING',
        time: Date.now() - 2000
    }]
])
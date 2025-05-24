import { NTPData } from "./types"
export const calculateStatus = (data: NTPData): string => {
    if (Math.abs(data.offset) <= 0.1 && 
        data.RTT <= 0.01 && 
        ((data.jitter != null && data.jitter <= 0.002) || data.jitter == null) &&
        data.stratum <= 2)
        return 'PASSING'
    if (data.stratum <= 3 &&
        (
            (0.01 < data.RTT && data.RTT <= 0.1) ||
            (0.1 < Math.abs(data.offset) && Math.abs(data.offset) <= 0.5) ||
            ((data.jitter != null &&  0.002 <= data.jitter && data.jitter <= 0.01) || data.jitter == null)
        ))
        return 'UNSTABLE'
    return 'FAILING'
}
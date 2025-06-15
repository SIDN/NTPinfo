import { NTPData } from "./types"
export const calculateStatus = (data: NTPData): string => {
    if (Math.abs(data.offset) <= 100 && 
        data.RTT <= 10 && 
        ((data.jitter != null && data.jitter <= 2) || data.jitter == null) &&
        data.stratum <= 2)
        return 'PASSING'
    if (data.stratum <= 3 &&
        (
            (10 < data.RTT && data.RTT <= 100) ||
            (100 < Math.abs(data.offset) && Math.abs(data.offset) <= 500) ||
            ((data.jitter != null &&  2 <= data.jitter && data.jitter <= 10) || data.jitter == null)
        ))
        return 'UNSTABLE'
    return 'FAILING'
}
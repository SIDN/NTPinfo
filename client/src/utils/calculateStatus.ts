import { NTPData, RIPEData } from "./types"

export const calculateStatus = (ntpData: NTPData, ripeData: RIPEData): string => {
    if (Math.max(Math.abs(ntpData.offset), Math.abs(ripeData.measurementData.offset)) < import.meta.env.VITE_STATUS_THRESHOLD)
        return "PASSING"
    else if (Math.min(Math.abs(ntpData.offset), Math.abs(ripeData.measurementData.offset)) < import.meta.env.VITE_STATUS_THRESHOLD)
        return "CAUTION"
    return "FAILING"
}
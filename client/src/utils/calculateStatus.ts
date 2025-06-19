import { NTPData, RIPEData } from "./types"

export const calculateStatus = (ntpData: NTPData, ripeData: RIPEData): string => {
    if (Math.max(Math.abs(ntpData.offset), Math.abs(ripeData.measurementData.offset)) < 100)
        return "PASS"
    else if (Math.min(Math.abs(ntpData.offset), Math.abs(ripeData.measurementData.offset)) < 100)
        return "CAUTION"
    return "FAILING"
}
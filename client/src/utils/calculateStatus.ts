import { NTPData, RIPEData } from "./types"

/**
 * Calculates the status of the NTP server according to the threshold set in the .env file
 * @param ntpData The NTPData datapoint to be comapred
 * @param ripeData The RIPEData datapoint to be comapred
 * @returns "PASSING" if both offsets are smaller than the threshold, "CAUTION" if one of the offset is higher than the threshold
 * and "FAILING" if both are above the threshold
 */
export const calculateStatus = (ntpData: NTPData, ripeData: RIPEData): string => {
    if (Math.max(Math.abs(ntpData.offset), Math.abs(ripeData.measurementData.offset)) < import.meta.env.VITE_STATUS_THRESHOLD)
        return "PASSING"
    else if (Math.min(Math.abs(ntpData.offset), Math.abs(ripeData.measurementData.offset)) < import.meta.env.VITE_STATUS_THRESHOLD)
        return "CAUTION"
    return "FAILING"
}
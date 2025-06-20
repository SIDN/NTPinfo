/**
 * Function made for transforming time from UNIX to ISO8601, which is what is used by the backend endpoint
 * @param time the time to be converted to, given as UNIX time
 * @returns the time formatted as an ISO8601 string, up to second precision
 */
export const dateFormatConversion = (time: number): string => {
    const date = new Date(time - 60000)
    const iso = date.toISOString()
    return iso.split('.')[0] + 'Z'
}
import { useState } from "react"
import axios from "axios"

export interface IPInfoData {
    coordinates: [number,number]
    country_code: string
}

const transformIpData = (input: any): IPInfoData => ({
    coordinates: [input.lat, input.lon],
    country_code: input.countryCode
})

/**
 * An API hook used for getting IP data
 * It is mainly used for receiving geolocation data.
 * It makes use of the ip-api endpoint for getting the longitude and latitude of the IP given.
 * It is used on only the NTP server(s) used, as well as the vantage point, so there is no client privacy violated
 * It does not work for private IPs, so depening on where it is hosted, it might have some issues with getting the vantage point's location
 * @param ip The IP to be queried for data fetching
 * @returns the info itself, the function to fetch the info, a function to clear the state of the ip, loading status and an error status
 */
export const useIPInfo = () => {
    const [ipInfo,setIPInfo] = useState<IPInfoData | null>(null)
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState<Error | null>(null)

    const fetchIPInfo = async (ip: string) => {
        setLoading(true)
        setError(null)
        try{
            const res = await axios.get(`http://ip-api.com/json/${ip}`)
            const data = transformIpData(res.data)
            setIPInfo(data)
            return data
        } catch (err: any) {
            setError(err)
            return null
        } finally {
            setLoading(false)
        }
    }

    const clearIP = () => setIPInfo(null)

    return {ipInfo, fetchIPInfo, clearIP, loading, error}
}
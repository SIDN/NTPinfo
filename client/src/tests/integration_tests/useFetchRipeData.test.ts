import { renderHook } from '@testing-library/react'
import { useFetchRIPEData } from '../../hooks/useFetchRipeData'
import { waitFor } from '@testing-library/react'
import { RIPEData } from '../../utils/types'

const expected: RIPEData[] = [
        {
            measurementData: {
            ntp_version: 4,
            vantage_point_ip: "88.202.166.71",
            ip: "17.253.52.125",
            server_name: "time.apple.com",
            is_anycast: false,
            country_code: "NL",
            coordinates: [52.3824, 4.8995],
            ntp_server_ref_parent_ip: "",
            ref_id: "GPSs",
            client_sent_time: [3959232158, 4123875328],
            server_recv_time: [3959232158, 3914455040],
            server_sent_time: [3959232158, 3914508288],
            client_recv_time: [3959232158, 4132907008],
            offset: 49.805,
            RTT: 2.09,
            stratum: 1,
            precision: 9.53674e-7,
            root_delay: 0,
            poll: 64,
            root_dispersion: 0.00018310477025806904,
            ntp_last_sync_time: [-1, -1],
            leap: -1,
            jitter: -1,
            nr_measurements_jitter: -1,
            time: 1750243358000
            },
            probe_addr_v4: "88.202.166.71",
            probe_addr_v6: "2a04:8400:c300:ba00:ea94:f6ff:fe48:5f64",
            probe_id: "22138",
            probe_country: "NL",
            probe_location: [52.0015, 4.3685],
            time_to_result: 30.280227,
            got_results: true,
            measurement_id: 110405699
        },
        {
            measurementData: {
            ntp_version: 4,
            vantage_point_ip: "91.215.7.190",
            ip: "17.253.14.251",
            server_name: "time.apple.com",
            is_anycast: false,
            country_code: "DE",
            coordinates: [50.1169, 8.6837],
            ntp_server_ref_parent_ip: "",
            ref_id: "GPSs",
            client_sent_time: [3959232160, 1071108096],
            server_recv_time: [3959232159, 2370416640],
            server_sent_time: [3959232159, 2370535424],
            client_recv_time: [3959232160, 1108856832],
            offset: 701.862,
            RTT: 8.761,
            stratum: 1,
            precision: 4.76837e-7,
            root_delay: 0,
            poll: 64,
            root_dispersion: 0.000152587890625,
            ntp_last_sync_time: [-1, -1],
            leap: -1,
            jitter: -1,
            nr_measurements_jitter: -1,
            time: 1750243360000
            },
            probe_addr_v4: "91.215.7.190",
            probe_addr_v6: null,
            probe_id: "50350",
            probe_country: "NL",
            probe_location: [52.0075, 4.3595],
            time_to_result: 3.868,
            got_results: true,
            measurement_id: 110405699
        },
        {
            measurementData: {
            ntp_version: 4,
            vantage_point_ip: "145.94.58.246",
            ip: "17.253.14.253",
            server_name: "time.apple.com",
            is_anycast: false,
            country_code: "DE",
            coordinates: [50.1169, 8.6837],
            ntp_server_ref_parent_ip: "",
            ref_id: "GPSs",
            client_sent_time: [3959232159, 1762224128],
            server_recv_time: [3959232159, 1777287168],
            server_sent_time: [3959232159, 1777362944],
            client_recv_time: [3959232159, 1797818368],
            offset: 0.628,
            RTT: 8.269,
            stratum: 1,
            precision: 9.53674e-7,
            root_delay: 0,
            poll: 64,
            root_dispersion: 0.00016784691251814365,
            ntp_last_sync_time: [-1, -1],
            leap: -1,
            jitter: -1,
            nr_measurements_jitter: -1,
            time: 1750243359000
            },
            probe_addr_v4: "145.94.58.246",
            probe_addr_v6: "2001:610:908:c132:da58:d7ff:fe03:41a",
            probe_id: "61331",
            probe_country: "NL",
            probe_location: [51.9975, 4.3685],
            time_to_result: 0.969981,
            got_results: true,
            measurement_id: 110405699
        }
        ]

describe('useFetchRipeData', () => {
    it('fetches and sets ripe measurement data correctly - completed', async () => {
        const { result } = renderHook(() => useFetchRIPEData("1"))


        await waitFor(() => {
            expect(result.current.status).toBe("complete")
            expect(result.current.result).toEqual(expected)
        })

        expect(result.current.error).toBeNull()
    })
    it('fetches and sets ripe measurement data correctly - partial_results', async () => {
        const { result } = renderHook(() => useFetchRIPEData("2"))

        await waitFor(() => {
            expect(result.current.status).toBe("partial_results")
            expect(result.current.result).toEqual(expected)
        })

        expect(result.current.error).toBeNull()
    })
    it('fetches and sets ripe measurement data correctly - timeout', async () => {
        const { result } = renderHook(() => useFetchRIPEData("3"))

        await waitFor(() => {
            expect(result.current.status).toBe("complete")
            expect(result.current.result).toEqual(expected)
        })

        expect(result.current.error).toBeNull()
    })
    it('fetches and sets ripe measurement data correctly - pending', async () => {
        const { result } = renderHook(() => useFetchRIPEData("4"))

        await waitFor(() => {
            expect(result.current.status).toBe("pending")
            expect(result.current.result).toEqual(expected)
        })

        expect(result.current.error).toBeNull()
    })
    it('fetches and sets ripe measurement data correctly - error', async () => {
        const { result } = renderHook(() => useFetchRIPEData("5"))

        await waitFor(() => {
            expect(result.current.status).toBe("error")
            expect(result.current.result).toEqual(expected)
        })

        expect(result.current.error).not.toBeNull()
    })
    it('handles RIPE measurement error correctly', async () => {
        const { result } = renderHook(() => useFetchRIPEData("failed-error"))

        await waitFor(() => {
            expect(result.current.status).toBe("error")
        })
            
        expect(result.current.result).toBe(null)
        expect(result.current.error).not.toBeNull()
        expect(result.current.error?.message).toBe("Request failed with status code 500")
    })
    it('handles RIPE measurement timeout error correctly', async () => {
        const { result } = renderHook(() => useFetchRIPEData("failed-timeout"))

        await waitFor(() => {
            expect(result.current.status).toBe("timeout")
        })
            
        expect(result.current.result).toBe(null)
        expect(result.current.error).not.toBeNull()
        expect(result.current.error?.message).toBe("Request failed with status code 504")
    })
    it('handles RIPE null measurementId', async () => {
        const { result, rerender } = renderHook(({id}) => useFetchRIPEData(id), {
            initialProps: { id: "1" }
        })

        await waitFor(() => {
            expect(result.current.status).toBe("complete")
        })

        rerender({ id: "" })

        await waitFor(() => {
            expect(result.current.status).toBe("pending")
        })

        expect(result.current.result).toBe(null)
        expect(result.current.error).toBe(null)
    })
    it('handles RIPE measurement recall', async () => {
        const { result, rerender } = renderHook(({id}) => useFetchRIPEData(id), {
            initialProps: { id: "2" }
        })

        await waitFor(() => {
            expect(result.current.status).toBe("partial_results")
        })

        rerender({ id: "1" })

        await waitFor(() => {
            expect(result.current.status).toBe("complete")
            expect(result.current.result).toEqual(expected)
        })

        expect(result.current.error).toBeNull()
    })
    it('handles RIPE measurement timeout error correctly', async () => {
        const { result } = renderHook(() => useFetchRIPEData("failed-retry"))

        await waitFor(() => {
            expect(result.current.status).not.toBe("error")
            expect(result.current.status).not.toBe("timeout")
        })
            
        expect(result.current.result).toBe(null)
        expect(result.current.error).toBeNull()
    })
})
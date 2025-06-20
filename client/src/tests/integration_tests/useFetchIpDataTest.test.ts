import { renderHook, act } from '@testing-library/react'
import { useFetchIPData } from '../../hooks/useFetchIPData'
import { waitFor } from '@testing-library/react'
import { vi } from 'vitest'
import { NTPData } from '../../utils/types'
import axios from 'axios'

describe('useFetchIPData', () => {
    it('fetches and sets measurement data correctly', async () => {
        const { result } = renderHook(() => useFetchIPData())

        await act(async () => {
            await result.current.fetchData('/measurements/', { server: 'time.apple.com', ipv6_measurement:false })
        })

        await waitFor(() => {
            expect(result.current.loading).toBe(false)
        })

        const expected: NTPData[] = [
        {
            ntp_version: 4,
            vantage_point_ip: "145.94.203.168",
            ip: "17.253.52.253",
            server_name: "time.apple.com",
            is_anycast: false,
            country_code: "NL",
            coordinates: [52.3824, 4.8995],
            ntp_server_ref_parent_ip: null,
            ref_id: "GPSs",
            client_sent_time: [3959231207, 3938824192],
            server_recv_time: [3959231202, 60612608],
            server_sent_time: [3959231202, 60737536],
            client_recv_time: [3959231207, 3962165248],
            offset: -5905.669,
            RTT: 5.405,
            stratum: 1,
            precision: -20,
            root_delay: 0,
            poll: 6,
            root_dispersion: 0.0001678466796875,
            ntp_last_sync_time: [3959231196, 2094338048],
            leap: 0,
            jitter: 0.8551980300704615,
            nr_measurements_jitter: 8,
            asn_ntp_server: "6185",
            time: 1750242407000
        },
        {
            ntp_version: 4,
            vantage_point_ip: "145.94.203.168",
            ip: "17.253.14.125",
            server_name: "time.apple.com",
            is_anycast: false,
            country_code: "DE",
            coordinates: [50.1169, 8.6837],
            ntp_server_ref_parent_ip: null,
            ref_id: "GPSs",
            client_sent_time: [3959231207, 4003549184],
            server_recv_time: [3959231202, 152694784],
            server_sent_time: [3959231202, 152760320],
            client_recv_time: [3959231207, 4076879872],
            offset: -5905.126,
            RTT: 17.058,
            stratum: 1,
            precision: -20,
            root_delay: 0,
            poll: 6,
            root_dispersion: 0.0001373291015625,
            ntp_last_sync_time: [3959231198, 2253635584],
            leap: 0,
            jitter: 1.5482209225207348,
            nr_measurements_jitter: 8,
            asn_ntp_server: "6185",
            time: 1750242407000
        },
        {
            ntp_version: 4,
            vantage_point_ip: "145.94.203.168",
            ip: "17.253.52.125",
            server_name: "time.apple.com",
            is_anycast: false,
            country_code: "NL",
            coordinates: [52.3824, 4.8995],
            ntp_server_ref_parent_ip: null,
            ref_id: "GPSs",
            client_sent_time: [3959231207, 4114880512],
            server_recv_time: [3959231202, 253331456],
            server_sent_time: [3959231202, 253396992],
            client_recv_time: [3959231207, 4163008512],
            offset: -5904.682,
            RTT: 11.19,
            stratum: 1,
            precision: -20,
            root_delay: 0,
            poll: 6,
            root_dispersion: 0.0001068115234375,
            ntp_last_sync_time: [3959231200, 3654258688],
            leap: 0,
            jitter: 0.8562105498953563,
            nr_measurements_jitter: 8,
            asn_ntp_server: "6185",
            time: 1750242407000
        },
        {
            ntp_version: 4,
            vantage_point_ip: "145.94.203.168",
            ip: "17.253.28.123",
            server_name: "time.apple.com",
            is_anycast: false,
            country_code: "GB",
            coordinates: [51.5177, -0.6215],
            ntp_server_ref_parent_ip: null,
            ref_id: "GPSs",
            client_sent_time: [3959231207, 4202512384],
            server_recv_time: [3959231202, 390150144],
            server_sent_time: [3959231202, 390213632],
            client_recv_time: [3959231208, 24203264],
            offset: -5901.208,
            RTT: 27.147,
            stratum: 1,
            precision: -20,
            root_delay: 0,
            poll: 6,
            root_dispersion: 0.00018310546875,
            ntp_last_sync_time: [3959231196, 3131183104],
            leap: 0,
            jitter: 0,
            nr_measurements_jitter: 1,
            asn_ntp_server: "6185",
            time: 1750242407000
        }
        ]


        expect(result.current.httpStatus).toBe(200)
        expect(result.current.error).toBeNull()
        expect(result.current.data).toEqual(expected)
    })
    it('handles response with missing measurement field', async () => {
        vi.spyOn(axios, 'post').mockResolvedValueOnce({
            data: {},
            status: 200
        })

        const { result } = renderHook(() => useFetchIPData())

        await act(async () => {
            await result.current.fetchData('/measurements/', { server: 'time.apple.com', ipv6_measurement: false })
        })

        await waitFor(() => {
            expect(result.current.loading).toBe(false)
        })

        expect(result.current.data).toEqual([])
        expect(result.current.httpStatus).toBe(200)
        expect(result.current.error).toBeNull()
    })
    it('handles errors correctly', async () => {
        const { result } = renderHook(() => useFetchIPData())

        await act(async () => {
            await result.current.fetchData('/measurements/', { server: 'invalid.com', ipv6_measurement:false })
        })

        await waitFor(() => {
            expect(result.current.loading).toBe(false)
        })

        expect(result.current.data).toBe(null)
        expect(result.current.httpStatus).toBe(503)
        expect(result.current.error).not.toBeNull()
        expect(result.current.error?.message).toBe("Request failed with status code 503")
        expect(result.current.errorMessage).toBe("Server is not reachable.")
    })
})

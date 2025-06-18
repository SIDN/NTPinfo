import { renderHook, act } from '@testing-library/react'
import { useFetchHistoricalIPData } from '../../hooks/useFetchHistoricalIPData'
import { waitFor } from '@testing-library/react'
import { vi } from 'vitest'
import { NTPData } from '../../utils/types'
import axios from 'axios'

describe('useFetchHistoricalIPData', () => {
    it('fetches and sets historical measurement data correctly', async () => {
        const { result } = renderHook(() => useFetchHistoricalIPData())

        await act(async () => {
            await result.current.fetchData('/measurements/history/?server=time.apple.com&start=2025-06-10T10:24:00Z&end=2025-06-18T10:24:00Z')
        })

        await waitFor(() => {
            expect(result.current.loading).toBe(false)
        })

        const expected: NTPData[] = [
        {
            ntp_version: 4,
            vantage_point_ip: "145.90.49.147",
            ip: "17.253.52.253",
            server_name: "time.apple.com",
            is_anycast: false,
            country_code: "NL",
            coordinates: [52.3824, 4.8995],
            ntp_server_ref_parent_ip: null,
            ref_id: "GPSs",
            client_sent_time: [3958798919, 4197421056],
            server_recv_time: [3958798913, 939790336],
            server_sent_time: [3958798913, 939862016],
            client_recv_time: [3958798919, 4230189056],
            offset: -6762.283,
            RTT: 7.613,
            stratum: 1,
            precision: -20,
            root_delay: 0,
            poll: 6,
            root_dispersion: 0.0001678466796875,
            ntp_last_sync_time: [3958798908, 2094313472],
            leap: 0,
            jitter: null,
            nr_measurements_jitter: 0,
            time: 1749810119000
        },
        {
            ntp_version: 4,
            vantage_point_ip: "145.90.49.147",
            ip: "17.253.14.123",
            server_name: "time.apple.com",
            is_anycast: false,
            country_code: "DE",
            coordinates: [50.1169, 8.6837],
            ntp_server_ref_parent_ip: null,
            ref_id: "GPSs",
            client_sent_time: [3958798919, 4264443904],
            server_recv_time: [3958798913, 1021216768],
            server_sent_time: [3958798913, 1021317120],
            client_recv_time: [3958798920, 35274752],
            offset: -6762.771,
            RTT: 15.296,
            stratum: 1,
            precision: -20,
            root_delay: 0,
            poll: 6,
            root_dispersion: 0.0001983642578125,
            ntp_last_sync_time: [3958798906, 645177344],
            leap: 0,
            jitter: null,
            nr_measurements_jitter: 0,
            time: 1749810119000
        },
        {
            ntp_version: 4,
            vantage_point_ip: "145.90.49.147",
            ip: "17.253.52.125",
            server_name: "time.apple.com",
            is_anycast: false,
            country_code: "NL",
            coordinates: [52.3824, 4.8995],
            ntp_server_ref_parent_ip: null,
            ref_id: "GPSs",
            client_sent_time: [3958798920, 70766592],
            server_recv_time: [3958798913, 1108938752],
            server_sent_time: [3958798913, 1109004288],
            client_recv_time: [3958798920, 103895040],
            offset: -6762.131,
            RTT: 7.698,
            stratum: 1,
            precision: -20,
            root_delay: 0,
            poll: 6,
            root_dispersion: 0.000213623046875,
            ntp_last_sync_time: [3958798904, 3654199296],
            leap: 0,
            jitter: null,
            nr_measurements_jitter: 0,
            time: 1749810120000
        },
        {
            ntp_version: 4,
            vantage_point_ip: "145.90.49.147",
            ip: "17.253.14.251",
            server_name: "time.apple.com",
            is_anycast: false,
            country_code: "DE",
            coordinates: [50.1169, 8.6837],
            ntp_server_ref_parent_ip: null,
            ref_id: "GPSs",
            client_sent_time: [3958798920, 134465536],
            server_recv_time: [3958798913, 1186314240],
            server_sent_time: [3958798913, 1186375680],
            client_recv_time: [3958798920, 194453504],
            offset: -6762.074,
            RTT: 13.953,
            stratum: 1,
            precision: -21,
            root_delay: 0,
            poll: 6,
            root_dispersion: 0.0001678466796875,
            ntp_last_sync_time: [3958798907, 2075832320],
            leap: 0,
            jitter: null,
            nr_measurements_jitter: 0,
            time: 1749810120000
        }
        ]

        expect(result.current.error).toBeNull()
        expect(result.current.data).toEqual(expected)
    })
    it('handles historical measurement error correctly', async () => {
        const { result } = renderHook(() => useFetchHistoricalIPData())

        await act(async () => {
            await result.current.fetchData('/measurements/history/?server=time.apple.com&start=2025-06-18T10:24:00Z&end=2025-06-10T10:24:00Z')
        })

        await waitFor(() => {
            expect(result.current.loading).toBe(false)
        })
        
        expect(result.current.data).toBe(null)
        expect(result.current.error).not.toBeNull()
        expect(result.current.error?.message).toBe("Request failed with status code 400")
    })
    it('handles response with missing measurement field', async () => {
        vi.spyOn(axios, 'get').mockResolvedValueOnce({
            data: {},
            status: 200
        })

        const { result } = renderHook(() => useFetchHistoricalIPData())

        await act(async () => {
            await result.current.fetchData('/measurements/history/?server=time.apple.com&start=2025-06-10T10:24:00Z&end=2025-06-18T10:24:00Z')
        })

        await waitFor(() => {
            expect(result.current.loading).toBe(false)
        })

        expect(result.current.data).toEqual([])
        expect(result.current.error).toBeNull()
    })
})
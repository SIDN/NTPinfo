import { renderHook, act } from '@testing-library/react'
import { useTriggerRipeMeasurement } from '../../hooks/useTriggerRipeMeasurement'
import { waitFor } from '@testing-library/react'
import { vi } from 'vitest'
import { RIPEResp } from '../../utils/types'
import axios from 'axios'

describe('useTriggerRipeMeasurement', () => {
    it('triggers ripe measurement correctly', async () => {
        const { result } = renderHook(() => useTriggerRipeMeasurement())

        await act(async () => {
            await result.current.triggerMeasurement({ server: 'time.apple.com', ipv6_measurement: false })
        })

        await waitFor(() => {
            expect(result.current.loading).toBe(false)
        })

        const expected: RIPEResp = {
            measurementId: "110405699",
            vantage_point_ip: "145.94.203.168",
            coordinates: [52.0038,4.3733]
        }

        expect(result.current.error).toBeNull()
        expect(result.current.data).toEqual(expected)
    })
    it('handles ripe trigger error correctly', async () => {
        const { result } = renderHook(() => useTriggerRipeMeasurement())

        await act(async () => {
            await result.current.triggerMeasurement({ server: 'error.server', ipv6_measurement: false })
        })

        await waitFor(() => {
            expect(result.current.loading).toBe(false)
        })
        
        expect(result.current.data).toBe(null)
        expect(result.current.error).not.toBeNull()
        expect(result.current.error?.message).toBe("Request failed with status code 400")
    })
    it('handles response with missing measurement field', async () => {
        vi.spyOn(axios, 'post').mockResolvedValueOnce({
            data: {},
            status: 200
        })

        const { result } = renderHook(() => useTriggerRipeMeasurement())

        await act(async () => {
            await result.current.triggerMeasurement({ server: 'time.apple.com', ipv6_measurement: false })
        })

        await waitFor(() => {
            expect(result.current.loading).toBe(false)
        })

        const expected: RIPEResp = {
            measurementId: null,
            vantage_point_ip: null,
            coordinates: null
        }

        expect(result.current.data).toEqual(expected)
        expect(result.current.error).toBeNull()
    })
})